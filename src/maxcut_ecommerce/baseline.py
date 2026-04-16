from __future__ import annotations

from itertools import product as cartesian_product

from .instance import EcommerceInstance


def _cut_weight(instance: EcommerceInstance, side_a: set[str]) -> float:
    weight = 0.0
    for relation in instance.relations:
        a_in = relation.product_a in side_a
        b_in = relation.product_b in side_a
        if a_in != b_in:
            weight += relation.weight
    return weight


def brute_force_max_cut(instance: EcommerceInstance) -> tuple[float, set[str], set[str]]:
    """Resolve Max-Cut exatamente por força bruta (complexidade O(2^n))."""
    products = instance.products
    root = products[0]

    best_weight = float("-inf")
    best_side_a: set[str] = {root}

    for choice in cartesian_product((False, True), repeat=len(products) - 1):
        side_a = {root}
        for prod_name, goes_to_a in zip(products[1:], choice):
            if goes_to_a:
                side_a.add(prod_name)

        current = _cut_weight(instance, side_a)
        if current > best_weight:
            best_weight = current
            best_side_a = side_a

    side_b = set(products) - best_side_a
    return best_weight, best_side_a, side_b
