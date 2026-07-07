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
}

results = {}
for name, path in instances.items():
    inst = load_instance(path)
    n, m = len(inst.products), len(inst.relations)
    print(f"=== {name}: n={n}, m={m} ===", flush=True)

    entry = {"n": n, "m": m}

    # Heuristic (always run)
    h = local_search_max_cut(inst, restarts=30, seed=42)
    entry["heuristic_weight"] = h.weight
    entry["heuristic_time"] = h.time_seconds
    print(f"  heuristic: weight={h.weight:.2f} time={h.time_seconds:.4f}s", flush=True)

    # Baseline (skip if too large)
    if n <= 25:
        t0 = time.perf_counter()
        bw, sa, sb, iters = brute_force_max_cut(inst)
        t1 = time.perf_counter() - t0
        entry["baseline_weight"] = bw
        entry["baseline_time"] = t1
        entry["baseline_iterations"] = iters
        entry["quality_ratio"] = h.weight / bw if bw else None
        print(f"  baseline:  weight={bw:.2f} time={t1:.4f}s iters={iters}", flush=True)
    else:
        entry["baseline_weight"] = None
        entry["baseline_time"] = None
        entry["baseline_iterations"] = 2 ** (n - 1)
        entry["quality_ratio"] = None
        print(f"  baseline:  SKIPPED (2^{n - 1} = {2 ** (n - 1):,} particoes -> inviavel)", flush=True)

    results[name] = entry

with open("experiment_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print("\nDONE")
