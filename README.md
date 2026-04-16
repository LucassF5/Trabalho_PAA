# Trabalho PAA — Algoritmo de Corte Máximo

## Descrição

Este repositório implementa o problema de **Corte Máximo (Max-Cut)** aplicado ao contexto de ecommerce: produtos são vértices e relações de compra conjunta são arestas com peso.

## Objetivo

- Modelar uma base de dados descritiva de produtos e suas relações.
- Permitir entrada de instâncias do problema via arquivo.
- Resolver a instância com uma **baseline exata por força bruta** (ótima para instâncias pequenas).

## Estrutura do repositório

- `src/maxcut_ecommerce/instance.py` — estrutura de dados e carregamento da instância.
- `src/maxcut_ecommerce/baseline.py` — algoritmo baseline de força bruta para Max-Cut.
- `src/maxcut_ecommerce/cli.py` — interface de linha de comando para avaliar instâncias.
- `data/ecommerce_instance.json` — base de dados exemplo com produtos, relações e pesos.
- `tests/test_baseline.py` — testes unitários focados na baseline e validação de instância.

## Formato da instância (JSON)

```json
{
  "description": "texto descritivo",
  "weight_note": "como o peso é mensurado",
  "products": ["Produto A", "Produto B"],
  "relations": [
    {
      "product_a": "Produto A",
      "product_b": "Produto B",
      "weight": 3.5,
      "rationale": "motivo/descrição da relação"
    }
  ]
}
```

## Execução

```bash
python -m src.maxcut_ecommerce.cli --instance data/ecommerce_instance.json
```

Saída esperada: peso máximo do corte e as duas partições de produtos encontradas.
