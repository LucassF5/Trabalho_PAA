from __future__ import annotations

from itertools import product as cartesian_product

from .instance import EcommerceInstance


def compute_cut_weight(instance: EcommerceInstance, side_a: set[str]) -> float:
    """Calcula o peso total das arestas que cruzam o corte (S, V\\S).

    Este é o **verificador polinomial** que demonstra Max-Cut ∈ NP:
    dado um certificado (partição ``side_a``), percorre todas as arestas
    em O(|E|) e soma os pesos daquelas que conectam vértices em lados
    opostos.
    """
    weight = 0.0
    for relation in instance.relations:
        a_in = relation.product_a in side_a
        b_in = relation.product_b in side_a
        if a_in != b_in:
            weight += relation.weight
    return weight


def verify_cut(
    instance: EcommerceInstance,
    side_a: set[str],
    threshold: float,
) -> tuple[bool, float]:
    """Verificador polinomial para a versão de decisão do Max-Cut.

    Dados:
      - Uma instância (grafo ponderado de produtos).
      - Um certificado (partição ``side_a``).
      - Um limiar ``threshold`` (k).

    Retorna ``(True, peso)`` se o peso do corte ≥ k, provando que
    o certificado é válido em tempo O(|E|).  Isso demonstra que
    Max-Cut ∈ NP.
    """
    cut_weight = compute_cut_weight(instance, side_a)
    return cut_weight >= threshold, cut_weight


def brute_force_max_cut(
    instance: EcommerceInstance,
) -> tuple[float, set[str], set[str], int]:
    """Resolve Max-Cut por força bruta, enumerando 2^(n-1) partições.

    Complexidade: O(2^n · |E|) — exponencial, consistente com a
    NP-completude do problema.
    """
    products = instance.products
    root = products[0]

    best_weight = float("-inf")
    best_side_a: set[str] = {root}
    iterations = 0

    for choice in cartesian_product((False, True), repeat=len(products) - 1):
        side_a = {root}
        for product_name, goes_to_a in zip(products[1:], choice):
            if goes_to_a:
                side_a.add(product_name)

        current_weight = compute_cut_weight(instance, side_a)
        iterations += 1
        if current_weight > best_weight:
            best_weight = current_weight
            best_side_a = side_a

    side_b = set(products) - best_side_a
    return best_weight, best_side_a, side_b, iterations
