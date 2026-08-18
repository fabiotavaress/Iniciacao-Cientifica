# 🔬 Iniciação Científica — Visualização de Soluções em Otimização Multiobjetivo

Projeto de **Iniciação Científica** desenvolvido no Bacharelado em Ciência da Computação da **Universidade Federal de Ouro Preto (UFOP)**, com foco na **visualização de soluções de problemas de otimização multiobjetivo** de alta dimensionalidade.

O objetivo é representar, de forma clara e interpretável, conjuntos de soluções (fronteiras de Pareto) com **muitos objetivos** — algo difícil de visualizar em gráficos tradicionais 2D/3D. Para isso, o projeto explora **diagramas de corda (chord diagrams)**, **mapeamento angular** e **coordenadas paralelas**, revelando relações e padrões entre as dimensões do problema.

**Fábio Tavares Pinto** — [LinkedIn](https://www.linkedin.com/in/f%C3%A1bio-tavares-662439302/) · [GitHub](https://github.com/fabiotavaress)

---

## 🎯 Abordagem

- **Mapeamento angular:** para cada solução, calcula-se a norma (ρ), o menor ângulo em relação aos eixos e a associação ao eixo dominante — reduzindo a alta dimensionalidade a coordenadas interpretáveis.
- **Diagramas de corda:** cada dimensão/objetivo vira um setor no círculo; as soluções são desenhadas como conexões entre os setores, expondo trade-offs e agrupamentos.
- **Coordenadas paralelas** como visualização complementar.

Os experimentos usam instâncias clássicas de otimização multiobjetivo, como o benchmark **WFG4** e dados de decisão de algoritmos evolutivos (ex.: **NSGA-II**, **DWU**), além do conjunto **Iris** para validação.

## 🗂️ Estrutura

| Arquivo | Descrição |
|---|---|
| `grafico_otimizado.py` | Versão principal (otimizada) em Python: gera o diagrama de corda com classificação angular das soluções. |
| `chord_diagram_final.py` · `chord_diagram_color2.py` | Geração dos diagramas de corda a partir dos dados de otimização. |
| `codigo_atual.py` | Versão de trabalho mais recente do script em Python. |
| `CAP_vis2.R` · `grafico.r` | Implementações equivalentes em **R** (biblioteca `circlize`) para chord diagram e mapeamento angular. |
| `wfg4_dwu-dec.csv` · `plano_4D.csv` | Conjuntos de dados de soluções multiobjetivo (benchmark WFG4 e plano 4D). |
| `Iris-*.csv` · `cartonn.csv` | Dados auxiliares para validação das visualizações. |

## 🛠️ Tecnologias

`Python` (NumPy · Pandas · Matplotlib · **pyCirclize**) · `R` (**circlize**)

## ▶️ Como executar (Python)

```bash
pip install numpy pandas matplotlib pycirclize
python grafico_otimizado.py
```

---

> Projeto de pesquisa em andamento, orientado no âmbito da graduação. As visualizações têm como meta apoiar a análise e a tomada de decisão em problemas de otimização com muitos objetivos.
