class Pag:
    def __init__(self, ORDEM) -> None:
        self.n_chaves : int = 0
        self.chaves : list[list] = [[-1, -1]] * (ORDEM - 1) #lista que armazena as chave do registro e seu byteoffset [chave, byteoffset]
        self.filhos : list[int] = [-1] * ORDEM #armazena os rrn das paginas filhas, -1 indica que não tem filhas
