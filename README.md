# Separatrizes: PIB per capita dos municípios do Rio Grande do Norte

Documentação do projeto para reprodução no GitHub: objetivo, origem dos dados, passos de coleta e explicação dos arquivos Python.

## 1. Objetivo

Este projeto responde a uma atividade de **separatrizes** aplicada ao PIB per capita municipal do Rio Grande do Norte.

Perguntas da atividade:

1. Obter o PIB per capita de **todos os municípios do RN**.
2. Criar o grupo com os **10% municípios de menor PIB per capita**.
   - **2.1** Calcular o **percentil 10**.
   - **2.2** Separar os municípios com PIB per capita **menor que** o percentil 10.
   - **2.3** Apresentar variáveis que possam explicar esses PIBs per capita.
3. Descrever sumariamente essa situação.

Para isso, o repositório:

- consulta as **APIs oficiais do IBGE** (as mesmas bases do portal Cidades@);
- organiza os dados em **CSV** e **XLSX**;
- calcula a separatriz (percentil 10) em Python;
- disponibiliza uma **API local** opcional para consultar o resultado.

Portal de referência da atividade:

[https://cidades.ibge.gov.br/brasil/rn/panorama](https://cidades.ibge.gov.br/brasil/rn/panorama)

Esse endereço **não é uma API**. É uma página web. Os dados vêm de serviços REST públicos do IBGE, descritos abaixo.

## 2. Requisitos para reproduzir

- Python 3.10 ou superior
- Acesso à internet (na primeira coleta)
- Dependências listadas em `requirements.txt`

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python gerar_dataset.py
```

Para acompanhar a atividade pergunta a pergunta, abra o notebook `atividade_separatrizes_pib_rn.ipynb` e execute todas as células.

Para gerar o dataset em notebook (em vez do terminal), abra `gerar_dataset.ipynb` e execute todas as células.

No Linux ou macOS, ative o ambiente com:

```bash
source .venv/bin/activate
```

A pasta `data/` **não vai para o GitHub**: ela é criada na sua máquina quando você roda `python gerar_dataset.py`.

## 3. Estrutura do repositório

```text
API_IBGE/
├── README.md                 # este arquivo
├── requirements.txt          # bibliotecas Python
├── .gitignore                # o que o Git não deve versionar
├── gerar_dataset.py          # ponto de entrada da coleta (terminal)
├── gerar_dataset.ipynb       # a mesma coleta, em notebook passo a passo
├── atividade_separatrizes_pib_rn.ipynb  # notebook da atividade (perguntas)
├── src/
│   ├── __init__.py           # torna src um pacote Python
│   ├── ibge_client.py        # cliente HTTP das APIs do IBGE
│   ├── pipeline.py           # junta os dados, calcula o P10 e exporta
│   ├── api.py                # API local (FastAPI), opcional
│   └── relatorio.py          # gerador de PDF/XLSX formatado (opcional)
└── data/                     # criada na sua máquina ao rodar gerar_dataset.py
    ├── municipios_rn.csv
    ├── municipios_rn.xlsx
    ├── grupo_p10_menores_pib.csv
    └── resumo_separatriz.json
```

Os arquivos de `data/` ficam no `.gitignore`. Quem clona o repositório baixa o código e o notebook, e gera os dados localmente com `python gerar_dataset.py`.

### Explicação de cada arquivo

#### Arquivos da raiz

| Arquivo | Para que serve |
| --- | --- |
| `README.md` | Documentação do GitHub: objetivo, como coletar os dados, como reproduzir o projeto e o significado de cada arquivo. |
| `requirements.txt` | Lista das bibliotecas Python necessárias (`pandas`, `numpy`, `openpyxl`, `fastapi`, `uvicorn`). Instale com `pip install -r requirements.txt`. |
| `.gitignore` | Impede que o Git envie lixo ao repositório (pasta `.venv`, cache `__pycache__`, arquivos temporários). |
| `gerar_dataset.py` | **Arquivo principal para coletar os dados no terminal.** Baixa os indicadores do IBGE, calcula o percentil 10, monta o grupo dos menores PIBs e grava CSV/XLSX em `data/`. |
| `gerar_dataset.ipynb` | **A mesma coleta, em notebook.** Explica cada etapa (municípios, PIB, Censo, percentil 10 e exportação) com texto e código comentado. Também funciona no Google Colab. |
| `atividade_separatrizes_pib_rn.ipynb` | **Notebook da atividade.** Responde cada pergunta com células de texto e código, usando o dataset já gerado. |

#### Pasta `src/` (código)

| Arquivo | Para que serve |
| --- | --- |
| `src/__init__.py` | Arquivo vazio só para o Python tratar `src` como um pacote (`from src.pipeline import ...`). |
| `src/ibge_client.py` | Fala com as APIs oficiais do IBGE: lista municípios do RN, busca PIB, Censo, alfabetização e IDHM. Não calcula estatística; só baixa e organiza o JSON. |
| `src/pipeline.py` | Coração da atividade. Cruza os indicadores em uma tabela, calcula o percentil 10, marca quem está abaixo do P10, escreve a descrição sumária e exporta os arquivos. |
| `src/api.py` | API local opcional (FastAPI). Serve o dataset já gerado em rotas como `/pib-per-capita` e `/grupo-p10`. Não substitui o IBGE. |
| `src/relatorio.py` | Gera um PDF da atividade e um Excel com nomes de colunas em português. É opcional e pede bibliotecas extras (`fpdf2`, `matplotlib`). |

#### Pasta `data/` (resultados da coleta — gerados localmente, não versionados)

Depois de `python gerar_dataset.py`, aparecem:

| Arquivo | Para que serve |
| --- | --- |
| `data/municipios_rn.csv` | Dataset completo dos **167 municípios** do RN: PIB per capita 2023, população, densidade, VAB setorial, alfabetização, IDHM e as colunas da separatriz. É o arquivo principal para análise. |
| `data/grupo_p10_menores_pib.csv` | Recorte da pergunta 2.2: só os municípios com PIB per capita **menor que o percentil 10** (17 cidades na coleta já feita). |
| `data/municipios_rn.xlsx` | A mesma informação em Excel, com quatro abas: `Todos_municipios` (pergunta 1), `Grupo_P10` (pergunta 2.2), `Comparativo` (pergunta 2.3) e `Resumo` (P10 + descrição). |
| `data/resumo_separatriz.json` | Resumo em JSON: valor do percentil 10, lista dos municípios do grupo, médias comparativas e o parágrafo da descrição sumária. |

Como as abas do Excel respondem à atividade:

| Aba do XLSX | Pergunta |
| --- | --- |
| `Todos_municipios` | 1. PIB per capita de todos os municípios |
| `Resumo` (campo do percentil 10) | 2.1 Calcular o percentil 10 |
| `Grupo_P10` | 2.2 Municípios com PIB per capita menor que o P10 |
| `Comparativo` | 2.3 Variáveis que podem explicar esses PIBs |

## 4. De onde os dados saem

O IBGE já publica APIs abertas. Este projeto **não raspa o HTML** do Cidades@ e **não inventa uma fonte nova**. Ele só organiza as consultas.

| API | URL base | Para que serve aqui |
| --- | --- | --- |
| Localidades | `https://servicodados.ibge.gov.br/api/v1/localidades` | Lista os 167 municípios do RN (UF `24`) |
| Pesquisas (Cidades@) | `https://servicodados.ibge.gov.br/api/v1/pesquisas` | PIB, VAB setorial, IDHM e indicadores do panorama |
| Agregados (SIDRA) | `https://servicodados.ibge.gov.br/api/v3/agregados` | População, área, densidade e alfabetização do Censo 2022 |

Documentação oficial:

- [API de Pesquisas](https://servicodados.ibge.gov.br/api/docs/pesquisas?versao=1)
- [API de Agregados](https://servicodados.ibge.gov.br/api/docs/agregados?versao=3)
- [API de Localidades](https://servicodados.ibge.gov.br/api/docs/localidades)

O recorte `N6[N3[24]]` significa: **todos os municípios (nível N6) contidos na Unidade da Federação 24 (RN)**.

Há dois códigos de município:

- **7 dígitos** na API de Localidades e na de Agregados (exemplo: `2400109` = Acari)
- **6 dígitos** na API de Pesquisas (exemplo: `240010`)

O projeto guarda o código de 7 dígitos e usa os 6 primeiros para cruzar as duas APIs.

## 5. Passo a passo da coleta (reproduzível)

A sequência abaixo é exatamente a que `gerar_dataset.py` executa.

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

Esse é o indicador central da atividade.

Observação: na tabela SIDRA 5938, o código `543` **não** é PIB per capita; é impostos sobre produtos. O PIB per capita do Cidades@ é o indicador `47001`.

### Passo 3 — Valor adicionado por setor (2021)

Para 2022 e 2023 o IBGE divulgou só o PIB e o PIB per capita. A composição setorial completa mais recente é **2021**.

| Indicador | Setor |
| --- | --- |
| `47006` | Agropecuária |
| `47007` | Indústria |
| `47008` | Serviços (exclusive administração pública) |
| `47009` | Administração, defesa, educação e saúde públicas e seguridade social |

Exemplo:

```
https://servicodados.ibge.gov.br/api/v1/pesquisas/38/periodos/2021/indicadores/47006/resultados/N6[N3[24]]
```

No pipeline, a participação de cada setor é calculada assim:

```text
participação = 100 × (VAB do setor / soma dos quatro VABs)
```

Essas participações entram na questão 2.3 (variáveis explicativas).

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

A população do Censo 2022 é a mesma base que o IBGE usa no PIB per capita recente.

### Passo 5 — Alfabetização (Censo 2022)

Tabela SIDRA **9543**, variável `2513` (taxa de alfabetização de 15 anos ou mais).  
Filtro de totais: sexo `2[6794]`, cor ou raça `86[95251]`, idade `287[100362]`.

```
https://servicodados.ibge.gov.br/api/v3/agregados/9543/periodos/2022/variaveis/2513?localidades=N6[N3[24]]&classificacao=2[6794]|86[95251]|287[100362]
```

### Passo 6 — Indicadores sociais complementares

Consultas da API de Pesquisas. Se alguma falhar, o script segue e deixa a coluna vazia (`consultar_indicador_opcional`).

| Pesquisa | Indicador | Conteúdo |
| --- | --- | --- |
| `10111` | `329756` | IDHM |
| `10058` | `60045` | Taxa de escolarização de 6 a 14 anos |
| `10058` | `60038` | Salário médio mensal |
| `10058` | `60036` | População ocupada |

Exemplo:

```
https://servicodados.ibge.gov.br/api/v1/pesquisas/10111/indicadores/329756/resultados/N6[N3[24]]
```

### Passo 7 — Cruzar tudo em uma tabela municipal

`src/pipeline.py` monta uma linha por município, unindo:

- código e nome (Localidades);
- PIB e PIB per capita (2023);
- VAB e participações setoriais (2021);
- demografia e alfabetização (Censo 2022);
- IDHM, escolarização, salário médio e ocupação.

### Passo 8 — Calcular o percentil 10 e recortar o grupo

```python
p10 = round(float(numpy.percentile(pib_per_capita, 10)), 2)
abaixo_percentil_10 = pib_per_capita < p10
```

O método padrão do NumPy interpola linearmente os valores ordenados.

Regra da atividade (questão 2.2): município entra no grupo se o PIB per capita for **estritamente menor** que o P10.

Há também a coluna `entre_os_10_pct_menores`, que marca os 10% de menor ranking (`ceil(0,10 × 167) = 17`). Serve só para conferência. A análise usa `abaixo_percentil_10`.

### Passo 9 — Exportar

O script grava em `data/`:

| Arquivo | Conteúdo |
| --- | --- |
| `municipios_rn.csv` | Dataset completo (167 municípios) |
| `grupo_p10_menores_pib.csv` | Só o grupo abaixo do P10 |
| `municipios_rn.xlsx` | Abas `Todos_municipios`, `Grupo_P10`, `Comparativo` e `Resumo` |
| `resumo_separatriz.json` | P10, lista do grupo, comparativo e descrição |

## 6. Como a atividade fica respondida nos dados

### Questão 1 — PIB per capita de todos os municípios

Coluna `pib_per_capita` em `data/municipios_rn.csv` e na aba `Todos_municipios` do XLSX. Ano: **2023**. Cobertura: **167 municípios**.

### Questão 2.1 — Percentil 10

Coluna `percentil_10_pib_per_capita` (o mesmo valor em todas as linhas) e o campo `percentil_10_pib_per_capita` em `resumo_separatriz.json`.

Na coleta já realizada, o P10 foi **R$ 13.668,37**.

### Questão 2.2 — Municípios abaixo do P10

Filtrar `abaixo_percentil_10 == True`, ou abrir `grupo_p10_menores_pib.csv`. Na coleta já realizada, são **17 municípios**.

### Questão 2.3 — Variáveis explicativas

No grupo P10, o dataset traz:

- população, área e densidade;
- participação da agropecuária, indústria, serviços e administração pública no VAB;
- taxa de alfabetização, escolarização, IDHM, salário médio e população ocupada.

A aba `Comparativo` compara **média e mediana** dessas variáveis no grupo P10 versus os demais municípios do RN.

Leitura resumida da coleta já feita: o décimo inferior reúne municípios pequenos, de baixa densidade, com maior peso da administração pública, menor peso da indústria e indicadores sociais um pouco mais frágeis.

## 7. Explicação dos arquivos Python

### `gerar_dataset.py`

Ponto de entrada. Só chama `executar()` de `src/pipeline.py` e imprime:

- quantidade de municípios;
- ano do PIB;
- valor do percentil 10;
- nomes do grupo P10;
- caminhos dos arquivos gerados;
- a descrição sumária.

Rode sempre na **raiz do repositório**, para o Python encontrar o pacote `src`.

### `src/ibge_client.py`

Cliente HTTP das APIs do IBGE, sem biblioteca extra (`urllib`).

Funções principais:

| Função | Papel |
| --- | --- |
| `_get_json` | Faz o GET, trata gzip, tenta de novo se a API falhar |
| `listar_municipios_rn` | Passo 1 da coleta |
| `consultar_indicador` | API de Pesquisas (Cidades@) |
| `consultar_indicador_opcional` | Igual à anterior, mas não interrompe o programa se der erro |
| `consultar_agregado` | API de Agregados / SIDRA |
| `valor_do_ano` / `ultimo_valor` | Escolhe o ano pedido ou o mais recente disponível |

Constantes úteis:

- `CODIGO_RN = "24"`
- `LOCALIDADES_MUNICIPIOS_RN = "N6[N3[24]]"`

### `src/pipeline.py`

Orquestra a atividade.

| Função | Papel |
| --- | --- |
| `coletar_dados` | Executa os passos 1 a 7 |
| `aplicar_separatriz` | Calcula o P10 e cria as colunas do grupo |
| `resumo_separatriz` | Monta o JSON com médias, lista do grupo e texto |
| `descrever_situacao` | Redige a descrição sumária a partir dos números |
| `exportar` | Grava CSV, XLSX e JSON |
| `executar` | Roda coleta + resumo + exportação |

Anos usados no código:

```python
ANO_PIB = "2023"
ANO_VAB = "2021"
ANO_CENSO = "2022"
PERCENTIL = 10
```

### `src/api.py`

API local opcional (FastAPI). Não substitui o IBGE: só serve o dataset já gerado.

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
| `/download/xlsx` | Download da planilha |
| `/download/csv` | Download do CSV (`?grupo=true` baixa só o P10) |
| `/docs` | Documentação interativa |

Se `data/municipios_rn.csv` já existir, a API lê o arquivo. Se não existir, ela chama a coleta do IBGE na primeira requisição.

### `src/relatorio.py`

Módulo auxiliar para gerar um PDF da atividade e um XLSX com nomes de colunas em português. Depende de `fpdf2` e `matplotlib`, que não estão no `requirements.txt` básico. Use só se quiser o relatório formatado além do CSV/XLSX padrão.

### `requirements.txt`

Bibliotecas do fluxo principal:

- `pandas` — tabelas
- `numpy` — percentil
- `openpyxl` — Excel
- `fastapi` e `uvicorn` — API local

## 8. Dicionário das colunas do dataset

| Coluna | Significado |
| --- | --- |
| `codigo_municipio` | Código IBGE de 7 dígitos |
| `municipio` | Nome do município |
| `mesorregiao` / `microrregiao` | Recortes territoriais do IBGE |
| `pib_per_capita` | PIB per capita 2023 (R$) |
| `pib_mil_reais` | PIB 2023 (R$ mil) |
| `percentil_10_pib_per_capita` | Valor da separatriz |
| `abaixo_percentil_10` | `True` se PIB per capita < P10 |
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

## 9. Observações para quem for reproduzir

- A primeira execução depende das APIs do IBGE e pode levar cerca de um minuto.
- Se um indicador opcional (IDHM, salário, ocupação) estiver fora do ar, o restante da coleta continua.
- Os valores de 2023 do PIB municipal podem ser revisados em divulgações seguintes do IBGE.
- Não é necessário token nem cadastro: as APIs usadas são públicas.
- Rode os comandos na raiz do repositório (`API_IBGE/`), não dentro de `src/`.

## 10. Licença dos dados

Os microdados agregados e indicadores pertencem ao **IBGE**. Este repositório apenas organiza consultas públicas para uma atividade acadêmica. Ao republicar, mantenha a citação da fonte.
