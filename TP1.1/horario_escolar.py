# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.23.3",
#     "pandas",
#     "ortools",
# ]
# ///

import marimo

__generated_with = "0.16.5"
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

    # Carrega e devolve os dados das turmas, disciplinas, salas e disponibilidades.
    def carregar_dados(pasta):
        turmas = ler_csv(f"{pasta}/turmas.csv", ["turma"])

        disciplinas = ler_csv(
            f"{pasta}/disciplinas.csv",
            [
                "disciplina",
                "professor",
                "carga_semanal",
                "duplo_periodo",
                "sala_especial",
            ],
        )

        salas = ler_csv(
            f"{pasta}/salas.csv",
            [
                "sala", 
                "tipo", 
                "quantidade"
            ],
        )

        excecoes = ler_csv(
            f"{pasta}/disponibilidade_excecoes.csv",
            [
                "professor", 
                "dia", 
                "periodo"
            ],
        )

        return turmas, disciplinas, salas, excecoes


@app.cell(hide_code=True)
def _():
    mo.md(
        r"""
    ## Declaração de uso de LLMs

    **Prompt (ChatGPT):**

    > Explica-me os passos que precisamos para chegar ao produto final, e explica o que cada função que vai ser desenvolvida tem de fazer.

    **Resposta do LLM:**

    ---

    ### 1. Carregar os dados

    Já têm `ler_csv`. Essa função abre um CSV, verifica se contém as colunas necessárias e devolve as linhas como uma lista de dicionários.

    A seguir, uma função de carregamento pode reunir os quatro ficheiros:

    ```python
    def carregar_dados(pasta):
        ...
    ```

    Deve ler `turmas.csv`, `disciplinas.csv`, `salas.csv` e `disponibilidade_excecoes.csv` da pasta indicada e devolver os dados agrupados. Assim, a mesma função pode carregar tanto `dados/` como `dados_v2/`.

    ### 2. Limpar e validar os dados

    Os valores lidos de um CSV são texto. Por isso, será preciso preparar os dados para os cálculos e detetar erros antes de tentar gerar um horário.

    ```python
    def preparar_dados(dados):
        ...
    ```

    Esta função pode converter `carga_semanal`, `quantidade` e `periodo` em números; converter `sim`/`nao` em valores booleanos; e verificar, por exemplo, se os dias e períodos são válidos e se as salas especiais pedidas existem.

    ### 3. Definir os tempos possíveis

    O trabalho usa cinco dias e cinco períodos por dia. Uma pequena função pode representar cada tempo como um par `(dia, período)`:

    ```python
    def criar_tempos():
        ...
    ```

    A função devolve todas as combinações possíveis, por exemplo, `("Seg", 1)`, `("Seg", 2)` … até `("Sex", 5)`. Ter essa lista facilita criar as opções de horário para cada aula.

    ### 4. Criar o modelo do horário

    Com os dados preparados, o programa precisa de criar uma variável de decisão para cada combinação relevante de turma, disciplina e tempo. Essa variável representa uma pergunta: «Esta aula fica neste período?»

    ```python
    def criar_modelo(dados):
        ...
    ```

    Esta função cria o modelo CP-SAT, as variáveis de decisão e as restrições obrigatórias. A separação exata depende da forma como decidirem representar as aulas. O importante é que o modelo consiga expressar as regras do enunciado.

    ### 5. Acrescentar as restrições

    Para manter o código compreensível, podem criar funções que acrescentam grupos de regras ao modelo:

    ```python
    def adicionar_restricoes_turmas(modelo, variaveis, dados):
        ...
    ```

    Impede que uma turma tenha duas aulas ao mesmo tempo e garante que cada disciplina cumpre a sua carga semanal.

    ```python
    def adicionar_restricoes_professores(modelo, variaveis, dados):
        ...
    ```

    Impede conflitos entre aulas do mesmo professor e bloqueia os períodos em que esse professor está indisponível.

    ```python
    def adicionar_restricoes_salas(modelo, variaveis, dados):
        ...
    ```

    Garante que cada aula usa uma sala compatível e que não são usadas mais salas do mesmo tipo do que as disponíveis.

    ```python
    def adicionar_restricoes_diarias(modelo, variaveis, dados):
        ...
    ```

    Limita a uma ocorrência diária cada disciplina por turma e trata as disciplinas de duplo período como blocos de dois tempos consecutivos no mesmo dia.

    Estas funções devem traduzir os requisitos do enunciado para o modelo. A forma concreta dependerá das variáveis que escolherem; por exemplo, representar cada aula individualmente ou representar blocos duplos como uma opção própria.

    ### 6. Otimizar e resolver

    Depois das restrições, acrescentam o objetivo de reduzir os «buracos» dos professores — tempos livres entre a primeira e a última aula num dia.

    ```python
    def adicionar_objetivo_buracos(modelo, variaveis, dados):
        ...
    ```

    Depois, uma função executa o solver:

    ```python
    def resolver_modelo(modelo, limite_segundos=None):
        ...
    ```

    Deve correr o CP-SAT, respeitar um eventual limite de tempo e devolver o estado da resolução e os valores das variáveis. O estado é importante: pode haver solução ótima, solução válida ainda não provada ótima, ou nenhuma solução encontrada.

    ### 7. Transformar a solução num horário legível

    Os valores das variáveis do solver não são ainda uma apresentação amigável. Uma função pode convertê-los numa lista organizada de aulas:

    ```python
    def extrair_horario(solver, variaveis, dados):
        ...
    ```

    Cada aula deve indicar pelo menos a turma, disciplina, professor, dia, período e sala. Depois, outra função pode mostrar o resultado numa tabela:

    ```python
    def apresentar_horario(horario):
        ...
    ```

    No Marimo, podem apresentar uma tabela por turma ou organizar os dias e períodos em grelhas.

    ### 8. Verificar o horário

    Mesmo que o solver use as restrições, o trabalho pede verificações automáticas para confirmar que o horário final respeita as regras.

    ```python
    def validar_horario(horario, dados):
        ...
    ```

    Deve percorrer o horário produzido e verificar cargas semanais, conflitos de turma e professor, disponibilidade, salas e blocos duplos. Pode devolver uma lista de erros; se estiver tudo correto, a lista fica vazia.

    ### 9. Atualizar o horário quando os dados mudam

    Para a parte incremental, será precisa uma função que compare dois horários:

    ```python
    def contar_alteracoes(horario_antigo, horario_novo):
        ...
    ```

    Deve contar quantas aulas mudaram de período ou sala entre H0 e H1. Para comparar corretamente, cada ocorrência de aula precisa de ter uma identificação estável — por exemplo, turma, disciplina e número da ocorrência naquela semana.

    A função de atualização incremental pode receber o horário anterior e os novos dados:

    ```python
    def atualizar_horario(horario_antigo, dados_novos):
        ...
    ```

    Deve gerar um novo horário que respeite os dados novos e, ao mesmo tempo, tente preservar as aulas que ainda podem ficar nos mesmos tempos e salas. Depois, comparem o resultado com uma resolução dos mesmos dados começada do zero. Registem o tempo e o número de alterações para apresentar a evidência pedida no enunciado.
    """
    )
    return


app._unparsable_cell(
    r"""
    def preparar_dados(dados):
    

    """,
    name="_"
)


app._unparsable_cell(
    r"""
    def criar_tempos():
    

    """,
    name="_"
)


app._unparsable_cell(
    r"""
    def criar_modelos():
    """,
    name="_"
)


@app.function
def adicionar_restricoes_turmas(modelo, variaveis, dados):
    ...


@app.function
def adicionar_restricoes_professores(modelo, variaveis, dados):
    ...


@app.function
def adicionar_restricoes_salas(modelo, variaveis, dados):
    ...


@app.function
def adicionar_restricoes_diarias(modelo, variaveis, dados):
    ...


@app.function
def adicionar_objetivo_buracos(modelo, variaveis, dados):
    ...


@app.function
def resolver_modelo(modelo, limite_segundos=None):
    ...


@app.function
def extrair_horario(solver, variaveis, dados):
    ...


@app.function
def apresentar_horario(horario):
    ...


@app.function
def validar_horario(horario, dados):
    ...


@app.function
def contar_alteracoes(horario_antigo, horario_novo):
    ...


@app.function
def atualizar_horario(horario_antigo, dados_novos):
    ...


if __name__ == "__main__":
    app.run()
