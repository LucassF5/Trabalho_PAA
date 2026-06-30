"""Algoritmos para o problema Max-Cut.

Contém:
  - compute_cut_weight : verificador polinomial — O(|E|).
  - verify_cut         : versão de decisão (corte ≥ k?).
  - brute_force_max_cut: solução exata por força bruta — O(2^n · |E|).
"""

from __future__ import annotations

from itertools import product as cartesian_product

from .instance import EcommerceInstance


# ---------------------------------------------------------------------------
# Verificador polinomial  (prova de que Max-Cut ∈ NP)
# ---------------------------------------------------------------------------

def compute_cut_weight(instance: EcommerceInstance, side_a: set[str]) -> float:
    """Soma os pesos das arestas que cruzam o corte (S, V\\S).

    Complexidade: O(|E|) — percorre cada aresta uma única vez.
    """
    return sum(
        rel.weight
        for rel in instance.relations
        if (rel.product_a in side_a) != (rel.product_b in side_a)
    )


def verify_cut(
    instance: EcommerceInstance,
    side_a: set[str],
    threshold: float,
) -> tuple[bool, float]:
    """Verificador polinomial para a versão de decisão do Max-Cut.

    Dado um certificado (partição *side_a*) e um limiar *k*, retorna
    ``(True, peso)`` se o peso do corte ≥ k.

    Complexidade: O(|E|) — confirma a resposta em tempo polinomial,
    demonstrando que Max-Cut ∈ NP.
    """
    weight = compute_cut_weight(instance, side_a)
    return weight >= threshold, weight


# ---------------------------------------------------------------------------
# Solução exata — força bruta
# ---------------------------------------------------------------------------

def brute_force_max_cut(
    instance: EcommerceInstance,
) -> tuple[float, set[str], set[str], int]:
    """Enumera todas as 2^(n−1) partições e retorna o corte de peso máximo.

    Retorna: (peso_máximo, partição_A, partição_B, total_iterações).
    Complexidade: O(2^n · |E|) — exponencial.
    """
    products = instance.products
    # Fixa o primeiro produto no lado A para evitar partições simétricas.
    root = products[0]

    best_weight = float("-inf")
    best_side_a: set[str] = {root}
    iterations = 0

    for bits in cartesian_product((False, True), repeat=len(products) - 1):
        side_a = {root}
        for name, in_a in zip(products[1:], bits):
            if in_a:
                side_a.add(name)

        weight = compute_cut_weight(instance, side_a)
        iterations += 1

        if weight > best_weight:
            best_weight = weight
            best_side_a = side_a

    side_b = set(products) - best_side_a
    return best_weight, best_side_a, side_b, iterations
