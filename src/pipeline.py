"""Monta o dataset do RN, calcula o percentil 10 e exporta CSV/XLSX."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.ibge_client import (
    consultar_agregado,
    consultar_indicador,
    consultar_indicador_opcional,
    listar_municipios_rn,
    ultimo_valor,
    valor_do_ano,
)

RAIZ = Path(__file__).resolve().parent.parent
PASTA_DADOS = RAIZ / "data"

ANO_PIB = "2023"
ANO_VAB = "2021"
ANO_CENSO = "2022"
PERCENTIL = 10


def coletar_dados() -> pd.DataFrame:
    """Busca nas APIs oficiais do IBGE os indicadores da atividade."""
    municipios = pd.DataFrame(listar_municipios_rn())

    print("Buscando PIB per capita e PIB total...")
    pib_pc = consultar_indicador(38, 47001, periodo=ANO_PIB)
    pib_total = consultar_indicador(38, 46997, periodo=ANO_PIB)
    print("Buscando valor adicionado setorial (2021)...")
    vab_agro = consultar_indicador(38, 47006, periodo=ANO_VAB)
    vab_industria = consultar_indicador(38, 47007, periodo=ANO_VAB)
    vab_servicos = consultar_indicador(38, 47008, periodo=ANO_VAB)
    vab_adm = consultar_indicador(38, 47009, periodo=ANO_VAB)

    print("Buscando Censo 2022 (população, área, densidade e alfabetização)...")
    censo = consultar_agregado(4714, "93|6318|614", ANO_CENSO)
    alfabetizacao = consultar_agregado(
        9543,
        "2513",
        ANO_CENSO,
        classificacao="2[6794]|86[95251]|287[100362]",
    )
    print("Buscando indicadores sociais complementares...")
    idhm = consultar_indicador_opcional(10111, 329756)
    escolarizacao = consultar_indicador_opcional(10058, 60045)
    salario_medio = consultar_indicador_opcional(10058, 60038)
    populacao_ocupada = consultar_indicador_opcional(10058, 60036)

    linhas: list[dict[str, Any]] = []
    for _, mun in municipios.iterrows():
        codigo7 = mun["codigo_municipio"]
        codigo6 = mun["codigo_municipio_6"]
        demo = censo.get(codigo7, {})
        alfa = alfabetizacao.get(codigo7, {})

        pib_per_capita = valor_do_ano(pib_pc.get(codigo6), ANO_PIB)
        pib = valor_do_ano(pib_total.get(codigo6), ANO_PIB)
        agro = valor_do_ano(vab_agro.get(codigo6), ANO_VAB)
        industria = valor_do_ano(vab_industria.get(codigo6), ANO_VAB)
        servicos = valor_do_ano(vab_servicos.get(codigo6), ANO_VAB)
        adm = valor_do_ano(vab_adm.get(codigo6), ANO_VAB)
        vab_total = _soma([agro, industria, servicos, adm])

        linhas.append(
            {
                "codigo_municipio": codigo7,
                "municipio": mun["municipio"],
                "uf": mun["uf"],
                "mesorregiao": mun["mesorregiao"],
                "microrregiao": mun["microrregiao"],
                "regiao_imediata": mun["regiao_imediata"],
                "regiao_intermediaria": mun["regiao_intermediaria"],
                "ano_pib": int(ANO_PIB),
                "pib_mil_reais": pib,
                "pib_per_capita": pib_per_capita,
                "populacao_censo_2022": demo.get("93"),
                "area_km2": demo.get("6318"),
                "densidade_demografica": demo.get("614"),
                "ano_vab": int(ANO_VAB),
                "vab_agropecuaria_mil_reais": agro,
                "vab_industria_mil_reais": industria,
                "vab_servicos_mil_reais": servicos,
                "vab_administracao_publica_mil_reais": adm,
                "participacao_agropecuaria_pct": _participacao(agro, vab_total),
                "participacao_industria_pct": _participacao(industria, vab_total),
                "participacao_servicos_pct": _participacao(servicos, vab_total),
                "participacao_adm_publica_pct": _participacao(adm, vab_total),
                "taxa_alfabetizacao_15_mais_pct": alfa.get("2513"),
                "idhm": ultimo_valor(idhm.get(codigo6)),
                "taxa_escolarizacao_6_a_14_pct": ultimo_valor(escolarizacao.get(codigo6)),
                "salario_medio_mensal": ultimo_valor(salario_medio.get(codigo6)),
                "populacao_ocupada": ultimo_valor(populacao_ocupada.get(codigo6)),
            }
        )

    df = pd.DataFrame(linhas)
    df = aplicar_separatriz(df)
    return df.sort_values(
        ["abaixo_percentil_10", "pib_per_capita"],
        ascending=[False, True],
        ignore_index=True,
    )


def aplicar_separatriz(df: pd.DataFrame, percentil: int = PERCENTIL) -> pd.DataFrame:
    """Calcula o percentil 10 do PIB per capita e marca o grupo inferior."""
    valores = df["pib_per_capita"].dropna().to_numpy(dtype=float)
    p10 = round(float(np.percentile(valores, percentil)), 2)
    n_dez_porcento = max(1, int(np.ceil(len(valores) * percentil / 100)))

    saida = df.copy()
    saida["percentil_10_pib_per_capita"] = p10
    saida["abaixo_percentil_10"] = saida["pib_per_capita"] < p10
    saida["ranking_pib_per_capita_asc"] = (
        saida["pib_per_capita"].rank(method="min", ascending=True).astype("Int64")
    )
    saida["entre_os_10_pct_menores"] = (
        saida["ranking_pib_per_capita_asc"] <= n_dez_porcento
    )
    return saida


def resumo_separatriz(df: pd.DataFrame) -> dict[str, Any]:
    p10 = float(df["percentil_10_pib_per_capita"].iloc[0])
    grupo = df[df["abaixo_percentil_10"]].copy()
    demais = df[~df["abaixo_percentil_10"]].copy()
    return {
        "estado": "Rio Grande do Norte",
        "ano_pib": int(ANO_PIB),
        "n_municipios": int(len(df)),
        "percentil": PERCENTIL,
        "percentil_10_pib_per_capita": p10,
        "n_municipios_abaixo_p10": int(grupo.shape[0]),
        "pib_per_capita_minimo": float(df["pib_per_capita"].min()),
        "pib_per_capita_maximo": float(df["pib_per_capita"].max()),
        "pib_per_capita_mediana_rn": float(df["pib_per_capita"].median()),
        "pib_per_capita_media_rn": float(df["pib_per_capita"].mean()),
        "pib_per_capita_media_grupo_p10": float(grupo["pib_per_capita"].mean()),
        "pib_per_capita_media_demais": float(demais["pib_per_capita"].mean()),
        "municipios_grupo_p10": grupo["municipio"].tolist(),
        "comparativo_grupo_vs_demais": _comparativo(grupo, demais),
        "descricao": descrever_situacao(df, grupo, demais, p10),
    }


def descrever_situacao(
    df: pd.DataFrame,
    grupo: pd.DataFrame,
    demais: pd.DataFrame,
    p10: float,
) -> str:
    n = len(grupo)
    nomes = ", ".join(grupo["municipio"].tolist())
    meso = grupo["mesorregiao"].value_counts().head(3).to_dict()
    meso_txt = "; ".join(f"{k} ({v})" for k, v in meso.items())

    return (
        f"O PIB per capita de 2023 dos {len(df)} municípios do Rio Grande do Norte "
        f"tem percentil 10 igual a R$ {_br(p10)}. Ficaram abaixo dessa separatriz "
        f"{n} municípios: {nomes}. "
        f"Nesse grupo, a média do PIB per capita é R$ {_br(grupo['pib_per_capita'].mean())}, "
        f"frente a R$ {_br(df['pib_per_capita'].mean())} na média estadual. "
        f"São, em geral, municípios pequenos (população média de "
        f"{_br(grupo['populacao_censo_2022'].mean(), 0)} habitantes, contra "
        f"{_br(demais['populacao_censo_2022'].mean(), 0)} nos demais) e de baixa densidade "
        f"({_br(grupo['densidade_demografica'].mean(), 1)} hab/km² contra "
        f"{_br(demais['densidade_demografica'].mean(), 1)}). "
        f"A estrutura produtiva de 2021 indica maior dependência da administração pública "
        f"({_br(grupo['participacao_adm_publica_pct'].mean(), 1)}% do VAB no grupo P10 "
        f"contra {_br(demais['participacao_adm_publica_pct'].mean(), 1)}% nos demais) e "
        f"menor peso da indústria ({_br(grupo['participacao_industria_pct'].mean(), 1)}% "
        f"contra {_br(demais['participacao_industria_pct'].mean(), 1)}%). "
        f"Há também pior desempenho educacional e de desenvolvimento humano: taxa de "
        f"alfabetização de 15 anos ou mais de "
        f"{_br(grupo['taxa_alfabetizacao_15_mais_pct'].mean(), 1)}% "
        f"(contra {_br(demais['taxa_alfabetizacao_15_mais_pct'].mean(), 1)}%) "
        f"e IDHM médio de {_br(grupo['idhm'].mean(), 3)} "
        f"(contra {_br(demais['idhm'].mean(), 3)}). "
        f"A concentração territorial do grupo está principalmente em: {meso_txt}. "
        f"Em conjunto, o recorte aponta municípios de pequeno porte, com economia pouco "
        f"diversificada, forte peso do setor público e indicadores sociais mais frágeis, "
        f"o que ajuda a explicar o PIB per capita situado no décimo inferior da distribuição estadual."
    )


def exportar(df: pd.DataFrame, resumo: dict[str, Any]) -> dict[str, Path]:
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    csv_todos = PASTA_DADOS / "municipios_rn.csv"
    csv_grupo = PASTA_DADOS / "grupo_p10_menores_pib.csv"
    xlsx = PASTA_DADOS / "municipios_rn.xlsx"
    json_resumo = PASTA_DADOS / "resumo_separatriz.json"

    grupo = df[df["abaixo_percentil_10"]].copy()
    comparativo = pd.DataFrame(resumo["comparativo_grupo_vs_demais"])
    metadados = pd.DataFrame(
        [
            {"item": "Estado", "valor": "Rio Grande do Norte"},
            {"item": "Ano do PIB per capita", "valor": ANO_PIB},
            {"item": "Ano do VAB setorial", "valor": ANO_VAB},
            {"item": "Ano do Censo (população, área, densidade, alfabetização)", "valor": ANO_CENSO},
            {"item": "Percentil", "valor": PERCENTIL},
            {
                "item": "Valor do percentil 10 (R$)",
                "valor": resumo["percentil_10_pib_per_capita"],
            },
            {"item": "Municípios abaixo do P10", "valor": resumo["n_municipios_abaixo_p10"]},
            {"item": "Total de municípios", "valor": resumo["n_municipios"]},
            {"item": "Descrição", "valor": resumo["descricao"]},
            {
                "item": "Fonte PIB",
                "valor": "IBGE Cidades@, pesquisa 38, indicador 47001 (série revisada)",
            },
            {
                "item": "Fonte demografia",
                "valor": "IBGE Agregados, tabela 4714 (Censo 2022)",
            },
            {
                "item": "Fonte alfabetização",
                "valor": "IBGE Agregados, tabela 9543 (Censo 2022)",
            },
            {
                "item": "Fonte VAB",
                "valor": "IBGE Cidades@, pesquisa 38, indicadores 47006 a 47009 (2021)",
            },
            {
                "item": "Portal de referência",
                "valor": "https://cidades.ibge.gov.br/brasil/rn/panorama",
            },
        ]
    )

    df.to_csv(csv_todos, index=False, encoding="utf-8-sig")
    grupo.to_csv(csv_grupo, index=False, encoding="utf-8-sig")
    json_resumo.write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Todos_municipios", index=False)
        grupo.to_excel(writer, sheet_name="Grupo_P10", index=False)
        comparativo.to_excel(writer, sheet_name="Comparativo", index=False)
        metadados.to_excel(writer, sheet_name="Resumo", index=False)

    return {
        "csv_todos": csv_todos,
        "csv_grupo": csv_grupo,
        "xlsx": xlsx,
        "resumo": json_resumo,
    }


def executar() -> tuple[pd.DataFrame, dict[str, Any], dict[str, Path]]:
    df = coletar_dados()
    resumo = resumo_separatriz(df)
    arquivos = exportar(df, resumo)
    return df, resumo, arquivos


def _soma(valores: list[float | None]) -> float | None:
    nums = [v for v in valores if v is not None]
    if not nums:
        return None
    return float(sum(nums))


def _participacao(parte: float | None, total: float | None) -> float | None:
    if parte is None or not total:
        return None
    return 100.0 * parte / total


def _comparativo(grupo: pd.DataFrame, demais: pd.DataFrame) -> list[dict[str, Any]]:
    colunas = [
        ("pib_per_capita", "PIB per capita (R$)"),
        ("pib_mil_reais", "PIB (R$ mil)"),
        ("populacao_censo_2022", "População (Censo 2022)"),
        ("densidade_demografica", "Densidade (hab/km²)"),
        ("area_km2", "Área (km²)"),
        ("participacao_agropecuaria_pct", "Participação agropecuária no VAB (%)"),
        ("participacao_industria_pct", "Participação indústria no VAB (%)"),
        ("participacao_servicos_pct", "Participação serviços no VAB (%)"),
        ("participacao_adm_publica_pct", "Participação administração pública no VAB (%)"),
        ("taxa_alfabetizacao_15_mais_pct", "Taxa de alfabetização 15 anos ou mais (%)"),
        ("idhm", "IDHM"),
        ("taxa_escolarizacao_6_a_14_pct", "Taxa de escolarização 6 a 14 anos (%)"),
        ("salario_medio_mensal", "Salário médio mensal"),
        ("populacao_ocupada", "População ocupada"),
    ]
    linhas = []
    for coluna, rotulo in colunas:
        linhas.append(
            {
                "variavel": rotulo,
                "media_grupo_p10": _media(grupo[coluna]),
                "media_demais_municipios": _media(demais[coluna]),
                "mediana_grupo_p10": _mediana(grupo[coluna]),
                "mediana_demais_municipios": _mediana(demais[coluna]),
            }
        )
    return linhas


def _br(valor: float, casas: int = 2) -> str:
    texto = f"{float(valor):,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _media(serie: pd.Series) -> float | None:
    valores = pd.to_numeric(serie, errors="coerce").dropna()
    if valores.empty:
        return None
    return float(valores.mean())


def _mediana(serie: pd.Series) -> float | None:
    valores = pd.to_numeric(serie, errors="coerce").dropna()
    if valores.empty:
        return None
    return float(valores.median())
