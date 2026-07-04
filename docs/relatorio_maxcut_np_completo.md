# Relatório: Corte Máximo (Max-Cut) aplicado a e-commerce

## 1. Descrição do problema

O problema estudado neste trabalho é o **Corte Máximo**, conhecido na literatura como **Max-Cut**. Seja um grafo não direcionado e ponderado \(G = (V, E, w)\), em que \(V\) é o conjunto de vértices, \(E\) é o conjunto de arestas e \(w(e)\) é o peso associado a cada aresta \(e \in E\). O objetivo é dividir os vértices em dois subconjuntos disjuntos, \(S\) e \(V \setminus S\), de modo que a soma dos pesos das arestas que atravessam a divisão seja máxima.

Uma aresta atravessa o corte quando seus dois extremos ficam em lados diferentes da partição. Assim, o valor de um corte é definido por:

\[
W(S) = \sum_{(u,v) \in E,\ u \in S,\ v \notin S} w(u,v)
\]

No contexto deste projeto, os vértices representam **produtos de um e-commerce**, e as arestas representam relações de **compra conjunta** entre pares de produtos. O peso de cada aresta indica a força dessa relação: quanto maior o peso, mais forte é a associação entre os dois produtos. Dessa forma, encontrar um corte máximo significa separar os produtos em dois grupos maximizando a soma das relações que passam de um grupo para o outro.

Essa modelagem pode apoiar decisões práticas, como organização de catálogo, estratégias de recomendação, campanhas de venda cruzada e análise de produtos frequentemente relacionados. Por exemplo, se "Smartphone" e "Carregador Rápido" possuem uma aresta de peso alto, separá-los em grupos diferentes contribui bastante para o valor do corte, indicando uma relação relevante entre categorias ou conjuntos distintos de produtos.

## 2. Modelagem usada no projeto

A aplicação implementada representa uma instância do problema por meio de um arquivo JSON contendo:

- uma lista de produtos;
- uma lista de relações entre pares de produtos;
- um peso numérico para cada relação.

Formalmente, cada produto é um vértice do grafo, cada relação de compra conjunta é uma aresta, e cada peso é um valor real não negativo. O projeto também define uma regra de ponderação baseada no **índice de Jaccard**, usada para medir a força de associação entre dois produtos:

\[
\text{peso}(A,B) =
\frac{\text{compras conjuntas}(A,B)}
{\text{compras}(A) + \text{compras}(B) - \text{compras conjuntas}(A,B)}
\times 10
\]

O fator \(10\) normaliza o peso para a escala de \(0\) a \(10\). Assim, produtos que aparecem juntos em muitas compras tendem a receber pesos maiores, enquanto produtos com pouca relação de compra recebem pesos menores.

## 3. Descrição da implementação

A implementação está organizada no pacote `src/maxcut_ecommerce`. Os principais arquivos são:

- `instance.py`: define as estruturas de dados da instância e a função de carregamento do JSON;
- `baseline.py`: implementa o cálculo do peso de um corte, o verificador polinomial e o algoritmo exato por força bruta;
- `cli.py`: fornece uma interface de linha de comando para executar o algoritmo sobre uma instância.

### 3.1 Estruturas de dados

O arquivo `instance.py` define duas estruturas principais:

- `Relation`: representa uma aresta ponderada entre dois produtos;
- `EcommerceInstance`: representa a instância completa, contendo o conjunto de produtos e o conjunto de relações.

A função `load_instance` lê o arquivo JSON, valida a existência de produtos e relações, impede laços, rejeita pesos negativos e verifica se todos os produtos citados nas relações pertencem à lista de produtos da instância.

### 3.2 Cálculo do peso de um corte

O peso de uma partição é calculado pela função `compute_cut_weight`, em `baseline.py`. Ela percorre todas as arestas e soma apenas aquelas cujos extremos estão em lados diferentes da partição:

```python
def compute_cut_weight(instance: EcommerceInstance, side_a: set[str]) -> float:
    return sum(
        rel.weight
        for rel in instance.relations
        if (rel.product_a in side_a) != (rel.product_b in side_a)
    )
```

A condição lógica usa diferença booleana: a aresta é somada somente quando exatamente um dos produtos está no conjunto `side_a`. Como cada aresta é visitada uma única vez, a complexidade dessa etapa é \(O(|E|)\).

### 3.3 Verificador polinomial

A função `verify_cut` implementa a versão de decisão do problema: dada uma partição candidata e um limiar \(k\), ela verifica se o peso do corte é pelo menos \(k\). Esse procedimento é importante para a prova de que o problema pertence à classe NP.

```python
def verify_cut(instance, side_a, threshold):
    weight = compute_cut_weight(instance, side_a)
    return weight >= threshold, weight
```

Como a função apenas calcula o peso do corte e compara com o limiar, sua complexidade também é \(O(|E|)\), isto é, polinomial no tamanho da entrada.

### 3.4 Algoritmo exato por força bruta

Para encontrar a solução ótima, o arquivo `baseline.py` implementa `brute_force_max_cut`. Esse algoritmo enumera todas as partições possíveis dos vértices e calcula o peso de cada uma. Como trocar os lados da partição gera o mesmo corte, o primeiro produto é fixado em um dos lados, reduzindo a enumeração para \(2^{n-1}\) partições.

Mesmo com essa otimização, o algoritmo é exponencial:

\[
O(2^n \cdot |E|)
\]

Isso acontece porque, para cada uma das partições possíveis, o algoritmo percorre as arestas para calcular o peso do corte. Portanto, a implementação é adequada como linha de base exata para instâncias pequenas e médias, mas não escala bem para instâncias grandes.

## 4. Versão de decisão do Max-Cut

Para discutir NP-completude, é necessário considerar a versão de decisão do problema, pois a classe NP é definida para problemas de decisão.

A versão de decisão do Max-Cut é:

**Entrada:** um grafo ponderado \(G = (V, E, w)\) e um número \(k\).

**Pergunta:** existe uma partição \((S, V \setminus S)\) tal que a soma dos pesos das arestas que cruzam o corte seja pelo menos \(k\)?

Se a resposta for "sim", então existe um certificado: basta apresentar o conjunto \(S\). O verificador calcula o peso do corte correspondente e compara com \(k\).

## 5. Prova de que o problema é NP-completo

Para provar que Max-Cut é NP-completo, são necessários dois passos:

1. provar que Max-Cut pertence a NP;
2. provar que Max-Cut é NP-difícil.

### 5.1 Max-Cut pertence a NP

Um problema pertence a NP se, para toda instância cuja resposta é "sim", existe um certificado que pode ser verificado em tempo polinomial.

No Max-Cut, o certificado é uma partição dos vértices, isto é, o conjunto \(S\). Dado esse conjunto, o verificador percorre todas as arestas do grafo e soma os pesos das arestas que possuem um extremo em \(S\) e outro em \(V \setminus S\). Em seguida, compara essa soma com o limiar \(k\).

O procedimento percorre cada aresta uma única vez, logo sua complexidade é:

\[
O(|E|)
\]

Como \(O(|E|)\) é polinomial no tamanho da entrada, a verificação é polinomial. Portanto:

\[
\text{Max-Cut} \in \text{NP}
\]

### 5.2 Max-Cut é NP-difícil

Para provar que Max-Cut é NP-difícil, reduzimos em tempo polinomial um problema conhecido como NP-completo para Max-Cut. Usaremos o problema **NAE-3SAT**.

No NAE-3SAT, recebe-se uma fórmula booleana em 3-CNF, isto é, uma conjunção de cláusulas com três literais cada. A pergunta é se existe uma atribuição de valores verdade tal que, em cada cláusula, os três literais **não sejam todos iguais**. Em outras palavras, cada cláusula precisa ter pelo menos um literal verdadeiro e pelo menos um literal falso.

Sabemos que NAE-3SAT é NP-completo. Mostraremos que:

\[
\text{NAE-3SAT} \leq_p \text{Max-Cut}
\]

Ou seja, qualquer instância de NAE-3SAT pode ser transformada, em tempo polinomial, em uma instância de Max-Cut cuja resposta preserva a resposta da instância original.

### 5.3 Construção da redução

Considere uma fórmula NAE-3SAT com \(n\) variáveis e \(m\) cláusulas.

Construímos um grafo ponderado da seguinte forma:

1. Para cada variável \(x_i\), criamos dois vértices: um para \(x_i\) e outro para \(\neg x_i\).
2. Para cada variável \(x_i\), adicionamos uma aresta de peso \(m\) entre os vértices \(x_i\) e \(\neg x_i\).
3. Para cada cláusula \((l_a, l_b, l_c)\), adicionamos arestas de peso \(1\) formando um triângulo entre os três literais \(l_a\), \(l_b\) e \(l_c\).
4. Definimos o limiar:

\[
k = n \cdot m + 2m
\]

A construção cria \(2n\) vértices e \(n + 3m\) arestas, portanto o tamanho do grafo é polinomial no tamanho da fórmula original.

### 5.4 Correção da redução

Agora mostramos que a fórmula NAE-3SAT é satisfatível se, e somente se, o grafo construído possui um corte de peso pelo menos \(k\).

#### Ida: se a fórmula é satisfatível, então existe corte de peso pelo menos \(k\)

Suponha que exista uma atribuição que satisfaz a fórmula no sentido NAE, isto é, em toda cláusula há pelo menos um literal verdadeiro e pelo menos um literal falso.

Construímos uma partição do grafo colocando os literais verdadeiros de um lado do corte e os literais falsos do outro lado. Como \(x_i\) e \(\neg x_i\) sempre possuem valores opostos, a aresta de peso \(m\) entre eles sempre cruza o corte. Portanto, as arestas de variáveis contribuem:

\[
n \cdot m
\]

Em cada cláusula, os três literais não são todos iguais. Logo, no triângulo correspondente, exatamente duas arestas cruzam o corte. Como cada uma tem peso \(1\), cada cláusula contribui \(2\). Para \(m\) cláusulas, a contribuição total das cláusulas é:

\[
2m
\]

Assim, o peso total do corte é:

\[
n \cdot m + 2m = k
\]

Logo, se a fórmula NAE-3SAT é satisfatível, existe um corte de peso pelo menos \(k\).

#### Volta: se existe corte de peso pelo menos \(k\), então a fórmula é satisfatível

Suponha agora que o grafo construído possua um corte de peso pelo menos \(k = nm + 2m\).

As arestas entre \(x_i\) e \(\neg x_i\) têm peso \(m\). Como existem \(n\) dessas arestas, a maior contribuição possível das arestas de variáveis é \(nm\). Além disso, cada triângulo de cláusula pode contribuir no máximo \(2\), pois em um triângulo não é possível que as três arestas cruzem o mesmo corte. Assim, a maior contribuição possível dos triângulos é \(2m\).

Portanto, para que o corte alcance \(nm + 2m\), é necessário que:

- todas as arestas entre \(x_i\) e \(\neg x_i\) cruzem o corte;
- cada triângulo de cláusula contribua exatamente \(2\).

Se todas as arestas entre \(x_i\) e \(\neg x_i\) cruzam o corte, então cada variável e sua negação estão em lados opostos. Podemos interpretar um lado do corte como verdadeiro e o outro como falso.

Se cada triângulo de cláusula contribui exatamente \(2\), então, em cada cláusula, os três literais não estão todos no mesmo lado do corte. Isso significa que cada cláusula possui pelo menos um literal verdadeiro e pelo menos um literal falso.

Logo, a atribuição obtida a partir do corte satisfaz a fórmula NAE-3SAT.

### 5.5 Conclusão da prova

Mostramos que:

- Max-Cut pertence a NP, pois uma solução candidata pode ser verificada em tempo polinomial;
- Max-Cut é NP-difícil, pois NAE-3SAT, que é NP-completo, reduz-se polinomialmente a Max-Cut.

Portanto:

\[
\boxed{\text{Max-Cut é NP-completo}}
\]

## 6. Relação entre a teoria e a implementação

A implementação reforça diretamente os conceitos usados na prova.

Primeiro, a função `verify_cut` representa o verificador polinomial da versão de decisão. Ela recebe uma partição candidata e verifica em \(O(|E|)\) se o corte atinge o limiar desejado.

Segundo, o algoritmo `brute_force_max_cut` mostra por que resolver o problema por enumeração direta é custoso: o número de partições cresce exponencialmente com a quantidade de produtos. Para \(n\) produtos, a implementação avalia \(2^{n-1}\) partições, já eliminando a simetria entre os dois lados do corte.

Assim, a implementação separa claramente duas ideias centrais da teoria da complexidade:

- **verificar** uma solução candidata é eficiente;
- **encontrar** a melhor solução por força bruta pode exigir tempo exponencial.

Essa diferença é exatamente a intuição por trás da classe NP e ajuda a justificar a importância da prova de NP-completude para o Max-Cut.

## 7. Conclusão

O projeto implementa uma solução exata para o problema Max-Cut aplicado a relações de compra conjunta em e-commerce. A modelagem transforma produtos em vértices, relações de compra conjunta em arestas e forças de associação em pesos. A solução por força bruta encontra o corte ótimo, mas possui complexidade exponencial, sendo adequada principalmente para instâncias de tamanho limitado.

Do ponto de vista teórico, a versão de decisão do Max-Cut é NP-completa. A pertinência a NP decorre da existência de um verificador polinomial para uma partição candidata. A NP-dificuldade decorre da redução polinomial de NAE-3SAT para Max-Cut. Portanto, o problema combina relevância prática, modelagem simples e alta dificuldade computacional no pior caso.
