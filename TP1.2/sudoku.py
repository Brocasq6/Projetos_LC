# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "ortools",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from ortools.sat.python import cp_model

    return (cp_model,)


@app.class_definition
class box:

    def __init__(self, celulas=None, n=3):
        # verificar se o n é valido
        if type(n) != int:
            raise ValueError("n tem de ser um inteiro")
        if n < 1:
            raise ValueError("n tem de ser maior que 0")

        self.n = n
        self.N = n * n  # tamanho da grelha (ex: 9 para n=3)

        # dicionario com (linha, coluna) -> valor ou None
        self.celulas = {}

        # se deram celulas iniciais, adicionar uma a uma
        if celulas != None:
            for posicao in celulas:
                l = posicao[0]
                c = posicao[1]
                valor = celulas[posicao]
                self.add(l, c, valor)

    def add(self, l, c, valor=None):
        # as coordenadas tem de ser inteiros
        if type(l) != int or type(c) != int:
            raise TypeError("as coordenadas tem de ser inteiros")

        # as coordenadas tem de estar dentro da grelha
        if l < 0 or l >= self.N or c < 0 or c >= self.N:
            raise IndexError("a celula (" + str(l) + ", " + str(c) + ") esta fora da grelha")

        # se houver valor, tem de ser inteiro entre 1 e N
        if valor != None:
            if type(valor) != int:
                raise TypeError("o valor tem de ser um inteiro")
            if valor < 1 or valor > self.N:
                raise ValueError("o valor " + str(valor) + " tem de estar entre 1 e " + str(self.N))

        # se a celula ja existir
        if (l, c) in self.celulas:
            valor_antigo = self.celulas[(l, c)]
            # nao deixar mudar uma celula que ja estava fixa para outro valor
            if valor_antigo != None and valor != None and valor_antigo != valor:
                raise ValueError("a celula ja esta fixa a " + str(valor_antigo))
            # so atualiza se o novo valor nao for None
            if valor != None:
                self.celulas[(l, c)] = valor
        else:
            self.celulas[(l, c)] = valor

    def matriz(self):
        # criar uma matriz N x N cheia de zeros
        m = []
        for i in range(self.N):
            linha = []
            for j in range(self.N):
                linha.append(0)
            m.append(linha)

        # meter os valores fixos nas posicoes certas
        for posicao in self.celulas:
            valor = self.celulas[posicao]
            if valor != None:
                l = posicao[0]
                c = posicao[1]
                m[l][c] = valor

        return m

    def fixas(self):
        # devolve so as celulas que tem valor
        resultado = {}
        for posicao in self.celulas:
            if self.celulas[posicao] != None:
                resultado[posicao] = self.celulas[posicao]
        return resultado

    def mostrar(self):
        print("box com n =", self.n, "e", len(self.celulas), "celulas,", len(self.fixas()), "fixas")


@app.class_definition
class cube(box):

    def __init__(self, i, j, n=3):
        # inicializar a box vazia
        box.__init__(self, None, n)

        # os indices do bloco tem de ser inteiros
        if type(i) != int or type(j) != int:
            raise TypeError("os indices do bloco tem de ser inteiros")

        # os indices do bloco tem de estar entre 0 e n-1
        if i < 0 or i >= n or j < 0 or j >= n:
            raise IndexError("o bloco (" + str(i) + ", " + str(j) + ") nao existe")

        # canto superior esquerdo do bloco
        linha_inicio = i * n
        coluna_inicio = j * n

        # adicionar as n x n celulas do bloco
        for l in range(linha_inicio, linha_inicio + n):
            for c in range(coluna_inicio, coluna_inicio + n):
                self.add(l, c)


@app.class_definition
class path(box):

    def __init__(self, inicio, fim, n=3):
        # inicializar a box vazia
        box.__init__(self, None, n)

        # tirar as coordenadas do inicio e do fim
        linha0 = inicio[0]
        coluna0 = inicio[1]
        linha1 = fim[0]
        coluna1 = fim[1]

        # caso horizontal (mesma linha)
        if linha0 == linha1:
            # ver se anda para a direita ou para a esquerda
            if coluna1 >= coluna0:
                passo = 1
            else:
                passo = -1

            c = coluna0
            while c != coluna1 + passo:
                self.add(linha0, c)
                c = c + passo

        # caso vertical (mesma coluna)
        elif coluna0 == coluna1:
            # ver se anda para baixo ou para cima
            if linha1 >= linha0:
                passo = 1
            else:
                passo = -1

            l = linha0
            while l != linha1 + passo:
                self.add(l, coluna0)
                l = l + passo

        # se nao for nem horizontal nem vertical da erro
        else:
            raise ValueError("o caminho de " + str(inicio) + " para " + str(fim) + " nao e reto")


@app.cell
def _():
    import random

    def pistas_random(n, k=None, seed=None):
        N = n * n

        # se nao derem k, usar n pistas
        if k == None:
            k = n

        # como os valores sao todos diferentes, nao da para ter mais de N pistas
        if k < 0 or k > N:
            raise ValueError("k tem de estar entre 0 e " + str(N))

        # gerador de numeros aleatorios (com seed para dar sempre o mesmo resultado)
        gerador = random.Random(seed)

        # lista com todas as celulas da grelha
        todas_celulas = []
        for i in range(N):
            for j in range(N):
                todas_celulas.append((i, j))

        # lista com todos os valores possiveis
        todos_valores = []
        for v in range(1, N + 1):
            todos_valores.append(v)

        # escolher k celulas e k valores diferentes ao calhas
        celulas = gerador.sample(todas_celulas, k)
        valores = gerador.sample(todos_valores, k)

        # criar a box com as pistas
        b = box(None, n)
        for x in range(k):
            l = celulas[x][0]
            c = celulas[x][1]
            b.add(l, c, valores[x])
        return b

    return


@app.cell
def _(cp_model):
    class Modelo:

        def __init__(self, n=3):
            self.n = n
            self.N = n * n

            # criar o modelo
            self.modelo = cp_model.CpModel()

            # uma variavel inteira por celula, com valor entre 1 e N
            self.x = []
            for l in range(self.N):
                linha = []
                for c in range(self.N):
                    nome = "x_" + str(l) + "_" + str(c)
                    linha.append(self.modelo.NewIntVar(1, self.N, nome))
                self.x.append(linha)

        def add(self, *grupos):
            for grupo in grupos:

                # o grupo tem de ser do mesmo tamanho que o modelo
                if grupo.N != self.N:
                    raise ValueError("o grupo tem N=" + str(grupo.N) + " mas o modelo tem N=" + str(self.N))

                # juntar as variaveis das celulas do grupo
                variaveis = []
                for posicao in grupo.celulas:
                    l = posicao[0]
                    c = posicao[1]
                    variaveis.append(self.x[l][c])

                # todas as celulas do grupo tem valores diferentes
                self.modelo.AddAllDifferent(variaveis)

                # fixar as celulas que tem valor
                for posicao in grupo.celulas:
                    valor = grupo.celulas[posicao]
                    if valor != None:
                        l = posicao[0]
                        c = posicao[1]
                        self.modelo.Add(self.x[l][c] == valor)

        def solve(self):
            solver = cp_model.CpSolver()
            estado = solver.Solve(self.modelo)

            # se nao encontrou solucao devolve None
            if estado != cp_model.OPTIMAL and estado != cp_model.FEASIBLE:
                return None

            # construir a grelha com a solucao
            grelha = []
            for l in range(self.N):
                linha = []
                for c in range(self.N):
                    linha.append(solver.Value(self.x[l][c]))
                grelha.append(linha)

            return grelha

    return


if __name__ == "__main__":
    app.run()
