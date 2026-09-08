"""API local simples para consultar PIB per capita dos municípios do RN."""

from __future__ import annotations

import json
from functools import lru_cache

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.responses import FileResponse

from src.pipeline import PASTA_DADOS, executar

app = FastAPI(
    title="API PIB per capita RN",
    description=(
        "Wrapper simples das APIs oficiais do IBGE (Cidades@ e Agregados/SIDRA) "
        "para a atividade de separatrizes do PIB per capita dos municípios do "
        "Rio Grande do Norte."
    ),
    version="1.0.0",
)


@lru_cache(maxsize=1)
def _dados():
    csv_todos = PASTA_DADOS / "municipios_rn.csv"
    csv_grupo = PASTA_DADOS / "grupo_p10_menores_pib.csv"
    xlsx = PASTA_DADOS / "municipios_rn.xlsx"
    json_resumo = PASTA_DADOS / "resumo_separatriz.json"

    if csv_todos.exists() and json_resumo.exists() and xlsx.exists():
        df = pd.read_csv(csv_todos)
        resumo = json.loads(json_resumo.read_text(encoding="utf-8"))
        arquivos = {
            "csv_todos": csv_todos,
            "csv_grupo": csv_grupo,
            "xlsx": xlsx,
            "resumo": json_resumo,
        }
        return df, resumo, arquivos

    return executar()


def _registros():
    df, _, _ = _dados()
    return df.where(df.notna(), None).to_dict(orient="records")


@app.get("/")
def raiz():
    return {
        "projeto": "API PIB per capita RN",
        "fonte_oficial": "https://cidades.ibge.gov.br/brasil/rn/panorama",
        "apis_ibge": [
            "https://servicodados.ibge.gov.br/api/docs/pesquisas?versao=1",
            "https://servicodados.ibge.gov.br/api/docs/agregados?versao=3",
            "https://servicodados.ibge.gov.br/api/docs/localidades",
        ],
        "rotas": [
            "/municipios",
            "/pib-per-capita",
            "/separatriz",
            "/grupo-p10",
            "/download/xlsx",
            "/download/csv",
        ],
    }


@app.get("/municipios")
def municipios():
    return _registros()


@app.get("/pib-per-capita")
def pib_per_capita():
    campos = [
        "codigo_municipio",
        "municipio",
        "mesorregiao",
        "microrregiao",
        "ano_pib",
        "pib_per_capita",
        "pib_mil_reais",
        "ranking_pib_per_capita_asc",
        "abaixo_percentil_10",
    ]
    return [{k: item[k] for k in campos} for item in _registros()]


@app.get("/separatriz")
def separatriz():
    _, resumo, _ = _dados()
    return resumo


@app.get("/grupo-p10")
def grupo_p10():
    return [item for item in _registros() if item["abaixo_percentil_10"]]


@app.get("/download/xlsx")
def download_xlsx():
    _, _, arquivos = _dados()
    return FileResponse(
        arquivos["xlsx"],
        filename="municipios_rn.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@app.get("/download/csv")
def download_csv(
    grupo: bool = Query(False, description="Se true, baixa só o grupo P10"),
):
    _, _, arquivos = _dados()
    caminho = arquivos["csv_grupo"] if grupo else arquivos["csv_todos"]
    nome = "grupo_p10_menores_pib.csv" if grupo else "municipios_rn.csv"
    return FileResponse(caminho, filename=nome, media_type="text/csv")
