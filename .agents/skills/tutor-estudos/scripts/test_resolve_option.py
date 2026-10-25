"""Behavior tests for resolve_option.py using only the Python standard library."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("resolve_option.py")
FLOW = """# FLUXO DE APRENDIZADO

## CARD 1
- Assunto: Introdução
- Pai: INÍCIO
- Opção de origem: ---
- Filhos: CARD 4

### Opções
1. Conceitos
2. MAIS
3. IR PARA

## CARD 4
- Assunto: Armazenamento
- Pai: CARD 1
- Opção de origem: Armazenamento
- Filhos: ---

### Opções
1. Discos
2. Sistemas de arquivos
3. Pontos de montagem
4. MAIS
5. IR PARA
6. VOLTAR

## Estado da navegação
- CARD atual: CARD 4
"""


class ResolveOptionTests(unittest.TestCase):
    def run_cli(self, flow_text: str, *args: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        with tempfile.TemporaryDirectory() as temp_dir:
            flow_path = Path(temp_dir) / "fluxo.md"
            flow_path.write_text(flow_text, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(flow_path), *args],
                capture_output=True,
                text=True,
                check=False,
            )
        return result, json.loads(result.stdout)

    def test_number_maps_to_the_active_card_option(self) -> None:
        result, data = self.run_cli(FLOW, "--choice", "5")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(data["current_card"], "CARD 4")
        self.assertEqual(data["option"], "IR PARA")
        self.assertEqual(data["action"], "navigate")
        self.assertTrue(data["destination_required"])

    def test_more_and_back_use_their_registered_indices(self) -> None:
        more, more_data = self.run_cli(FLOW, "--choice", "4")
        back, back_data = self.run_cli(FLOW, "--choice", "6")
        self.assertEqual(more.returncode, 0)
        self.assertEqual(more_data["action"], "more")
        self.assertEqual(back.returncode, 0)
        self.assertEqual(back_data["action"], "back")

    def test_topic_choice_is_resolved_from_the_same_menu(self) -> None:
        result, data = self.run_cli(FLOW, "--choice", "1")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(data["option"], "Discos")
        self.assertEqual(data["action"], "open_card")

    def test_exact_action_label_is_resolved(self) -> None:
        result, data = self.run_cli(FLOW, "--choice", "IR PARA")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(data["choice_number"], 5)
        self.assertEqual(data["action"], "navigate")

    def test_same_number_has_no_global_meaning_between_cards(self) -> None:
        card_one_active = FLOW.replace("- CARD atual: CARD 4", "- CARD atual: CARD 1")
        valid, valid_data = self.run_cli(card_one_active, "--choice", "2")
        stale, stale_data = self.run_cli(card_one_active, "--choice", "5")
        self.assertEqual(valid.returncode, 0)
        self.assertEqual(valid_data["option"], "MAIS")
        self.assertEqual(stale.returncode, 2)
        self.assertFalse(stale_data["ok"])

    def test_legacy_flow_requires_explicit_active_card(self) -> None:
        legacy = FLOW.replace("\n## Estado da navegação\n- CARD atual: CARD 4\n", "\n")
        missing, missing_data = self.run_cli(legacy, "--choice", "4")
        explicit, explicit_data = self.run_cli(legacy, "--choice", "4", "--card", "CARD 4")
        self.assertEqual(missing.returncode, 2)
        self.assertFalse(missing_data["ok"])
        self.assertEqual(explicit.returncode, 0)
        self.assertEqual(explicit_data["current_card"], "CARD 4")

    def test_inconsistent_active_card_override_is_rejected(self) -> None:
        result, data = self.run_cli(FLOW, "--choice", "1", "--card", "CARD 1")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(data["ok"])

    def test_unregistered_number_is_rejected(self) -> None:
        result, data = self.run_cli(FLOW, "--choice", "7")
        self.assertEqual(result.returncode, 2)
        self.assertIn("não existe em CARD 4", data["error"])

    def test_direct_destination_is_validated(self) -> None:
        valid, valid_data = self.run_cli(FLOW, "--goto", "CARD 1")
        invalid, invalid_data = self.run_cli(FLOW, "--goto", "CARD 99")
        self.assertEqual(valid.returncode, 0)
        self.assertEqual(valid_data["action"], "navigate_to")
        self.assertEqual(valid_data["destination"], "CARD 1")
        self.assertEqual(invalid.returncode, 2)
        self.assertFalse(invalid_data["ok"])

    def test_duplicate_option_number_is_rejected(self) -> None:
        malformed = FLOW.replace("1. Discos", "4. Discos")
        result, data = self.run_cli(malformed, "--choice", "4")
        self.assertEqual(result.returncode, 2)
        self.assertIn("aparece mais de uma vez", data["error"])

    def test_non_sequential_options_are_rejected(self) -> None:
        malformed = FLOW.replace("4. MAIS\n5. IR PARA", "7. MAIS\n5. IR PARA")
        result, data = self.run_cli(malformed, "--choice", "5")
        self.assertEqual(result.returncode, 2)
        self.assertIn("numeração de opções não sequencial", data["error"])


if __name__ == "__main__":
    unittest.main()
