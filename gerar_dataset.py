"""Gera o dataset CSV/XLSX da atividade de separatrizes do RN."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.pipeline import executar


def main() -> None:
    df, resumo, arquivos = executar()
    print(f"Municipios do RN: {resumo['n_municipios']}")
    print(f"Ano do PIB: {resumo['ano_pib']}")
    print(f"Percentil 10 (R$): {resumo['percentil_10_pib_per_capita']:.2f}")
    print(f"Municipios abaixo do P10: {resumo['n_municipios_abaixo_p10']}")
    print("Grupo P10:")
    for nome in resumo["municipios_grupo_p10"]:
        print(f" - {nome}")
    print()
    print("Arquivos gerados:")
    for tipo, caminho in arquivos.items():
        print(f" - {tipo}: {caminho}")
    print()
    print(resumo["descricao"])


if __name__ == "__main__":
    main()
