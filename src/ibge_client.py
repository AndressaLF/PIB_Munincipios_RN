"""Cliente HTTP simples para as APIs oficiais do IBGE."""

from __future__ import annotations

import gzip
import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

IBGE_PESQUISAS = "https://servicodados.ibge.gov.br/api/v1/pesquisas"
IBGE_LOCALIDADES = "https://servicodados.ibge.gov.br/api/v1/localidades"
IBGE_AGREGADOS = "https://servicodados.ibge.gov.br/api/v3/agregados"

CODIGO_RN = "24"
LOCALIDADES_MUNICIPIOS_RN = "N6[N3[24]]"


class IbgeErro(RuntimeError):
    """Falha ao consultar uma API do IBGE."""


def _get_json(url: str, tentativas: int = 4, timeout: int = 120) -> Any:
    ultimo_erro: Exception | None = None
    for i in range(tentativas):
        try:
            req = Request(
                url,
                headers={
                    "User-Agent": "API-IBGE-RN/1.0 (atividade academica)",
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                },
            )
            with urlopen(req, timeout=timeout) as resposta:
                bruto = resposta.read()
                if (
                    resposta.headers.get("Content-Encoding") == "gzip"
                    or bruto[:2] == b"\x1f\x8b"
                ):
                    bruto = gzip.decompress(bruto)
                return json.loads(bruto.decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            ultimo_erro = exc
            time.sleep(1.5 * (i + 1))
    raise IbgeErro(f"Falha ao consultar {url}: {ultimo_erro}") from ultimo_erro


def listar_municipios_rn() -> list[dict[str, Any]]:
    """Lista os 167 municípios do Rio Grande do Norte com recortes territoriais."""
    url = f"{IBGE_LOCALIDADES}/estados/{CODIGO_RN}/municipios?orderBy=nome"
    bruto = _get_json(url)
    municipios: list[dict[str, Any]] = []
    for item in bruto:
        micro = item.get("microrregiao") or {}
        meso = micro.get("mesorregiao") or {}
        imediata = item.get("regiao-imediata") or {}
        intermediaria = imediata.get("regiao-intermediaria") or {}
        codigo = str(item["id"])
        municipios.append(
            {
                "codigo_municipio": codigo,
                "codigo_municipio_6": codigo[:6],
                "municipio": item["nome"],
                "uf": "RN",
                "microrregiao": micro.get("nome"),
                "mesorregiao": meso.get("nome"),
                "regiao_imediata": imediata.get("nome"),
                "regiao_intermediaria": intermediaria.get("nome"),
            }
        )
    return municipios


def consultar_indicador(
    pesquisa: int,
    indicador: int,
    periodo: str | None = None,
    localidades: str = LOCALIDADES_MUNICIPIOS_RN,
    tentativas: int = 4,
) -> dict[str, dict[str, float | None]]:
    """
    Consulta a API de Pesquisas (Cidades@).

    Retorna {codigo_6: {ano: valor}}.
    """
    local = quote(localidades, safe="[]")
    if periodo:
        url = (
            f"{IBGE_PESQUISAS}/{pesquisa}/periodos/{periodo}"
            f"/indicadores/{indicador}/resultados/{local}"
        )
    else:
        url = (
            f"{IBGE_PESQUISAS}/{pesquisa}"
            f"/indicadores/{indicador}/resultados/{local}"
        )
    dados = _get_json(url, tentativas=tentativas)
    saida: dict[str, dict[str, float | None]] = {}
    for bloco in dados:
        for registro in bloco.get("res", []):
            codigo = str(registro["localidade"])
            serie: dict[str, float | None] = {}
            for ano, valor in (registro.get("res") or {}).items():
                serie[str(ano)] = _para_numero(valor)
            saida[codigo] = serie
    return saida


def consultar_indicador_opcional(
    pesquisa: int,
    indicador: int,
    periodo: str | None = None,
    localidades: str = LOCALIDADES_MUNICIPIOS_RN,
) -> dict[str, dict[str, float | None]]:
    """Igual a consultar_indicador, mas devolve vazio se a API falhar."""
    try:
        return consultar_indicador(
            pesquisa, indicador, periodo, localidades, tentativas=2
        )
    except IbgeErro as exc:
        print(f"Indicador opcional {pesquisa}/{indicador} indisponivel: {exc}")
        return {}


def consultar_agregado(
    agregado: int,
    variaveis: str,
    periodo: str,
    localidades: str = LOCALIDADES_MUNICIPIOS_RN,
    classificacao: str | None = None,
) -> dict[str, dict[str, float | None]]:
    """
    Consulta a API de Agregados (SIDRA).

    Retorna {codigo_7: {id_variavel: valor}}.
    """
    local = quote(localidades, safe="[]")
    url = (
        f"{IBGE_AGREGADOS}/{agregado}/periodos/{periodo}"
        f"/variaveis/{variaveis}?localidades={local}"
    )
    if classificacao:
        url += f"&classificacao={quote(classificacao, safe='[]|,')}"
    dados = _get_json(url)
    saida: dict[str, dict[str, float | None]] = {}
    for variavel in dados:
        vid = str(variavel["id"])
        for resultado in variavel.get("resultados", []):
            for serie in resultado.get("series", []):
                codigo = str(serie["localidade"]["id"])
                valores = serie.get("serie") or {}
                valor = next(iter(valores.values()), None)
                saida.setdefault(codigo, {})[vid] = _para_numero(valor)
    return saida


def ultimo_valor(serie: dict[str, float | None] | None) -> float | None:
    """Devolve o valor mais recente não nulo de uma série anual."""
    if not serie:
        return None
    for ano in sorted(serie.keys(), reverse=True):
        if serie[ano] is not None:
            return serie[ano]
    return None


def valor_do_ano(serie: dict[str, float | None] | None, ano: str) -> float | None:
    if not serie:
        return None
    return serie.get(ano)


def _para_numero(valor: Any) -> float | None:
    if valor is None or valor in ("", "-", "...", "X"):
        return None
    try:
        return float(str(valor).replace(",", "."))
    except (TypeError, ValueError):
        return None
