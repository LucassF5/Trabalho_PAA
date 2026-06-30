from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class Relation:
    product_a: str
    product_b: str
    weight: float


@dataclass(frozen=True)
class EcommerceInstance:
    products: tuple[str, ...]
    relations: tuple[Relation, ...]


def compute_relation_weight(
    co_purchases: int,
    total_purchases_a: int,
    total_purchases_b: int,
) -> float:
    """Calcula o peso da aresta entre dois produtos usando o índice de Jaccard.

    Regra de ponderação:
        peso(A, B) = co_purchases(A, B) / (purchases(A) + purchases(B) - co_purchases(A, B))

    O resultado é normalizado para a escala [0, 10]:
        peso_final = jaccard × 10

    Onde:
      - ``co_purchases``:       nº de vezes que A e B foram comprados juntos.
      - ``total_purchases_a``:  nº total de compras do produto A.
      - ``total_purchases_b``:  nº total de compras do produto B.

    Quanto maior a proporção de compras conjuntas em relação ao total,
    maior o peso — refletindo a força da relação entre os produtos.
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


def load_instance(path: str | Path) -> EcommerceInstance:
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    products = tuple(data.get("products", []))
    if len(products) < 2:
        raise ValueError("A instância precisa ter dois ou mais produtos.")

    known_products = set(products)
    relations: list[Relation] = []
    for item in data.get("relations", []):
        relation = Relation(
            product_a=item["product_a"],
            product_b=item["product_b"],
            weight=float(item["weight"]),
        )

        if relation.product_a not in known_products or relation.product_b not in known_products:
            raise ValueError("Relação contém produto inexistente na lista de produtos.")
        if relation.product_a == relation.product_b:
            raise ValueError("Relações devem conectar produtos diferentes.")
        if relation.weight < 0:
            raise ValueError("Peso não pode ser negativo.")

        relations.append(relation)

    if not relations:
        raise ValueError("A instância precisa de pelo menos uma relação com peso.")

    return EcommerceInstance(products=products, relations=tuple(relations))
