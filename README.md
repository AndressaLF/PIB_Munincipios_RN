# Separatrizes: PIB per capita dos municípios do Rio Grande do Norte

Atividade acadêmica de **separatrizes** aplicada ao PIB per capita de **todos os municípios do RN**. O projeto consulta as **APIs oficiais do IBGE** (as mesmas bases do [Cidades@](https://cidades.ibge.gov.br/brasil/rn/panorama)), calcula o **percentil 10** e descreve o grupo com os menores valores.

O portal Cidades@ é uma **página web**, não uma API. Os dados saem dos serviços REST públicos do IBGE, documentados mais abaixo.

[![Abrir a atividade no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AndressaLF/PIB_Munincipios_RN/blob/main/atividade_separatrizes_pib_rn.ipynb)
[![Gerar o dataset no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/AndressaLF/PIB_Munincipios_RN/blob/main/gerar_dataset.ipynb)

**Resultado de referência** (coleta já realizada; o IBGE pode revisar a série):

| Item | Valor |
| --- | --- |
| Municípios do RN | 167 |
| Ano do PIB per capita | 2023 |
| Percentil 10 | R$ 13.668,37 |
| Municípios abaixo do P10 | 17 |

---

## Por onde começar

Escolha **um** caminho. Os três fazem a mesma coleta; os notebooks só explicam mais.

| Quem você é | O que abrir |
| --- | --- |
| Quer **responder a atividade** pergunta a pergunta | `atividade_separatrizes_pib_rn.ipynb` |
| Quer **ver como os dados são baixados** do IBGE | `gerar_dataset.ipynb` |
| Prefere o **terminal** | `python gerar_dataset.py` |
| Está no **Google Colab** | Clone o repositório **inteiro** (precisa da pasta `src/`) |

**CSV não vai no GitHub e não é obrigatório.** A pasta `data/` é criada na sua máquina (ou no Colab) quando a coleta roda. Sem CSV, o código em `src/` baixa os indicadores do IBGE (internet, cerca de 1 minuto).

### Opção A — Notebooks (recomendado para a disciplina)

1. Instale as bibliotecas uma vez (no computador):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

No Linux ou macOS: `source .venv/bin/activate`.

2. Abra **nesta ordem**:

| Ordem | Arquivo | Função |
| --- | --- | --- |
| 1 | `gerar_dataset.ipynb` | Baixa os dados e grava `data/` |
| 2 | `atividade_separatrizes_pib_rn.ipynb` | Responde as perguntas 1, 2.1, 2.2, 2.3 e a descrição |

3. Em cada notebook: **Run All** / **Executar tudo**. Leia os blocos de texto; no código, as linhas com `#` são comentários.

Se `data/` ainda não existir, o notebook da atividade tenta coletar sozinho (desde que `src/` esteja no mesmo projeto).

### Opção B — Terminal

Na **raiz** do repositório (não dentro de `src/`):

```bash
python gerar_dataset.py
```

Isso grava em `data/`:

- `municipios_rn.csv` — 167 municípios
- `grupo_p10_menores_pib.csv` — só quem está abaixo do P10
- `municipios_rn.xlsx` — abas da atividade
- `resumo_separatriz.json` — P10, lista do grupo e descrição

### Opção C — Google Colab

Não envie **só** o arquivo `.ipynb`. O código que fala com o IBGE está em `src/`.

```text
!git clone https://github.com/AndressaLF/PIB_Munincipios_RN.git
%cd PIB_Munincipios_RN
```

Depois abra o notebook **dentro** da pasta clonada. Os dois notebooks também tentam clonar sozinhos se detectarem o Colab e a pasta `src/` estiver ausente.

---

## Sumário

1. [Objetivo da atividade](#1-objetivo-da-atividade)
2. [O que cada notebook faz](#2-o-que-cada-notebook-faz)
3. [Requisitos](#3-requisitos)
4. [Estrutura do repositório](#4-estrutura-do-repositório)
5. [De onde os dados saem](#5-de-onde-os-dados-saem)
6. [Passo a passo da coleta](#6-passo-a-passo-da-coleta)
7. [Como a atividade fica respondida](#7-como-a-atividade-fica-respondida)
8. [Código Python](#8-código-python)
9. [API local (opcional)](#9-api-local-opcional)
10. [Dicionário das colunas](#10-dicionário-das-colunas)
11. [Observações](#11-observações)
12. [Licença dos dados](#12-licença-dos-dados)

---

## 1. Objetivo da atividade

1. Obter o PIB per capita de **todos os municípios do RN**.
2. Criar o grupo com os **10% municípios de menor PIB per capita**.
   - **2.1** Calcular o **percentil 10**.
   - **2.2** Separar os municípios com PIB per capita **menor que** o percentil 10.
   - **2.3** Apresentar variáveis que possam explicar esses PIBs per capita.
3. Descrever sumariamente essa situação.

Regra da pergunta 2.2 no código:

```python
p10 = round(float(np.percentile(pib_per_capita, 10)), 2)
abaixo_percentil_10 = pib_per_capita < p10
```

O símbolo `<` é **estritamente menor**: quem tiver exatamente o P10 não entra no grupo.

---

## 2. O que cada notebook faz

Os dois arquivos são didáticos: células de **texto** explicam a ideia; células de **código** calculam, com comentários em português.

| Notebook | Papel | Precisa de CSV? |
| --- | --- | --- |
| `gerar_dataset.ipynb` | Coleta nas APIs, calcula o P10, grava `data/` | Não. Ele **cria** os arquivos. |
| `atividade_separatrizes_pib_rn.ipynb` | Responde cada pergunta, com tabelas e gráficos | Não. Se o CSV não existir e `src/` estiver presente, baixa do IBGE. |

`gerar_dataset.py` é o equivalente do primeiro notebook no terminal (sem os textos explicativos).

---

## 3. Requisitos

- Python 3.10 ou superior
- Internet na primeira coleta
- Bibliotecas em `requirements.txt`: `pandas`, `numpy`, `openpyxl`, `matplotlib`, `fastapi`, `uvicorn`

```bash
pip install -r requirements.txt
```

`matplotlib` entra nos gráficos da atividade. `fastapi` e `uvicorn` só são necessários se for subir a API local.

---

## 4. Estrutura do repositório

```text
PIB_Munincipios_RN/
├── README.md                          # este arquivo
├── requirements.txt                   # bibliotecas Python
├── .gitignore                         # venv, cache e pasta data/
├── gerar_dataset.py                   # coleta no terminal
├── gerar_dataset.ipynb                # coleta passo a passo (notebook)
├── atividade_separatrizes_pib_rn.ipynb
├── src/
│   ├── __init__.py
│   ├── ibge_client.py                 # HTTP das APIs do IBGE
│   ├── pipeline.py                    # cruza dados, P10 e exportação
│   ├── api.py                         # FastAPI local (opcional)
│   └── relatorio.py                   # PDF/XLSX formatado (opcional)
└── data/                              # gerada na sua máquina, não vai ao GitHub
    ├── municipios_rn.csv
    ├── municipios_rn.xlsx
    ├── grupo_p10_menores_pib.csv
    └── resumo_separatriz.json
```

### Arquivos da raiz

| Arquivo | Para que serve |
| --- | --- |
| `README.md` | Documentação do GitHub. |
| `requirements.txt` | Dependências. Instale com `pip install -r requirements.txt`. |
| `.gitignore` | Impede versionar `.venv`, `__pycache__`, CSV/XLSX/JSON e a pasta `data/`. |
| `gerar_dataset.py` | Ponto de entrada no terminal: coleta, P10 e exportação. |
| `gerar_dataset.ipynb` | A mesma coleta, explicada célula a célula. Funciona no Colab. |
| `atividade_separatrizes_pib_rn.ipynb` | Notebook da disciplina: perguntas, gráficos e descrição. |

### Pasta `src/`

| Arquivo | Para que serve |
| --- | --- |
| `src/__init__.py` | Torna `src` um pacote (`from src.pipeline import ...`). |
| `src/ibge_client.py` | Lista municípios do RN e baixa PIB, Censo, alfabetização e IDHM. Não calcula estatística. |
| `src/pipeline.py` | Cruza os indicadores, calcula o percentil 10, descreve a situação e exporta. |
| `src/api.py` | API local opcional. Serve o dataset já gerado; **não** substitui o IBGE. |
| `src/relatorio.py` | PDF e Excel com rótulos em português. Pede `fpdf2` e `matplotlib` (o PDF é extra). |

### Pasta `data/` (gerada localmente)

| Arquivo | Conteúdo |
| --- | --- |
| `municipios_rn.csv` | Dataset completo: PIB 2023, população, VAB setorial, alfabetização, IDHM e colunas da separatriz. |
| `grupo_p10_menores_pib.csv` | Só os municípios com PIB per capita **menor que** o P10. |
| `municipios_rn.xlsx` | Abas `Todos_municipios`, `Grupo_P10`, `Comparativo` e `Resumo`. |
| `resumo_separatriz.json` | P10, nomes do grupo, médias comparativas e o parágrafo da descrição. |

| Aba do XLSX | Pergunta |
| --- | --- |
| `Todos_municipios` | 1. PIB per capita de todos os municípios |
| `Resumo` | 2.1 Valor do percentil 10 |
| `Grupo_P10` | 2.2 Municípios com PIB per capita menor que o P10 |
| `Comparativo` | 2.3 Variáveis que podem explicar esses PIBs |

---

## 5. De onde os dados saem

O projeto **não raspa HTML** do Cidades@ e **não inventa fonte**. Só organiza consultas oficiais.

| API | URL base | Uso neste projeto |
| --- | --- | --- |
| Localidades | `https://servicodados.ibge.gov.br/api/v1/localidades` | 167 municípios do RN (UF `24`) |
| Pesquisas (Cidades@) | `https://servicodados.ibge.gov.br/api/v1/pesquisas` | PIB, VAB setorial, IDHM e panorama |
| Agregados (SIDRA) | `https://servicodados.ibge.gov.br/api/v3/agregados` | População, área, densidade e alfabetização (Censo 2022) |

Documentação oficial:

- [API de Pesquisas](https://servicodados.ibge.gov.br/api/docs/pesquisas?versao=1)
- [API de Agregados](https://servicodados.ibge.gov.br/api/docs/agregados?versao=3)
- [API de Localidades](https://servicodados.ibge.gov.br/api/docs/localidades)

O recorte `N6[N3[24]]` significa: **todos os municípios (N6)** contidos na **UF 24 (RN)**.

Há dois códigos de município:

- **7 dígitos** em Localidades e Agregados (exemplo: `2400109` = Acari)
- **6 dígitos** na API de Pesquisas (exemplo: `240010`)

O projeto guarda o código de 7 dígitos e usa os 6 primeiros para cruzar as APIs.

---

## 6. Passo a passo da coleta

A sequência abaixo é a que `gerar_dataset.py` e `gerar_dataset.ipynb` executam.

### Passo 1 — Listar os municípios do RN

```
https://servicodados.ibge.gov.br/api/v1/localidades/estados/24/municipios?orderBy=nome
```

Retorna nome, código IBGE, microrregião, mesorregião e regiões imediata/intermediária.

Função: `listar_municipios_rn()` em `src/ibge_client.py`.

### Passo 2 — PIB per capita e PIB total (2023)

Pesquisa **38** = Produto Interno Bruto dos Municípios.

| Indicador | Conteúdo |
| --- | --- |
| `47001` | PIB per capita, série revisada (R$) |
| `46997` | PIB a preços correntes, série revisada (R$ mil) |

```
https://servicodados.ibge.gov.br/api/v1/pesquisas/38/periodos/2023/indicadores/47001/resultados/N6[N3[24]]
https://servicodados.ibge.gov.br/api/v1/pesquisas/38/periodos/2023/indicadores/46997/resultados/N6[N3[24]]
```

Na tabela SIDRA 5938, o código `543` **não** é PIB per capita; é impostos sobre produtos. O PIB per capita do Cidades@ é o indicador `47001`.

### Passo 3 — Valor adicionado por setor (2021)

Para 2022 e 2023 o IBGE divulgou só o PIB e o PIB per capita. A composição setorial completa mais recente é **2021**.

| Indicador | Setor |
| --- | --- |
| `47006` | Agropecuária |
| `47007` | Indústria |
| `47008` | Serviços (exclusive administração pública) |
| `47009` | Administração, defesa, educação e saúde públicas e seguridade social |

```
https://servicodados.ibge.gov.br/api/v1/pesquisas/38/periodos/2021/indicadores/47006/resultados/N6[N3[24]]
```

Participação de cada setor:

```text
participação = 100 × (VAB do setor / soma dos quatro VABs)
```

Essas participações entram na questão 2.3.

### Passo 4 — População, área e densidade (Censo 2022)

Tabela SIDRA **4714**:

| Variável | Conteúdo |
| --- | --- |
| `93` | População residente |
| `6318` | Área da unidade territorial (km²) |
| `614` | Densidade demográfica (hab/km²) |

```
https://servicodados.ibge.gov.br/api/v3/agregados/4714/periodos/2022/variaveis/93|6318|614?localidades=N6[N3[24]]
```

### Passo 5 — Alfabetização (Censo 2022)

Tabela SIDRA **9543**, variável `2513` (taxa de alfabetização de 15 anos ou mais).  
Filtro de totais: sexo `2[6794]`, cor ou raça `86[95251]`, idade `287[100362]`.

```
https://servicodados.ibge.gov.br/api/v3/agregados/9543/periodos/2022/variaveis/2513?localidades=N6[N3[24]]&classificacao=2[6794]|86[95251]|287[100362]
```

### Passo 6 — Indicadores sociais complementares

Se alguma consulta falhar, o script segue e deixa a coluna vazia (`consultar_indicador_opcional`).

| Pesquisa | Indicador | Conteúdo |
| --- | --- | --- |
| `10111` | `329756` | IDHM |
| `10058` | `60045` | Taxa de escolarização de 6 a 14 anos |
| `10058` | `60038` | Salário médio mensal |
| `10058` | `60036` | População ocupada |

```
https://servicodados.ibge.gov.br/api/v1/pesquisas/10111/indicadores/329756/resultados/N6[N3[24]]
```

### Passo 7 — Cruzar tudo em uma tabela municipal

`src/pipeline.py` monta uma linha por município, unindo código e nome, PIB 2023, VAB 2021, Censo 2022 e indicadores sociais.

### Passo 8 — Percentil 10 e grupo

O NumPy interpola linearmente os valores ordenados. A análise usa `abaixo_percentil_10`.

Há também `entre_os_10_pct_menores`, que marca os 10% de menor ranking (`ceil(0,10 × 167) = 17`). Serve só para conferência.

### Passo 9 — Exportar

Grava os quatro arquivos de `data/` listados na [estrutura](#4-estrutura-do-repositório).

---

## 7. Como a atividade fica respondida

### Questão 1 — PIB per capita de todos os municípios

Coluna `pib_per_capita` em `municipios_rn.csv` e na aba `Todos_municipios`. Ano: **2023**. Cobertura: **167 municípios**.

### Questão 2.1 — Percentil 10

Coluna `percentil_10_pib_per_capita` (o mesmo valor em todas as linhas) e o campo homônimo em `resumo_separatriz.json`.

Na coleta de referência: **R$ 13.668,37**.

### Questão 2.2 — Municípios abaixo do P10

Filtrar `abaixo_percentil_10 == True`, ou abrir `grupo_p10_menores_pib.csv`. Na coleta de referência: **17 municípios**.

### Questão 2.3 — Variáveis explicativas

No grupo P10 o dataset traz população, área, densidade, participação setorial no VAB, alfabetização, escolarização, IDHM, salário médio e população ocupada.

A aba `Comparativo` compara **média e mediana** dessas variáveis no grupo P10 versus os demais municípios do RN.

Leitura da coleta de referência: o décimo inferior reúne municípios **pequenos**, de **baixa densidade**, com **maior peso da administração pública** (~66% vs ~47% do VAB), **menor peso da indústria** (~4% vs ~16%) e indicadores de alfabetização e IDHM um pouco mais frágeis.

O VAB setorial é de **2021**; o PIB per capita é de **2023**; o Censo é de **2022**. Anos diferentes, fontes oficiais distintas.

---

## 8. Código Python

### `gerar_dataset.py`

Chama `executar()` de `src/pipeline.py` e imprime quantidade de municípios, ano do PIB, P10, nomes do grupo e caminhos dos arquivos.

Rode sempre na **raiz** do repositório.

### `src/ibge_client.py`

Cliente HTTP com `urllib` (sem biblioteca extra de rede).

| Função | Papel |
| --- | --- |
| `_get_json` | GET, gzip e nova tentativa se a API falhar |
| `listar_municipios_rn` | Passo 1 |
| `consultar_indicador` | API de Pesquisas (Cidades@) |
| `consultar_indicador_opcional` | Igual, mas não interrompe se der erro |
| `consultar_agregado` | API de Agregados / SIDRA |
| `valor_do_ano` / `ultimo_valor` | Ano pedido ou o mais recente disponível |

Constantes: `CODIGO_RN = "24"` e `LOCALIDADES_MUNICIPIOS_RN = "N6[N3[24]]"`.

### `src/pipeline.py`

| Função | Papel |
| --- | --- |
| `coletar_dados` | Passos 1 a 7 |
| `aplicar_separatriz` | P10 e colunas do grupo |
| `resumo_separatriz` | JSON com médias, lista e texto |
| `descrever_situacao` | Parágrafo da descrição sumária |
| `exportar` | CSV, XLSX e JSON |
| `executar` | Coleta + resumo + exportação |

```python
ANO_PIB = "2023"
ANO_VAB = "2021"
ANO_CENSO = "2022"
PERCENTIL = 10
```

### `src/relatorio.py`

Módulo auxiliar de PDF/XLSX formatado. `fpdf2` não está no `requirements.txt` básico.

---

## 9. API local (opcional)

Não substitui o IBGE: só serve o dataset já gerado.

```bash
uvicorn src.api:app --reload --port 8000
```

| Rota | Conteúdo |
| --- | --- |
| `/` | Visão geral e links das fontes |
| `/municipios` | Dataset completo em JSON |
| `/pib-per-capita` | PIB per capita de todos os municípios |
| `/separatriz` | P10 e descrição |
| `/grupo-p10` | Municípios abaixo do P10 |
| `/download/xlsx` | Planilha |
| `/download/csv` | CSV (`?grupo=true` baixa só o P10) |
| `/docs` | Documentação interativa |

Se `data/municipios_rn.csv` existir, a API lê o arquivo. Se não existir, chama a coleta do IBGE na primeira requisição.

---

## 10. Dicionário das colunas

| Coluna | Significado |
| --- | --- |
| `codigo_municipio` | Código IBGE de 7 dígitos |
| `municipio` | Nome do município |
| `mesorregiao` / `microrregiao` | Recortes territoriais do IBGE |
| `pib_per_capita` | PIB per capita 2023 (R$) |
| `pib_mil_reais` | PIB 2023 (R$ mil) |
| `percentil_10_pib_per_capita` | Valor da separatriz |
| `abaixo_percentil_10` | `True` se PIB per capita &lt; P10 |
| `ranking_pib_per_capita_asc` | 1 = menor PIB per capita |
| `populacao_censo_2022` | População do Censo 2022 |
| `area_km2` | Área territorial |
| `densidade_demografica` | Habitantes por km² |
| `participacao_*_pct` | Peso de cada setor no VAB de 2021 |
| `taxa_alfabetizacao_15_mais_pct` | Alfabetização de pessoas com 15 anos ou mais |
| `idhm` | Índice de Desenvolvimento Humano Municipal |
| `taxa_escolarizacao_6_a_14_pct` | Escolarização de 6 a 14 anos |
| `salario_medio_mensal` | Salário médio em salários mínimos |
| `populacao_ocupada` | Percentual da população ocupada |

---

## 11. Observações

- A primeira execução depende das APIs do IBGE e pode levar cerca de um minuto.
- Se um indicador opcional (IDHM, salário, ocupação) estiver fora do ar, o restante da coleta continua.
- Os valores de 2023 do PIB municipal podem ser revisados em divulgações seguintes do IBGE.
- Não é necessário token nem cadastro: as APIs usadas são públicas.
- Rode os comandos na raiz do repositório, não dentro de `src/`.
- No Colab, clone o repositório completo. Enviar só o `.ipynb` não inclui `src/`.

---

## 12. Licença dos dados

Os indicadores pertencem ao **IBGE**. Este repositório apenas organiza consultas públicas para uma atividade acadêmica. Ao republicar, mantenha a citação da fonte.
