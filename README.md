# Separatrizes: PIB per capita dos municípios do Rio Grande do Norte

Atividade acadêmica de **separatrizes** com o PIB per capita de **todos os municípios do RN**. O trabalho inteiro está em **um notebook**: ele baixa os dados das **APIs oficiais do IBGE** (as mesmas bases do [Cidades@](https://cidades.ibge.gov.br/brasil/rn/panorama)), monta um DataFrame, exporta Excel para o **Google Planilhas**, calcula o **percentil 10** e responde as perguntas.

O portal Cidades@ é uma **página web**, não uma API. Os números saem dos serviços REST públicos do IBGE. Tudo isso está **dentro do notebook** — não há pasta `src/` nem script à parte.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AndressaLF/PIB_Munincipios_RN/blob/main/atividade_separatrizes_pib_rn.ipynb)

**Resultado de referência** (o IBGE pode revisar a série):

| Item | Valor |
| --- | --- |
| Municípios do RN | 167 |
| Ano do PIB per capita | 2023 |
| Percentil 10 | R$ 13.668,37 |
| Municípios abaixo do P10 | 17 |

---

## Por onde começar

Abra `atividade_separatrizes_pib_rn.ipynb` e rode **Run All** / **Executar tudo**.

- No computador: `pip install -r requirements.txt` (Python 3.10+).
- No **Google Colab**: envie **só o notebook**. Precisa de internet na coleta (cerca de 1 minuto).

O notebook cria `data/municipios_rn.xlsx`. No Google Planilhas: **Arquivo → Importar** (ou abra o arquivo pelo Drive).

CSV e Excel **não vão para o GitHub**. Cada pessoa gera os arquivos na própria máquina ou no Colab.

---

## O que a atividade pede

1. Obter o PIB per capita de **todos os municípios do RN**.
2. Criar o grupo com os **10% de menor PIB per capita**.
   - **2.1** Calcular o **percentil 10**.
   - **2.2** Separar quem tem PIB per capita **menor que** o P10.
   - **2.3** Variáveis que possam explicar esses PIBs.
3. Descrever sumariamente a situação.

Regra da pergunta 2.2:

```python
p10 = round(float(np.percentile(pib_per_capita, 10)), 2)
abaixo_do_p10 = pib_per_capita < p10
```

O `<` é **estritamente menor**: quem tiver exatamente o P10 não entra no grupo.

---

## O que o notebook faz

Células de **texto** explicam; células de **código** executam, com comentários para quem está começando. As funções que falam com o IBGE (`baixar_json`, `listar_municipios_rn`, `consultar_cidades`, `consultar_sidra`, `montar_dataframe_rn` etc.) estão **definidas no próprio arquivo**, cada uma descrita em um bloco de texto.

Fluxo:

1. Objetivo e conceitos (separatriz, percentil, PIB per capita, DataFrame).
2. Importação das bibliotecas.
3. Quais dados vêm do Cidades@, de onde saem e para que servem.
4. Funções de coleta e download pelas APIs.
5. DataFrame municipal e exportação `.xlsx` (Google Planilhas).
6. Lista de todas as colunas.
7. Percentil 10 passo a passo (NumPy = Excel `PERCENTIL.INC` = Planilhas `PERCENTILE`).
8. Perguntas 1, 2.1, 2.2, 2.3 e descrição, com DataFrames e gráficos (Plotly).

No Google Planilhas / Excel, depois de importar o xlsx (coluna do PIB, por exemplo `J`):

```
=PERCENTILE(J2:J168; 0,1)
=ARRED(PERCENTILE(J2:J168; 0,1); 2)
```

---

## Arquivos do repositório

```text
PIB_Munincipios_RN/
├── README.md
├── requirements.txt
├── .gitignore
├── atividade_separatrizes_pib_rn.ipynb
└── data/                    # gerada ao rodar o notebook, não vai ao GitHub
    └── municipios_rn.xlsx
```

| Arquivo | Função |
| --- | --- |
| `atividade_separatrizes_pib_rn.ipynb` | Atividade completa: coleta, Excel, percentil e respostas. |
| `requirements.txt` | `pandas`, `numpy`, `openpyxl`, `plotly`. |
| `.gitignore` | Ignora `.venv`, cache, `data/` e planilhas geradas. |

Abas do Excel gerado:

| Aba | Pergunta |
| --- | --- |
| `Todos_municipios` | 1. PIB per capita de todos os municípios |
| `Grupo_P10` | 2.2 Municípios com PIB per capita menor que o P10 |
| `Comparativo` | 2.3 Variáveis explicativas |
| `Resumo` | P10 e descrição |

---

## De onde os dados saem

| API | Uso |
| --- | --- |
| [Localidades](https://servicodados.ibge.gov.br/api/docs/localidades) | 167 municípios do RN (UF `24`) |
| [Pesquisas / Cidades@](https://servicodados.ibge.gov.br/api/docs/pesquisas?versao=1) | PIB, VAB setorial, IDHM |
| [Agregados / SIDRA](https://servicodados.ibge.gov.br/api/docs/agregados?versao=3) | População, área, densidade, alfabetização (Censo 2022) |

O recorte `N6[N3[24]]` é “todos os municípios (N6) da UF 24”. Há dois códigos de município: **7 dígitos** (Localidades e SIDRA) e **6 dígitos** (Pesquisas). O notebook cruza pelos 6 primeiros dígitos.

| Dado | Indicador | Ano |
| --- | --- | --- |
| PIB per capita | Pesquisa 38, `47001` | 2023 |
| PIB total | Pesquisa 38, `46997` | 2023 |
| VAB por setor | Pesquisa 38, `47006`–`47009` | 2021 |
| População, área, densidade | SIDRA 4714 | 2022 |
| Alfabetização 15+ | SIDRA 9543, variável `2513` | 2022 |

O código SIDRA `543` **não** é PIB per capita (são impostos). A composição setorial completa mais recente é **2021**.

---

## Leitura da coleta de referência

No décimo inferior: municípios **pequenos**, de **baixa densidade**, **maior peso da administração pública** no VAB (~66% vs ~47%), **menor peso da indústria** (~4% vs ~16%) e alfabetização/IDHM um pouco mais frágeis.

---

## Dicionário das colunas

| Coluna | Significado |
| --- | --- |
| `codigo_municipio` | Código IBGE de 7 dígitos |
| `municipio` | Nome do município |
| `mesorregiao` / `microrregiao` | Recortes territoriais do IBGE |
| `pib_per_capita` | PIB per capita 2023 (R$) |
| `pib_mil_reais` | PIB 2023 (R$ mil) |
| `populacao_censo_2022` | População do Censo 2022 |
| `area_km2` / `densidade_demografica` | Área e habitantes por km² |
| `participacao_*_pct` | Peso de cada setor no VAB de 2021 |
| `taxa_alfabetizacao_15_mais_pct` | Alfabetização de 15 anos ou mais |
| `idhm` | Índice de Desenvolvimento Humano Municipal |
| `taxa_escolarizacao_6_a_14_pct` | Escolarização de 6 a 14 anos |
| `salario_medio_mensal` | Salário médio em salários mínimos |
| `populacao_ocupada` | Percentual da população ocupada |

---

## Observações

- A primeira execução depende das APIs do IBGE e pode levar cerca de um minuto.
- Não é necessário token nem cadastro.
- Os valores de 2023 do PIB municipal podem ser revisados pelo IBGE.
- No Colab, envie apenas o `.ipynb`.

---

## Licença dos dados

Os indicadores pertencem ao **IBGE**. Este repositório organiza consultas públicas para uma atividade acadêmica. Ao republicar, cite a fonte.
