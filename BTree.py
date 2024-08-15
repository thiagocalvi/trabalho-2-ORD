import struct
from Pag import Pag

class BTree:
    def __init__(self, arquivo_games : str, ORDEM : int = 4) -> None:
        self.arquivo_games = open(arquivo_games, 'rb+')
        self.btree = None
        self.controle_n_pagina : int = 0
        self.ORDEM : int = ORDEM


    def ler_raiz(self) -> int:
        self.btree.seek(0)
        raiz : int = struct.unpack("I", self.btree.read(4))[0]
        return raiz
    
    def escrever_raiz(self, nova_raiz) -> None:
        raiz : bytes = struct.pack("I", nova_raiz)
        self.btree.seek(0)
        self.btree.write(raiz)


    def buscar_na_arvore(self, chave : int, rrn : int):
        if rrn == None : return False, None, None

        #TO-DO
        #ler a pagina armazenada no rrn para pag
        #calcular o byteoffset

        pag : Pag = Pag(self.ORDEM) #somente ilustrativo
        achou, pos = self.buscar_na_pagina(chave, pag)

        if achou:
            return True, rrn, pos
        else:
            #busca na arvore filha
            return self.buscar_na_arvore(chave, pag.filhos[pos])


    def buscar_na_pagina(self, chave, pagina : Pag):
        pos = 0
        while pos < pagina.n_chaves & chave > pagina.chaves[pos]:
            pos += 1
        if pos < pagina.n_chaves & chave == pagina.chaves[pos]:
            return True, pos
        else:
            return False, pos

    def inserir_na_arvore(self, chave : int, rrnAtual : int):
        if rrnAtual == None :
            chavePro = chave
            filhoDpro = None
            return chavePro, filhoDpro, True
        
        else:
            #TO-DO
            #ler pagina armazenada no rrnAtual
            pag : Pag = Pag(self.ORDEM)
            achou, pos = self.buscar_na_pagina(chave, pag)
            
            if achou:
                raise ValueError("Chave duplicada")
            else:
                chavePro, filhoDpro, promo = self.inserir_na_arvore(chave, pag.filhos[pos])
                if promo:
                    if pag.n_chaves - (self.ORDEM - 1) >= 1:
                        #TO-DO
                        #inserir chavePro e filhoDpro em pag
                        #escrever pag no arquivo em rrnAtual
                        pass
                    else:
                        #TO-DO
                        #criar função divide
                        chavePro, filhoDpro, pag, novaPag = self.divide(chavePro, filhoDpro, promo)
                        #TO-DO
                        #escrever pag no arquivo em rrnAtual
                        #escrever novaPag no arquivo em filhoDpro
                        return chavePro, filhoDpro, True
                else:
                    return None, None, False
