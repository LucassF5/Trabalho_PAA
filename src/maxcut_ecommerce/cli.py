"""CLI — Resolve e verifica uma instância de Max-Cut."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from .baseline import brute_force_max_cut, verify_cut
from .instance import load_instance


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve uma instância de Max-Cut para relações de produtos.",
    )
    parser.add_argument(
        "--instance",
        type=Path,
        default=Path("data/small_instance.json"),
        help="Caminho para o arquivo JSON da instância (padrão: data/small_instance.json).",
    )
    return parser


def _print_section(title: str) -> None:
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")


def main() -> None:
    args = _build_parser().parse_args()
    instance = load_instance(args.instance)

    n = len(instance.products)
    m = len(instance.relations)
    total_partitions = 2 ** (n - 1)

    # ── Informações da instância ──
    _print_section(f"Instância: {args.instance}")
    print(f"  Produtos (|V|):        {n}")
    print(f"  Relações (|E|):        {m}")
    print(f"  Partições a avaliar:   2^({n}−1) = {total_partitions:,}")

    # ── Resolução por força bruta — O(2^n · |E|) ──
    _print_section("Resolução — força bruta")
    t0 = time.perf_counter()
    best_weight, side_a, side_b, iterations = brute_force_max_cut(instance)
    t_brute = time.perf_counter() - t0

    print(f"  Peso máximo do corte:  {best_weight:.2f}")
    print(f"  Partição A ({len(side_a)}):      {sorted(side_a)}")
    print(f"  Partição B ({len(side_b)}):      {sorted(side_b)}")
    print(f"  Iterações:             {iterations:,}")
    print(f"  Tempo total:           {t_brute:.4f}s")
    if iterations > 0:
        print(f"  Tempo por iteração:    {t_brute / iterations * 1_000:.4f}ms")

    # ── Verificação polinomial — O(|E|)  (prova de Max-Cut ∈ NP) ──
    _print_section("Verificação polinomial (Max-Cut ∈ NP)")
    t0 = time.perf_counter()
    is_valid, verified_weight = verify_cut(instance, side_a, best_weight)
    t_verify = time.perf_counter() - t0

    status = "SIM ✓" if is_valid else "NÃO ✗"
    print(f"  Limiar k:              {best_weight:.2f}")
    print(f"  Peso verificado:       {verified_weight:.2f}")
    print(f"  Corte ≥ k?             {status}")
    print(f"  Tempo de verificação:  {t_verify:.6f}s  (O(|E|) = O({m}))")
    if t_verify > 0:
        print(f"  Speedup vs. busca:     {t_brute / t_verify:,.0f}×")


if __name__ == "__main__":
    main()
