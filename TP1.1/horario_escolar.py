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
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    from ortools.sat.python import cp_model
    return (cp_model,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # 1. Descrição do problema e abordagem

    > **Objetivo** — construir um gerador de horários semanais a partir dos
    > ficheiros CSV, respeitando as regras das turmas, disciplinas, professores
    > e salas.

    ## Regras principais

    - Cada disciplina tem uma carga semanal e um professor associado.
    - Algumas disciplinas precisam de uma sala especial ou de blocos de dois
      períodos consecutivos.
    - Uma turma, um professor ou uma sala não podem ter aulas sobrepostas.
    - As indisponibilidades dos professores e a capacidade das salas têm de ser
      respeitadas.

    ## Estratégia de resolução

    Usaremos programação por restrições com **CP-SAT**, do OR-Tools. Cada
    colocação possível de uma aula será representada por uma decisão booleana.
    O solver procurará primeiro uma solução que cumpra todas as regras
    obrigatórias e, depois, minimizará os tempos livres entre aulas de cada
    professor no mesmo dia (os «buracos»).

    Os dados serão sempre lidos dos CSV, pelo que o modelo poderá ser usado com
    outros conjuntos de turmas, disciplinas, salas e indisponibilidades no mesmo
    formato. No final, o notebook também comparará uma resolução completa com
    uma atualização de horário baseada numa solução anterior.
    """
    )
    return


@app.cell
def _():
    import csv
    return (csv,)


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
    return (carregar_dados,)


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
    def adicionar_restricoes_turmas(modelo, x, dados):
        ...
    ```

    Impede que uma turma tenha duas aulas ao mesmo tempo e garante que cada disciplina cumpre a sua carga semanal.

    ```python
    def adicionar_restricoes_professores(modelo, x, dados):
        ...
    ```

    Impede conflitos entre aulas do mesmo professor e bloqueia os períodos em que esse professor está indisponível.

    ```python
    def adicionar_restricoes_salas(modelo, x, dados):
        ...
    ```

    Garante que cada aula usa uma sala compatível e que não são usadas mais salas do mesmo tipo do que as disponíveis.

    ```python
    def adicionar_restricoes_diarias(modelo, x, dados):
        ...
    ```

    Limita a uma ocorrência diária cada disciplina por turma e trata as disciplinas de duplo período como blocos de dois tempos consecutivos no mesmo dia.

    Estas funções devem traduzir os requisitos do enunciado para o modelo. A forma concreta dependerá das variáveis que escolherem; por exemplo, representar cada aula individualmente ou representar blocos duplos como uma opção própria.

    ### 6. Otimizar e resolver

    Depois das restrições, acrescentam o objetivo de reduzir os «buracos» dos professores — tempos livres entre a primeira e a última aula num dia.

    ```python
    def adicionar_objetivo_buracos(modelo, x, dados):
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
    def extrair_horario(solver, x, dados):
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
    ### Registo de apoio — `preparar_dados`

    **Prompt**

    > Vamos prosseguir. Dá-me as bases para a construção da função `preparar_dados`.

    **Resposta**

    A função `preparar_dados` será a etapa entre **ler os CSV** e **construir o
    modelo do horário**. `ler_csv` devolve valores como texto;
    `preparar_dados` converte-os para os tipos adequados e deteta dados
    inválidos. Ainda não cria o horário.

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
    ### Registo de apoio — `criar_tempos`

    **Prompt**

    > Muito bem. Vamos prosseguir para a próxima função do plano elaborado para
    > resolver este TP1.1.

    **Resposta**

    A próxima função do plano é `criar_tempos()`. Ela prepara a lista de todos
    os tempos possíveis da semana, que depois o modelo usará para decidir onde
    colocar cada aula.
    O trabalho define **cinco dias e cinco períodos por dia**. A função deve
    devolver 25 pares `(dia, período)`, desde `("Seg", 1)` até `("Sex", 5)`.

    Para construir a lista, percorremos os dias por uma ordem fixa e, para cada
    dia, percorremos os períodos de 1 a 5. Assim, os tempos ficam sempre
    organizados da mesma forma.
    """
    )
    return


@app.function
def criar_tempos():
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex"]
    tempos = []

    for dia in dias:
        for periodo in range(1, 6):
            tempos.append((dia, periodo))

    return tempos


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Registo de apoio — `criar_modelo`

    **Prompt**

    > Ok, vamos então à próxima.

    **Resposta**

    A próxima função do plano é `criar_modelo`. Antes de a escrevermos,
    precisamos de decidir o que representa uma variável de decisão no modelo
    CP-SAT.

    Uma opção que trata naturalmente as aulas duplas é criar uma variável booleana para cada **possível colocação de uma aula**:

    - `False` significa que a aula não começa nesse dia e período.
    - `True` significa que começa aí.
    - Para uma aula simples, qualquer período pode ser início.
    - Para uma aula dupla, só os períodos 1 a 4 podem ser início, porque tem de haver um período seguinte.

    Por exemplo, uma variável para Matemática da turma 7.º A, à terça-feira no
    período 2, representa essa colocação. Pode chamar-se
    `x_7A_Matematica_Ter_2`.

    A função terá este papel:
    ```python
    def criar_modelo(dados, tempos):
    ...
    return modelo, x
    ```

    Deve criar o modelo CP-SAT e as variáveis de decisão. As regras — como
    impedir conflitos de professores e cumprir as cargas semanais — ficam para
    as funções de restrições.

    **Aulas duplas:** uma variável ocupa dois períodos, apesar de representar
    uma única colocação. As restrições terão de considerar o período de início
    e o período seguinte.
    """
    )
    return

@app.cell
def _(cp_model):
    def criar_modelo(dados, tempos):
        turmas, disciplinas, _, _ = dados
        modelo = cp_model.CpModel()
        x = {}

        for i_turma, turma in enumerate(turmas):
            x[turma] = {}

            for i_disciplina, disciplina in enumerate(disciplinas):
                nome = disciplina["disciplina"]
                x[turma][nome] = {}

                for dia, periodo in tempos:
                    if dia not in x[turma][nome]:
                        x[turma][nome][dia] = {}

                    if disciplina["duplo_periodo"] and periodo == 5:
                        continue

                    nome_variavel = f"x_{i_turma}_{i_disciplina}_{dia}_{periodo}"
                    x[turma][nome][dia][periodo] = modelo.NewBoolVar(nome_variavel)

        return modelo, x
    return (criar_modelo,)

@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Registo de apoio — restrições das turmas

    **Prompt**

    > Agora que finalizámos estas funções, vamos começar a tratar das
    > restrições, começando pelas restrições das turmas.

    **Resposta**

    As restrições das turmas cobrem duas regras do enunciado:

    - **R1:** uma turma não pode ter duas aulas ao mesmo tempo.
    - **R2:** cada disciplina tem de cumprir a carga semanal daquela turma.

    A regra **R3** (no máximo uma ocorrência diária da mesma disciplina por
    turma) fica na função `adicionar_restricoes_diarias`.

    ## Representação das aulas

    Cada variável booleana representa uma possível colocação de uma aula. Ela
    fica organizada em quatro níveis:

    ```text
    x[turma][disciplina][dia][período_de_início]
    ```

    Por exemplo, `x["7ºA"]["Matemática"]["Ter"][2]` representa a opção de
    Matemática do 7.º A começar à terça-feira no período 2. `True` quer dizer
    que essa colocação foi escolhida; `False`, que não foi escolhida. Uma aula
    dupla ocupa o período de início e o seguinte.

    A função para acrescentar estas regras ao modelo será:

    ```python
    def adicionar_restricoes_turmas(modelo, x, dados):
        ...
    ```

    ## Começar por R2: carga semanal

    Para cada turma e disciplina, somamos as variáveis de todas as colocações
    possíveis. Uma aula simples conta como 1 período; uma dupla conta como 2.
    Essa soma tem de ser igual à `carga_semanal`.

    ```text
    soma(colocações escolhidas × duração da aula) = carga semanal
    ```

    Por exemplo, Matemática com carga semanal 4 precisa de quatro aulas
    simples; Educação Física com carga 2 e duplo período precisa de um bloco
    duplo.
    """
    )
    return

@app.function
def adicionar_restricoes_turmas(modelo, x, dados):
    turmas, disciplinas, _, _ = dados
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex"]

    # Cada disciplina tem de cumprir a carga semanal em cada turma.
    for turma in turmas:
        for disciplina in disciplinas:
            nome = disciplina["disciplina"]
            colocacoes = []

            for dia in dias:
                for periodo in range(1, 6):
                    if periodo in x[turma][nome][dia]:
                        colocacoes.append(x[turma][nome][dia][periodo])

            sessoes_necessarias = disciplina["carga_semanal"]
            if disciplina["duplo_periodo"]:
                sessoes_necessarias //= 2
                # O operador //= divide e guarda o resultado na mesma variável.

            modelo.Add(sum(colocacoes) == sessoes_necessarias)

    # Uma turma só pode ter uma aula a decorrer em cada período.
    for turma in turmas:
        for dia in dias:
            for periodo in range(1, 6):
                aulas_a_decorrer = []

                for disciplina in disciplinas:
                    nome = disciplina["disciplina"]

                    if periodo in x[turma][nome][dia]:
                        aulas_a_decorrer.append(x[turma][nome][dia][periodo])

                    if disciplina["duplo_periodo"] and periodo > 1:
                        inicio_anterior = periodo - 1
                        if inicio_anterior in x[turma][nome][dia]:
                            aulas_a_decorrer.append(
                                x[turma][nome][dia][inicio_anterior]
                            )

                modelo.Add(sum(aulas_a_decorrer) <= 1)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Registo de apoio — restantes restrições

    **Prompt (16:10)**

    > Ok, guia-me agora no resto das funções de restrições.

    **Resposta do ChatGPT**

    Vamos organizar as restrições por recurso. Usaremos esta convenção para `x`:

    ```text
    x[turma][disciplina][dia][período_de_início]
    ```

    Cada entrada é uma decisão do solver: a aula começa nesse período ou não.
    Para uma aula dupla, só criamos opções de início nos períodos 1 a 4; se
    começar no período 3, ocupa os períodos 3 e 4. Isso faz parte da forma de
    construir `x` e já ajuda a cumprir R4.

    Cada função de restrições recebe o mesmo modelo, `x` e os dados preparados.
    Dentro dela, `modelo.Add(...)` acrescenta condições que o horário tem de
    respeitar.

    #### Restrições das turmas

    A função `adicionar_restricoes_turmas(modelo, x, dados)` trata três regras:

    - **R2 — carga semanal:** para cada turma e disciplina, somar as aulas
      escolhidas. Aulas simples contam 1 período e duplas contam 2. A soma tem
      de ser igual à carga semanal.
    - **R3 — no máximo uma ocorrência diária:** para cada turma, disciplina e
      dia, a soma das opções escolhidas nesse dia tem de ser no máximo 1.
    - **R1 — sem conflitos na turma:** para cada turma, dia e período, somar as
      aulas que ocupam esse período. O resultado tem de ser no máximo 1. Para
      uma aula dupla, conta tanto no início como no período seguinte.

    **R4** fica garantida se `x` só tiver opções de início válidas para aulas
    duplas e essas aulas ocuparem sempre dois períodos consecutivos.

    #### Restrições dos professores

    A função `adicionar_restricoes_professores(modelo, x, dados)` trata:

    - **R5 — sem conflitos:** em cada dia e período, somar as aulas que ocupam
      esse período e pertencem ao mesmo professor. O total tem de ser no máximo
      1.
    - **R6 — disponibilidade:** se uma aula calhar num período em que o
      professor não está disponível, essa opção de `x` tem de ser proibida.
      Para uma aula dupla, verifica-se também o período seguinte.

    #### Restrições das salas

    A função `adicionar_restricoes_salas(modelo, x, dados)` trata a capacidade
    e a compatibilidade das salas:

    - Em cada dia e período, conta as aulas que precisam de cada recurso.
    - O total não pode ultrapassar a quantidade disponível em `salas.csv`.
    - Aulas sem sala especial usam a capacidade normal; aulas com uma sala
      especial só contam para essa sala, como Laboratório ou Ginásio.

    Se quiserem apresentar o nome exato da sala em cada aula, terão de decidir
    como atribuí-lo depois. Se as salas de um tipo forem equivalentes, podem
    primeiro garantir a capacidade com estas contagens.

    **R8** não é uma restrição do solver: cumpre-se carregando os dados dos
    CSV, como já fizeram.

    A ordem de implementação pode ser: carga semanal (R2), limite diário (R3),
    conflitos das turmas (R1), conflitos e disponibilidade dos professores
    (R5–R6), e capacidade das salas (R7). Antes de programarmos a primeira
    função, precisamos de ter `x` construído com essa convenção.

    **Nota sobre a implementação atual:** R3 está separada na função
    `adicionar_restricoes_diarias`; a função das turmas implementa R1 e R2.

    """
    )
    return


@app.function
def adicionar_restricoes_professores(modelo, x, dados):
    turmas, disciplinas, _, excecoes = dados
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex"]

    # Guardamos as indisponibilidades para poder consultá-las rapidamente.
    indisponibilidades = {
        (excecao["professor"], excecao["dia"], excecao["periodo"])
        for excecao in excecoes
    }

    # Um professor não pode estar em duas turmas no mesmo período.
    for professor in {disciplina["professor"] for disciplina in disciplinas}:
        for dia in dias:
            for periodo in range(1, 6):
                aulas_do_professor = []

                for turma in turmas:
                    for disciplina in disciplinas:
                        if disciplina["professor"] != professor:
                            continue

                        nome = disciplina["disciplina"]

                        # Aula que começa neste período.
                        if periodo in x[turma][nome][dia]:
                            aulas_do_professor.append(x[turma][nome][dia][periodo])

                        # Aula dupla que começou no período anterior.
                        if disciplina["duplo_periodo"] and periodo > 1:
                            inicio_anterior = periodo - 1
                            if inicio_anterior in x[turma][nome][dia]:
                                aulas_do_professor.append(
                                    x[turma][nome][dia][inicio_anterior]
                                )

                modelo.Add(sum(aulas_do_professor) <= 1)

    # Nenhuma aula pode ocupar um período em que o professor está indisponível.
    for turma in turmas:
        for disciplina in disciplinas:
            professor = disciplina["professor"]
            nome = disciplina["disciplina"]

            for dia in dias:
                for inicio, colocacao in x[turma][nome][dia].items():
                    periodos_ocupados = [inicio]
                    if disciplina["duplo_periodo"]:
                        periodos_ocupados.append(inicio + 1)

                    if any(
                        (professor, dia, periodo) in indisponibilidades
                        for periodo in periodos_ocupados
                    ):
                        modelo.Add(colocacao == 0)


@app.function
def adicionar_restricoes_salas(modelo, x, dados):
    turmas, disciplinas, salas, _ = dados
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex"]

    # As salas normais formam uma capacidade partilhada.
    quantidade_normais = sum(
        sala["quantidade"] for sala in salas if sala["tipo"] == "normal"
    )

    # Em cada período, não podemos exceder a quantidade de salas normais.
    if quantidade_normais > 0:
        for dia in dias:
            for periodo in range(1, 6):
                aulas_em_salas_normais = []

                for turma in turmas:
                    for disciplina in disciplinas:
                        if disciplina["sala_especial"] is not None:
                            continue

                        nome = disciplina["disciplina"]

                        if periodo in x[turma][nome][dia]:
                            aulas_em_salas_normais.append(
                                x[turma][nome][dia][periodo]
                            )

                        if disciplina["duplo_periodo"] and periodo > 1:
                            inicio_anterior = periodo - 1
                            if inicio_anterior in x[turma][nome][dia]:
                                aulas_em_salas_normais.append(
                                    x[turma][nome][dia][inicio_anterior]
                                )

                modelo.Add(sum(aulas_em_salas_normais) <= quantidade_normais)

    # Cada sala especial só pode ser usada até à sua capacidade.
    for sala in salas:
        if sala["tipo"] != "especial":
            continue

        for dia in dias:
            for periodo in range(1, 6):
                aulas_na_sala = []

                for turma in turmas:
                    for disciplina in disciplinas:
                        if disciplina["sala_especial"] != sala["sala"]:
                            continue

                        nome = disciplina["disciplina"]

                        if periodo in x[turma][nome][dia]:
                            aulas_na_sala.append(x[turma][nome][dia][periodo])

                        if disciplina["duplo_periodo"] and periodo > 1:
                            inicio_anterior = periodo - 1
                            if inicio_anterior in x[turma][nome][dia]:
                                aulas_na_sala.append(
                                    x[turma][nome][dia][inicio_anterior]
                                )

                modelo.Add(sum(aulas_na_sala) <= sala["quantidade"])


@app.function
def adicionar_restricoes_diarias(modelo, x, dados):
    turmas, disciplinas, _, _ = dados
    dias = ["Seg", "Ter", "Qua", "Qui", "Sex"]

    # Cada disciplina só pode ter uma ocorrência por dia em cada turma.
    for turma in turmas:
        for disciplina in disciplinas:
            nome = disciplina["disciplina"]

            for dia in dias:
                colocacoes_do_dia = []

                for periodo in range(1, 6):
                    if periodo in x[turma][nome][dia]:
                        colocacoes_do_dia.append(x[turma][nome][dia][periodo])

                modelo.Add(sum(colocacoes_do_dia) <= 1)


@app.function
def adicionar_objetivo_buracos(modelo, x, dados):
    ...


@app.function
def resolver_modelo(modelo, limite_segundos=None):
    ...


@app.function
def extrair_horario(solver, x, dados):
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
