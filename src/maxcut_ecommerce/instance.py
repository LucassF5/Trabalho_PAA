"""Modelagem da instância do problema Max-Cut para e-commerce.

Um grafo ponderado onde:
  - Vértices = produtos.
  - Arestas  = relações de compra conjunta, com peso ∈ [0, 10].
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


# ---------------------------------------------------------------------------
# Estruturas de dados
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Relation:
    """Aresta ponderada entre dois produtos."""
    product_a: str
    product_b: str
    weight: float


@dataclass(frozen=True)
class EcommerceInstance:
    """Instância completa do problema: vértices (produtos) e arestas (relações)."""
    products: tuple[str, ...]
    relations: tuple[Relation, ...]


# ---------------------------------------------------------------------------
# Regra de ponderação — Índice de Jaccard
# ---------------------------------------------------------------------------

def compute_relation_weight(
    co_purchases: int,
    total_purchases_a: int,
    total_purchases_b: int,
) -> float:
    """Calcula o peso de uma aresta pelo índice de Jaccard normalizado.

    Fórmula:
        J(A,B) = compras_conjuntas / (compras_A + compras_B - compras_conjuntas)
        peso   = J(A,B) × 10          (escala final: 0.0 a 10.0)

    Exemplo:
        >>> compute_relation_weight(co_purchases=30, total_purchases_a=100, total_purchases_b=80)
        2.0   # 30/(100+80-30) = 0.2 → 0.2×10 = 2.0
    """
    if co_purchases < 0 or total_purchases_a <= 0 or total_purchases_b <= 0:
        raise ValueError("Valores de compras devem ser positivos.")
    if co_purchases > min(total_purchases_a, total_purchases_b):
        raise ValueError(
            "Compras conjuntas não podem exceder o total de compras de nenhum produto."
        )

    union = total_purchases_a + total_purchases_b - co_purchases
    jaccard = co_purchases / union
    return round(jaccard * 10, 1)


# ---------------------------------------------------------------------------
# Carregamento de instância a partir de JSON
# ---------------------------------------------------------------------------

def load_instance(path: str | Path) -> EcommerceInstance:
    """Lê um arquivo JSON e devolve uma ``EcommerceInstance`` validada."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    products = tuple(data.get("products", []))
    if len(products) < 2:
        raise ValueError("A instância precisa ter dois ou mais produtos.")

    known_products = set(products)
    relations: list[Relation] = []

    for item in data.get("relations", []):
        rel = Relation(
            product_a=item["product_a"],
            product_b=item["product_b"],
            weight=float(item["weight"]),
        )
        if rel.product_a not in known_products or rel.product_b not in known_products:
            raise ValueError(f"Produto desconhecido na relação: {rel.product_a!r} — {rel.product_b!r}")
        if rel.product_a == rel.product_b:
            raise ValueError(f"Laço não permitido: {rel.product_a!r}")
        if rel.weight < 0:
            raise ValueError(f"Peso negativo ({rel.weight}) na relação {rel.product_a!r} — {rel.product_b!r}")
        relations.append(rel)

    if not relations:
        raise ValueError("A instância precisa de pelo menos uma relação com peso.")

    return EcommerceInstance(products=products, relations=tuple(relations))
