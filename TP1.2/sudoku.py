import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from ortools.linear_solver import pywraplp

    return (pywraplp,)


@app.cell
def box(val):
    class box:
        #funcao de inicialização
        def __init__(self, cells=None, n=3):

            if n < 1:
                raise ValueError(f"n inválido: {repr(n)}")

            if not isinstance(n, int) or isinstance(n, bool):
                raise ValueError(f"n inválido: {repr(n)}")

            if isinstance(n, bool):
                raise ValueError(f"n inválido: {repr(n)}")

            self.n = n
            self.N = n * n                      
            self.cells = {}                     

            for (l, c), valor in (cells or {}).items():
                self.add(l, c, valor)             

        #funcao que adiciona uma celula ao grupo e rejeita coordenadas ou valores invalidos
        def add(self, l, c, valor=None):

            for coordenada in (l, c):
                if not isinstance(coordenada, int) or isinstance(coordenada, bool):
                    raise TypeError(f"coordenada não inteira: {repr(coordenada)}")
    
            if not (0 <= l < self.N and 0 <= c < self.N):
                raise IndexError(f"célula ({l}, {c}) fora da grelha {self.N}x{self.N}")

            if valor is not None:
                if not isinstance(valor, int):
                    raise TypeError(f"valor não inteiro: {repr(valor)}")

                if isinstance(valor, bool):
                    raise TypeError(f"valor não inteiro: {repr(valor)}")

                if not (1 <= val <= self.N):
                    raise ValueError(f"valor {val} fora de [1, {self.N}]")

            atual = self.cells.get((l, c))

            if atual is not None and val is not None and atual != val:
                raise ValueError(f"({l}, {c}) já está fixa a {atual}, não pode passar a {val}")

            if val is not None or (l, c) not in self.cells:
                self.cells[(l, c)] = val

            return self                         

        #funcao que devolve o grupo como uma matriz NxN, com valores fixos e zeros em tudo o que restar
        def matrix(self):

            matriz = [[0] * self.N for _ in range(self.N)]

            for (l, c), val in self.cells.items():
                if val is not None:
                    matriz[l][c] = val
            return matriz

        #funcao que devolve as celulas que estiverem fixas
        def fixas(self):
            return {cel: val for cel, val in self.cells.items() if val is not None}

        def __iter__(self):
            return iter(self.cells.items())

        def __len__(self):
            return len(self.cells)

        def __contains__(self, cel):
            return cel in self.cells

        def __repr__(self):
            return (f"{type(self).__name__} (n={self.n}, {len(self)} células, "f"{len(self.fixed())} fixas) ")

    return (box,)


@app.cell
def _(box):
    class cube(box):

            def __init__(self, i, j, n=3):

                super().__init__(n=n)

                #garantir que os valores são inteiros 
                for indice in (i, j):
                    if not isinstance(indice, int) or isinstance(indice, bool):
                        raise TypeError(f"índice de bloco não inteiro: {repr(indice)}")

                if not (0 <= i < n and 0 <= j < n):
                    raise IndexError(f"bloco ({i}, {j}) fora de [0, {n})")

                for l in range(i * n, (i + 1) * n):
                    for c in range(j * n, (j + 1) * n):
                        self.add(l, c)

                return (cube)


    return


@app.cell
def _(box, c0, c1, l0, l1):
    class path(box):

            def __init__(self, inicio, fim, n=3):

                super().__init__(n=n)

                (linha0, col0) = inicio
                (linha1, col1) = fim

                # verifi
                if linha0 == linha1:                        
                    passo = 1 if col1 >= col0 else -1
                    celulas = [(linha0, c) for colunas in range(col0, col1 + passo, passo)]

                elif c0 == c1:
                    passo = 1 if l1 >= l0 else -1
                    celulas = [(l, c0) for l in range(l0, l1 + passo, passo)]

                else:
                    raise ValueError(f"{inicio} -> {fim} não é um troço horizontal nem vertical")

                for l, c in celulas:
                    self.add(l, c)

                return (path)

    return


@app.cell
def _(box, random):
    def pistas_random(n, k = None , seed = None):
        N = n*n
        k = n if k is None else k

        if not 0 <= k <= N:
            raise ValueError(f"k tem de estar em [0,{N}] valores distintos")

        range = random.Random(seed)

        celulas = range.sample([(i,j) for i in range(N) for j in range(N)],k)

        valores = range.sample(range(1,N+1),k)

        b = box(n)

        for(i,j) , v in zip(celulas,valores):
            b.add(i,j,v)
        return b

    return


@app.cell
def _(g, none, pywraplp, v):
    class Modelo:

        def __init__(self, n=3):
            self.n = n
            self.N = n * n

            # criar o solver
            self.solver = pywraplp.Solver.CreateSolver("SCIP")
            if self.solver is None:
                raise RuntimeError("SCIP não disponível no OR-Tools instalado")

            # criar as variáveis binárias x[l][c][v]
            self.x = []
            for l in range(self.N):
                linha = []
                for c in range(self.N):
                    celula = {}
                    for v in range(1, self.N + 1):
                        celula[v] = self.solver.BoolVar(f"x_{l}_{c}_{v}")
                    linha.append(celula)
                self.x.append(linha)

            # criar as variáveis inteiras y[l][c], com valor entre 1 e N
            self.y = []
            for l in range(self.N):
                linha = []
                for c in range(self.N):
                    linha.append(self.solver.IntVar(1, self.N, f"y_{l}_{c}"))
                self.y.append(linha)

            # restrições de cada célula
            for l in range(self.N):
                for c in range(self.N):

                    # cada célula tem exatamente um valor
                    soma = 0
                    for v in range(1, self.N + 1):
                        soma = soma + self.x[l][c][v]
                    self.solver.Add(soma == 1)

                    # y[l][c] é igual ao valor
                    valor_celula = 0
                    for v in range(1, self.N + 1):
                        valor_celula = valor_celula + v * self.x[l][c][v]
                    self.solver.Add(self.y[l][c] == valor_celula)

        def add(self, grupos):
            for grupo in grupos:
        
                # o grupo tem de ter o mesmo tamanho de grelha que o modelo
                if grupo.N != self.N:
                    raise ValueError(f"grupo com N={g.N}, modelo com N={self.N}")

                # todos diferentes: cada valor aparece no máximo uma vez no grupo
                for valor in range(1, self.N + 1):
                    soma = 0
                    for (l, c) in g.cells:
                        soma = soma + self.x[l][c][v]
                    self.solver.Add(soma <= 1)

                # fixar as células que têm valor
                for (l, c) in g.cells:
                    val = g.cells[(l, c)]
                    if val is not None:
                        self.solver.Add(self.x[l][c][val] == 1)

            return self

        def solve(self):
    
            estado = self.solver.Solve()

            if estado != pywraplp.Solver.OPTIMAL:
                return None
            if estado != pywraplp.Solver.FEASIBLE:
                return none

            grelha = []
    
            for l in range(self.N):
                linha = []
                for c in range(self.N):
                    valor = self.y[l][c].solution_value()
                    linha.append(int(round(valor)))
                grelha.append(linha)
            return grelha

    return


if __name__ == "__main__":
    app.run()
