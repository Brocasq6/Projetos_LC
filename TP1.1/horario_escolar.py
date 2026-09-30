# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "marimo>=0.23.3",
#     "pandas",
#     "ortools",
# ]
# ///

import marimo
import marimo as mo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # 1. Descrição do problema e abordagem

    O objetivo deste trabalho é construir um gerador de horários semanais
    para as turmas descritas nos ficheiros CSV. Cada disciplina tem uma
    carga semanal e um professor associado; algumas disciplinas exigem
    uma sala especial ou têm de ser lecionadas em blocos de dois tempos.
    O horário tem de respeitar simultaneamente as disponibilidades dos
    professores, a capacidade das salas e as regras de não sobreposição.

    Para resolver o problema, vamos usar programação por restrições com
    CP-SAT do OR-Tools. Esta abordagem permite representar cada possível
    colocação de uma aula como uma decisão booleana e traduzir as regras
    do enunciado em restrições do modelo. O solver procurará uma solução
    que satisfaça todas as regras obrigatórias e, entre as soluções
    possíveis, minimizará os tempos livres entre aulas de cada professor
    no mesmo dia (os «buracos»).

    Os dados serão sempre lidos dos CSV. Assim, o modelo não dependerá
    dos valores específicos do exemplo e poderá ser executado com outros
    conjuntos de turmas, disciplinas, salas e indisponibilidades no mesmo
    formato. Mais adiante, o notebook também comparará uma resolução
    completa com uma atualização de horário que parte de uma solução
    anterior quando os recursos mudam.
    """
    )
    return


@app.cell
def _(csv):
    def ler_csv(diretorio,colunas_obrigatorias):
        with open(diretorio, newline="" , encoding="utf-8") as f:
            leitor = csv.DictReader(f)
            colunas_em_falta = set(colunas_obrigatorias) - set(leitor.fieldnames or [])

            if colunas_em_falta:
                raise ValueError(f"{diretorio} : faltam as colunas {colunas_em_falta}")
            return list(leitor)
    return (ler_csv,)


@app.cell
def _(ler_csv):
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
    return


@app.cell(hide_code=True)
def _(mo):
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    Prompt no CHATGPT: "vamos prosseguir. da-me as bases para a construcao da funcao preparar dados"

    Resposta do LLM: A função `preparar_dados` será a etapa entre **ler os CSV** e **construir o modelo do horário**. `ler_csv` devolve valores como texto; `preparar_dados` converte-os para os tipos adequados e deteta dados inválidos. Ainda não cria o horário.

    Como `carregar_dados` devolve quatro valores, a nova função pode recebê-los assim:
    ```python
    def preparar_dados(turmas, disciplinas, salas, excecoes):
        ...
    ```
    """
    )
    return


@app.function
def preparar_dados(dados):
    linhas_turmas, linhas_disciplinas, linhas_salas, linhas_excecoes = dados

    turmas = [linha["turma"].strip() for linha in linhas_turmas]

    if not turmas or any(not turma for turma in turmas):
        raise ValueError("Há turmas sem nome")
    if len(turmas) != len(set(turmas)):
        raise ValueError("Há turmas repetidas")

    salas = []
    for linha in linhas_salas:
        sala = {
            "sala": linha["sala"].strip(),
            "tipo": linha["tipo"].strip().lower(),
            "quantidade": int(linha["quantidade"]),
        }
        if sala["tipo"] not in {"normal", "especial"}:
            raise ValueError(f"Tipo de sala inválido: {sala['tipo']}")
        if sala["quantidade"] < 1:
            raise ValueError(f"Quantidade inválida para a sala {sala['sala']}")
        salas.append(sala)
        if not sala["sala"]:
            raise ValueError("Há salas sem nome")
        

    salas_especiais = {
        sala["sala"] for sala in salas if sala["tipo"] == "especial"
    }

    disciplinas = []
    for linha in linhas_disciplinas:
        duplo = linha["duplo_periodo"].strip().lower()
        carga = int(linha["carga_semanal"])
        sala_especial = linha["sala_especial"].strip()
        nome_disciplina = linha["disciplina"].strip()
        professor = linha["professor"].strip()

        if not nome_disciplina:
            raise ValueError("Há disciplinas sem nome")
        if not professor:
            raise ValueError(f"Falta o professor da disciplina {nome_disciplina}")

        if duplo not in {"sim", "nao"}:
            raise ValueError(
                f"Valor inválido em duplo_periodo: {linha['duplo_periodo']}"
            )
        if carga < 1 or (duplo == "sim" and carga % 2 != 0): 
            #se carga é dupla, erro se o resto a dividir por 2 =! 0
            raise ValueError(
                f"Carga semanal inválida para {linha['disciplina']}"
            )
        if sala_especial and sala_especial not in salas_especiais:
            raise ValueError(f"Sala especial inexistente: {sala_especial}")

        disciplinas.append({
            "disciplina": nome_disciplina,
            "professor": professor,
            "carga_semanal": carga,
            "duplo_periodo": duplo == "sim",
            "sala_especial": sala_especial or None,
        })

    dias_validos = {"Seg", "Ter", "Qua", "Qui", "Sex"}
    professores = {disciplina["professor"] for disciplina in disciplinas}

    excecoes = []
    for linha in linhas_excecoes:
        professor = linha["professor"].strip()
        dia = linha["dia"].strip()
        periodo = int(linha["periodo"])

        if professor not in professores:
            raise ValueError(f"Professor desconhecido na exceção: {professor}")
        if dia not in dias_validos or periodo not in range(1, 6):
            raise ValueError(f"Dia ou período inválido: {dia}, {periodo}")

        excecoes.append({
            "professor": professor,
            "dia": dia,
            "periodo": periodo,
        })

    return turmas, disciplinas, salas, excecoes

@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
Prompt no ChatGPT: muito bem. vamos prosseguir para a 
proxima funcao do plano que foi elaborado para a resolucao deste TP1.1
Resposta do LLM: A próxima função do plano é criar_tempos(). Ela prepara a lista de todos os tempos possíveis da semana, que depois o modelo usará para decidir onde colocar cada aula.
O trabalho define cinco dias (Seg a Sex) e cinco períodos por dia. A função deve devolver 25 pares, cada um com um dia e um período. Por exemplo, o primeiro par seria ("Seg", 1) e o último, ("Sex", 5).
Para a primeira versão, pensa em dois ciclos encadeados: para cada dia, percorres os cinco períodos e acrescentas o par (dia, periodo) a uma lista. É parecido com ciclos for dentro de ciclos em C ou Java.
Usa uma lista ordenada de dias para que os tempos fiquem sempre na mesma ordem.
        """
    )
    return


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
