from __future__ import annotations

import argparse
import json
import sys
import time

sys.path.insert(0, ".")

from src.maxcut_ecommerce.baseline import brute_force_max_cut
from src.maxcut_ecommerce.heuristic import local_search_max_cut
from src.maxcut_ecommerce.instance import load_instance


instances = {
    "small": "data/small_instance.json",
    "medium": "data/medium_instance.json",
    "large": "data/large_instance.json",
    "xlarge": "data/xlarge_instance.json",
    "xxlarge": "data/xxlarge_instance.json",
    "huge": "data/huge_instance.json",
    "massive": "data/massive_instance.json",
}


def _print_header(heuristic_only: bool) -> None:
    mode = "apenas heuristica" if heuristic_only else "heuristica + forca bruta quando viavel"
    print("Experimentos Max-Cut para e-commerce")
    print("=" * 44)
    print(f"Modo: {mode}")
    print("Heuristica: busca local com 30 reinicios aleatorios (seed=42)")
    print("Saida JSON: experiment_results.json")


def _print_instance_header(name: str, path: str, n: int, m: int) -> None:
    total_partitions = 2 ** (n - 1)
    print(f"\n{name.upper()} - {path}")
    print("-" * 44)
    print(f"Produtos (|V|):          {n}")
    print(f"Relacoes (|E|):          {m}")
    print(f"Particoes por forca bruta: 2^{n - 1} = {total_partitions:,}")


def _print_heuristic_result(weight: float, elapsed: float) -> None:
    print("\nHeuristica")
    print(f"  Peso do corte encontrado: {weight:.2f}")
    print(f"  Tempo de execucao:        {elapsed:.4f}s")


def _print_baseline_result(weight: float, elapsed: float, iterations: int, quality_ratio: float | None) -> None:
    print("\nForca bruta")
    print(f"  Peso otimo encontrado:    {weight:.2f}")
    print(f"  Tempo de execucao:        {elapsed:.4f}s")
    print(f"  Particoes avaliadas:      {iterations:,}")
    if quality_ratio is not None:
        print(f"  Qualidade da heuristica:  {quality_ratio * 100:.2f}% do otimo")


def _print_baseline_skipped(reason: str, theoretical_iterations: int) -> None:
    print("\nForca bruta")
    print(f"  Status:                  pulada")
    print(f"  Motivo:                  {reason}")
    print(f"  Particoes teoricas:      {theoretical_iterations:,}")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Executa experimentos de Max-Cut com heuristica e, opcionalmente, forca bruta.",
    )
    parser.add_argument(
        "--heuristic-only",
        "--heuristice-only",
        "--skip-baseline",
        action="store_true",
        help="Executa apenas a heuristica, sem rodar a forca bruta.",
    )
    return parser


def main() -> None:
    args = _build_parser().parse_args()

    _print_header(args.heuristic_only)

    results = {}
    for name, path in instances.items():
        inst = load_instance(path)
        n, m = len(inst.products), len(inst.relations)
        theoretical_iterations = 2 ** (n - 1)
        _print_instance_header(name, path, n, m)

        entry = {
            "n": n,
            "m": m,
            "density": m / (n * (n - 1) / 2) if n > 1 else 0,
        }

        # Heuristic (always run)
        h = local_search_max_cut(inst, restarts=30, seed=42)
        entry["heuristic_weight"] = h.weight
        entry["heuristic_time"] = h.time_seconds
        entry["heuristic_moves"] = h.total_moves
        entry["heuristic_restarts"] = h.restarts
        _print_heuristic_result(h.weight, h.time_seconds)

        # Baseline (skip by flag or if too large)
        if args.heuristic_only:
            entry["baseline_weight"] = None
            entry["baseline_time"] = None
            entry["baseline_iterations"] = theoretical_iterations
            entry["quality_ratio"] = None
            _print_baseline_skipped("flag --heuristic-only ativada", theoretical_iterations)
        elif n <= 25:
            t0 = time.perf_counter()
            bw, sa, sb, iters = brute_force_max_cut(inst)
            t1 = time.perf_counter() - t0
            entry["baseline_weight"] = bw
            entry["baseline_time"] = t1
            entry["baseline_iterations"] = iters
            entry["quality_ratio"] = h.weight / bw if bw else None
            _print_baseline_result(bw, t1, iters, entry["quality_ratio"])
        else:
            entry["baseline_weight"] = None
            entry["baseline_time"] = None
            entry["baseline_iterations"] = theoretical_iterations
            entry["quality_ratio"] = None
            _print_baseline_skipped("numero de particoes torna a enumeracao inviavel", theoretical_iterations)

        results[name] = entry

    with open("experiment_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("\nResultados salvos em experiment_results.json")


if __name__ == "__main__":
    main()
