# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.23.3",
#     "pandas",
#     "ortools",
# ]
# ///


import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo
    import pandas as pd
    import csv

    def ler_csv(diretorio,colunas_obrigatorias):
        with open(diretorio, newline="" , encoding="utf-8") as f:
            leitor = csv.DictReader(f)
            colunas_em_falta = set(colunas_obrigatorias) - set(leitor.fieldnames or [])

            if colunas_em_falta:
                raise ValueError(f"{diretorio} : faltam as colunas {colunas_em_falta}")
            return list(leitor)

    turmas = ler_csv("dados/turmas.csv", ["turma"])






if __name__ == "__main__":
    app.run()
