from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class Relation:
    product_a: str
    product_b: str
    weight: float
    rationale: str


@dataclass(frozen=True)
class EcommerceInstance:
    products: tuple[str, ...]
    relations: tuple[Relation, ...]


def load_instance(path: str | Path) -> EcommerceInstance:
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    products = tuple(data.get("products", []))
    if len(products) < 2:
        raise ValueError("A instância precisa de pelo menos dois produtos.")

    known_products = set(products)
    relations: list[Relation] = []
    for item in data.get("relations", []):
        relation = Relation(
            product_a=item["product_a"],
            product_b=item["product_b"],
            weight=float(item["weight"]),
            rationale=item.get("rationale", ""),
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
