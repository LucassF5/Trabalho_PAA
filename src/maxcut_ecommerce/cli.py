from __future__ import annotations

import argparse
from pathlib import Path

from .baseline import brute_force_max_cut
from .instance import load_instance


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Avalia uma instância de Max-Cut para relações de produtos de ecommerce."
    )
    parser.add_argument(
        "--instance",
        type=Path,
        default=Path("data/ecommerce_instance.json"),
        help="Caminho para o arquivo JSON da instância.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    instance = load_instance(args.instance)
    best_weight, side_a, side_b = brute_force_max_cut(instance)

    print(f"Instância: {args.instance}")
    print(f"Produtos: {len(instance.products)} | Relações: {len(instance.relations)}")
    print(f"Peso máximo do corte: {best_weight:.2f}")
    print(f"Partição A: {sorted(side_a)}")
    print(f"Partição B: {sorted(side_b)}")


if __name__ == "__main__":
    main()
