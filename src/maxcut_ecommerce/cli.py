from __future__ import annotations

import argparse
import time
from pathlib import Path

from .baseline import brute_force_max_cut, verify_cut
from .instance import load_instance


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Avalia uma instância de Max-Cut para relações de produtos de ecommerce."
    )
    parser.add_argument(
        "--instance",
        type=Path,
        default=Path("data/small_instance.json"),
        help="Caminho para o arquivo JSON da instância.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    instance = load_instance(args.instance)
    num_products = len(instance.products)
    num_relations = len(instance.relations)
    total_partitions = 2 ** (num_products - 1)

    print(f"Instância: {args.instance}")
    print(f"Produtos (|V|): {num_products} | Relações (|E|): {num_relations}")
    print(f"Partições a avaliar: 2^({num_products}-1) = {total_partitions:,}")
    print()

    start = time.perf_counter()
    best_weight, side_a, side_b, iterations = brute_force_max_cut(instance)
    elapsed = time.perf_counter() - start

    print(f"Peso máximo do corte: {best_weight:.2f}")
    print(f"Partição A: {sorted(side_a)}")
    print(f"Partição B: {sorted(side_b)}")
    print(f"Iterações (força bruta): {iterations}")
    print(f"Tempo de execução: {elapsed:.4f}s")
    if iterations > 0:
        print(f"Tempo por iteração: {elapsed / iterations * 1000:.4f}ms")
    print()

    # --- Verificação polinomial (prova de que Max-Cut ∈ NP) ---
    threshold = best_weight
    start_verify = time.perf_counter()
    is_valid, verified_weight = verify_cut(instance, side_a, threshold)
    verify_elapsed = time.perf_counter() - start_verify

    print("--- Verificação polinomial (Max-Cut ∈ NP) ---")
    print(f"Limiar k = {threshold:.2f}")
    print(f"Peso verificado: {verified_weight:.2f}")
    print(f"Corte ≥ k? {'SIM ✓' if is_valid else 'NÃO ✗'}")
    print(f"Tempo de verificação: {verify_elapsed:.6f}s  (O(|E|) = O({num_relations}))")
    print(f"Speedup verificação vs. busca: {elapsed / verify_elapsed if verify_elapsed > 0 else '∞'}x")


if __name__ == "__main__":
    main()
