#!/usr/bin/env python3
"""Resolve a menu choice against the active card in a study flow Markdown file."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


CARD_HEADING = re.compile(r"^##\s+(CARD\s+\d+)\s*$", re.IGNORECASE)
STATE_HEADING = re.compile(r"^##\s+Estado da navegação\s*$", re.IGNORECASE)
OPTION_HEADING = re.compile(r"^###\s+Opções\s*$", re.IGNORECASE)
OPTION_LINE = re.compile(r"^\s*(\d+)\.\s+(.+?)\s*$")
ACTIVE_CARD_LINE = re.compile(
    r"^\s*-\s*CARD\s+atual\s*:\s*(CARD\s+\d+)\s*$", re.IGNORECASE
)


class FlowError(ValueError):
    """A flow file cannot be safely used to resolve this request."""


@dataclass
class Card:
    card_id: str
    options: dict[int, str] = field(default_factory=dict)
    saw_options: bool = False


@dataclass
class Flow:
    cards: dict[str, Card]
    active_card: Optional[str]


def canonical_card_id(value: str) -> str:
    match = re.fullmatch(r"\s*CARD\s+(\d+)\s*", value, re.IGNORECASE)
    if not match:
        raise FlowError(f"ID de card inválido: {value!r}; use o formato 'CARD N'.")
    return f"CARD {int(match.group(1))}"


def parse_flow(path: Path) -> Flow:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise FlowError(f"Não foi possível ler {path}: {exc.strerror or exc}.") from exc
    except UnicodeError as exc:
        raise FlowError(f"O arquivo {path} não está em UTF-8 válido.") from exc

    cards: dict[str, Card] = {}
    active_cards: list[str] = []
    current_card: Optional[Card] = None
    in_state = False
    in_options = False

    for line_number, line in enumerate(lines, start=1):
        card_match = CARD_HEADING.match(line)
        if card_match:
            card_id = canonical_card_id(card_match.group(1))
            if card_id in cards:
                raise FlowError(f"{path}:{line_number}: {card_id} está registrado mais de uma vez.")
            current_card = Card(card_id)
            cards[card_id] = current_card
            in_state = False
            in_options = False
            continue

        if STATE_HEADING.match(line):
            current_card = None
            in_state = True
            in_options = False
            continue

        if line.startswith("## "):
            current_card = None
            in_state = False
            in_options = False
            continue

        if in_state:
            active_match = ACTIVE_CARD_LINE.match(line)
            if active_match:
                active_cards.append(canonical_card_id(active_match.group(1)))
            continue

        if current_card is None:
            continue

        if OPTION_HEADING.match(line):
            if current_card.saw_options:
                raise FlowError(f"{path}:{line_number}: {current_card.card_id} tem mais de uma seção de opções.")
            current_card.saw_options = True
            in_options = True
            continue

        if in_options:
            option_match = OPTION_LINE.match(line)
            if option_match:
                number = int(option_match.group(1))
                if number in current_card.options:
                    raise FlowError(
                        f"{path}:{line_number}: opção {number} aparece mais de uma vez em {current_card.card_id}."
                    )
                current_card.options[number] = option_match.group(2).strip()
            elif line.strip():
                in_options = False

    if not cards:
        raise FlowError(f"{path} não contém registros `## CARD N`.")

    if len(active_cards) > 1:
        raise FlowError(f"{path} registra mais de um CARD atual.")

    active_card = active_cards[0] if active_cards else None
    if active_card and active_card not in cards:
        raise FlowError(f"O CARD atual {active_card} não está registrado em {path}.")

    for card in cards.values():
        if not card.saw_options or not card.options:
            raise FlowError(f"{card.card_id} não tem opções numeradas legíveis em {path}.")
        actual_numbers = sorted(card.options)
        expected_numbers = list(range(1, len(actual_numbers) + 1))
        if actual_numbers != expected_numbers:
            raise FlowError(
                f"{card.card_id} tem numeração de opções não sequencial em {path}: {actual_numbers}."
            )

    return Flow(cards=cards, active_card=active_card)


def normalize_label(value: str) -> str:
    return re.sub(r"[`*_~]", "", value).strip().casefold()


def action_for(option: str) -> str:
    normalized = normalize_label(option)
    if normalized == "mais":
        return "more"
    if normalized == "voltar":
        return "back"
    if normalized == "ir para":
        return "navigate"
    return "open_card"


def resolve_active_card(flow: Flow, override: Optional[str]) -> Card:
    if override:
        card_id = canonical_card_id(override)
        if card_id not in flow.cards:
            raise FlowError(f"{card_id} não está registrado no fluxo.")
        if flow.active_card and flow.active_card != card_id:
            raise FlowError(
                f"O fluxo registra {flow.active_card} como atual, mas foi informado {card_id}. Corrija o estado antes de continuar."
            )
        return flow.cards[card_id]

    if not flow.active_card:
        raise FlowError("O fluxo não registra um CARD atual. Informe --card somente se a conversa identificar o CARD sem ambiguidade.")
    return flow.cards[flow.active_card]


def resolve_choice(flow: Flow, reply: str, card_override: Optional[str] = None) -> dict[str, object]:
    card = resolve_active_card(flow, card_override)
    stripped = reply.strip()

    number_match = re.fullmatch(r"(?:opção\s*)?(\d+)(?:[.)])?", stripped, re.IGNORECASE)
    if number_match:
        number = int(number_match.group(1))
        option = card.options.get(number)
        if option is None:
            available = ", ".join(str(item) for item in sorted(card.options))
            raise FlowError(
                f"A opção {number} não existe em {card.card_id}. Opções registradas: {available}."
            )
    else:
        matches = [
            (number, label)
            for number, label in card.options.items()
            if normalize_label(label) == normalize_label(stripped)
        ]
        if len(matches) != 1:
            raise FlowError(
                f"A resposta {reply!r} não identifica uma opção única de {card.card_id}. Use o número ou o texto exato de uma opção registrada."
            )
        number, option = matches[0]

    result: dict[str, object] = {
        "ok": True,
        "current_card": card.card_id,
        "choice_number": number,
        "option": option,
        "action": action_for(option),
    }
    if result["action"] == "navigate":
        result["destination_required"] = True
    return result


def resolve_destination(flow: Flow, destination: str) -> dict[str, object]:
    card_id = canonical_card_id(destination)
    if card_id not in flow.cards:
        raise FlowError(f"O destino {card_id} não existe no fluxo.")
    result: dict[str, object] = {
        "ok": True,
        "action": "navigate_to",
        "destination": card_id,
    }
    if flow.active_card:
        result["current_card"] = flow.active_card
    return result


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Resolve uma escolha usando as opções registradas no card atual de fluxo.md."
    )
    parser.add_argument("flow_file", type=Path, help="Caminho para o fluxo.md do curso")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--choice", help="Número ou texto exato de uma opção exibida")
    mode.add_argument("--goto", dest="destination", help="Destino direto, como 'CARD 5'")
    parser.add_argument(
        "--card",
        help="CARD ativo para um fluxo legado sem estado gravado; use somente se a conversa o identificar sem ambiguidade",
    )
    args = parser.parse_args(argv)

    try:
        flow = parse_flow(args.flow_file)
        if args.destination:
            if args.card:
                raise FlowError("--card não pode ser combinado com --goto.")
            result = resolve_destination(flow, args.destination)
        else:
            result = resolve_choice(flow, args.choice, args.card)
    except FlowError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
