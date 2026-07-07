"""Heuristica para o problema Max-Cut.

Implementa uma busca local (local search) com reinicios aleatorios
(random restarts), tambem conhecida como abordagem "flip" de vizinhanca-1:

  1. Gera uma particao inicial aleatoria.
  2. Enquanto existir um produto cuja mudanca de lado aumente o peso do
     corte, move esse produto (melhoria estritamente positiva).
  3. Repete a partir de varias particoes iniciais diferentes e devolve a
     melhor solucao encontrada entre todos os reinicios.

Complexidade de uma unica busca local: no pior caso, cada rodada de
varredura custa O(|V| * |E|) (para cada vertice, recalcular a variacao de
peso ao troca-lo de lado custa O(deg(v)), e a soma dos graus e O(|E|)).
O numero de rodadas ate convergir e, na pratica, pequeno (poucas dezenas),
portanto o custo e muito inferior a enumeracao completa O(2^n * |E|) do
forca bruta.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .baseline import compute_cut_weight
from .instance import EcommerceInstance


@dataclass
class HeuristicResult:
    weight: float
    side_a: set[str]
    side_b: set[str]
    restarts: int
    total_moves: int
    time_seconds: float


def _delta_if_flipped(instance: EcommerceInstance, product: str, side_a: set[str]) -> float:
    """Calcula a variacao no peso do corte se `product` mudar de lado.

    So percorre as relacoes que envolvem `product` - O(deg(product)).
    """
    delta = 0.0
    in_a = product in side_a
    for rel in instance.relations:
        if rel.product_a == product:
            other = rel.product_b
        elif rel.product_b == product:
            other = rel.product_a
        else:
            continue

        other_in_a = other in side_a
        currently_crosses = in_a != other_in_a
        # Se cruza hoje, ao trocar de lado deixa de cruzar (perde peso);
        # se nao cruza hoje, ao trocar de lado passa a cruzar (ganha peso).
        delta += -rel.weight if currently_crosses else rel.weight
    return delta


def _local_search(
    instance: EcommerceInstance,
    side_a: set[str],
    rng: random.Random,
) -> tuple[set[str], int]:
    """Busca local de vizinhanca-1: troca produtos de lado enquanto melhora o corte."""
    products = list(instance.products)
    moves = 0
    improved = True

    while improved:
        improved = False
        rng.shuffle(products)
        for product in products:
            delta = _delta_if_flipped(instance, product, side_a)
            if delta > 1e-9:
                if product in side_a:
                    side_a.remove(product)
                else:
                    side_a.add(product)
                moves += 1
                improved = True

    return side_a, moves


def local_search_max_cut(
    instance: EcommerceInstance,
    restarts: int = 20,
    seed: int | None = 42,
) -> HeuristicResult:
    """Executa busca local com multiplos reinicios aleatorios.

    Retorna a melhor particao encontrada entre todos os reinicios.
    Complexidade aproximada: O(restarts * rodadas * |E|), com "rodadas"
    tipicamente pequeno (converge rapido), portanto muito mais barato que
    o forca bruta O(2^n * |E|) para instancias grandes.
    """
    rng = random.Random(seed)
    products = list(instance.products)

    best_weight = float("-inf")
    best_side_a: set[str] = set()
    total_moves = 0

    t0 = time.perf_counter()
    for _ in range(restarts):
        side_a = {p for p in products if rng.random() < 0.5}
        side_a, moves = _local_search(instance, side_a, rng)
        total_moves += moves

        weight = compute_cut_weight(instance, side_a)
        if weight > best_weight:
            best_weight = weight
            best_side_a = set(side_a)
    elapsed = time.perf_counter() - t0

    side_b = set(products) - best_side_a
    return HeuristicResult(
        weight=best_weight,
        side_a=best_side_a,
        side_b=side_b,
        restarts=restarts,
        total_moves=total_moves,
        time_seconds=elapsed,
    )
