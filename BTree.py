import struct
from Pag import Pag

class BTree:
    def __init__(self, arquivo_games : str, ORDEM : int = 4, controle_rrn : int = 0) -> None:   
        self.arquivo_games = open(arquivo_games, 'rb+')
        self.btree = None
        self.ORDEM : int = ORDEM
        self.controle_rrn : int = controle_rrn
        self.tamanho_registro : int = 2 + ((2 * (self.ORDEM - 1)) * 4) + (self.ORDEM * 4)
        #4 bytes para cada: chave, byteoffser e rrn das filhas
        #2 bytes são do numero de chaves na pagina 


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

    def novo_rrn(self) -> int:
        self.btree.seek(0, 2)
        #Outra forma de fazer é armazena a quantide de paginas no arquivo btree 
        #no cabeçalho e fazer o calculo (cabeçalho + (tam_pagina * q_paginas))
        offset : int = self.btree.tell()
        return (offset - 4) // self.tamanho_registro

    def divide(self, chave : int, filhoD : int, byteOffset : int, pagina : Pag):
        self.inserir_na_pagina(chave, filhoD, pagina, byteOffset)
        
        meio : int = self.ORDEM // 2
            
        chavePro = pagina.chaves[meio][0]
        byteoffsetPro = pagina.chaves[meio][1]
        filhoDpro = self.novo_rrn()
        
        pAtual = Pag(self.ORDEM)
        pNova = Pag(self.ORDEM)
        
        pAtual.chaves = pagina.chaves[:meio] + [[-1, -1]] * (self.ORDEM - 1 - meio)
        pAtual.filhos = pagina.filhos[:meio + 1] + [-1] * (self.ORDEM - (meio + 1))
        pAtual.n_chaves = meio
        
        pNova.chaves = pagina.chaves[meio:] + [[-1, -1]] * (self.ORDEM - 1 - (pagina.n_chaves - (meio + 1)))
        pNova.filhos = pagina.filhos[meio + 1:] + [-1] * (self.ORDEM - (pagina.n_chaves - (meio + 1)))
        pNova.n_chaves = pagina.n_chaves - (meio + 1)
        
        return chavePro, byteoffsetPro, filhoDpro, pAtual, pNova

    def inserir_na_arvore(self, chave : int, byteOffset : int, rrnAtual : int):
        if rrnAtual == None :
            chavePro = chave
            filhoDpro = None
            return chavePro, filhoDpro, True
        
        else:
            #TO-DO - FEITO
            #ler pagina armazenada no rrnAtual
            pag : Pag = self.ler_pagina(rrnAtual)
            achou, pos = self.buscar_na_pagina(chave, pag)
            
            if achou:
                raise ValueError("Chave duplicada")
            else:
                chavePro, filhoDpro, promo = self.inserir_na_arvore(chave, pag.filhos[pos])
                if promo:
                    if pag.n_chaves - (self.ORDEM - 1) <=0:
                        #TO-DO - Verificar a lógica
                        #inserir chavePro e filhoDpro em pag
                        self.inserir_na_pagina(chavePro,filhoDpro, byteOffset)
                        #escrever pag no arquivo em rrnAtual
                        self.escrever_pagina(rrnAtual ,pag)
                        
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

    def buscar_na_pagina(self, chave, pagina : Pag) -> list:
        pos : int = 0
        while pos < pagina.n_chaves and chave > pagina.chaves[pos][0]:
            pos += 1
        
        if pos < pagina.n_chaves and chave == pagina.chaves[pos][0]:
            return True, pos
        else:
            return False, pos

    def inserir_na_pagina(self, chave : int, filhoD : int, pagina : Pag, byteOffset : int):
        if pagina.n_chaves == (self.ORDEM - 1):
            pagina.chaves.append([-1, -1])
            pagina.filhos.append(-1)
        
        i : int = pagina.n_chaves

        while i > 0 and chave < pagina.chaves[i - 1][0]:
            pagina.chaves[i] = pagina.chaves[i - 1]
            pagina.filhos[i + 1] = pagina.filhos[i]
            i -= 1
        pagina.chaves[i] = [chave, byteOffset]
        pagina.filhos[i + 1] = filhoD
        pagina.n_chaves += 1

    def escrever_pagina(self, rrn : int, pagina : Pag) -> None:
        byteOffset : int = rrn * self.tamanho_registro + 4
        buffer : bytearray
        buffer += struct.pack("H", pagina.n_chaves)
        for x in range(self.ORDEM - 1):
            buffer += struct.pack("I", pagina.chaves[x][0])
            buffer += struct.pack("I", pagina.chaves[x][1])
        
        for i in range(self.ORDEM):
            buffer += struct.pack("I", pagina.filhos[i])

        self.btree.seek(byteOffset)
        self.btree.write(buffer)

    def ler_pagina(self, rrnPagina : int) -> Pag:
        pagina : Pag = Pag(self.ORDEM)
        byteOffsetPagina : int = rrnPagina * self.tamanho_registro + 4
        self.btree.seek(byteOffsetPagina)
        pagina.n_chaves = struct.unpack("H", self.btree.read(2))[0]

        for x in range(self.ORDEM - 1):
            chave : int = struct.unpack("I", self.btree.read(4))[0]
            byteOffset : int = struct.unpack("I", self.btree.read(4))[0]
            pagina.chaves.append([chave, byteOffset])

        for i in range(self.ORDEM):
            filho : int = struct.unpack("I", self.btree.read(4))[0]
            pagina.filhos.append(filho)

        return pagina