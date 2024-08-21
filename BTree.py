import struct
from Pag import Pag

'''
No arquivo btree.dat os 4 primeiros bytes armazenam a quatidade de paginas
e os proximos 4 bits armazenam o rrn da raiz
'''

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
        self.btree.seek(4)
        raiz : int = struct.unpack("I", self.btree.read(4))[0]
        return raiz
    
    def escrever_raiz(self, nova_raiz) -> None:
        raiz : bytes = struct.pack("I", nova_raiz)
        self.btree.seek(4)
        self.btree.write(raiz)

    def ler_q_paginas(self) -> int:
        self.btree.seek(0)
        q_paginas : int = struct.unpack("I", self.btree.read(4))[0]
        return q_paginas

    def add_q_paginas(self) -> None:
        #adiciona 1 ao numero de pagina e escreve no arquivo btree.dat
        q_paginas : int = self.ler_q_paginas()
        q_paginas += 1
        self.btree.seek(0)
        q_paginas = struct.pack("I", q_paginas)
        self.btree.write(q_paginas)

    def ler_registro(self, tam=0):
        #retorna a chave e o byteOffset do registro
        self.arquivo_games.seek(4)
        tam_registro = struct.unpack("H", self.arquivo_games.read(2))[0]
        reg = self.arquivo_games.read(tam_registro).decode()
        reg = reg.split("|")
        chave = int(reg[0])
        #ta dando erro aqui
        byteOffset = 4 + tam
        print(chave, byteOffset)
        return chave, byteOffset, tam_registro

    def criar_indice(self):
        btreeFile = open("btree.dat", 'wb+')
        self.btree = btreeFile
    
        pag : Pag = Pag(self.ORDEM)
        self.escrever_pagina(0, pag)
        self.escrever_raiz(0)


        chave, byt, tam = self.ler_registro()
        self.inserir_na_arvore(chave, byt, self.ler_raiz()) 
        self.add_q_paginas()

        chave, byt, tam = self.ler_registro(tam)
        self.inserir_na_arvore(chave, byt, self.ler_raiz()) 
        self.add_q_paginas()

        pagina = self.ler_pagina(0)
        print(pagina.chaves, pagina.filhos)
        #chave, byteOffset = self.ler_registros()
        #self.inserir_na_arvore(chave, byteOffset, None)

    def buscar_na_arvore(self, chave : int, rrn : int):
        if rrn == None : return False, None, None

        #TO-DO - Feito
        #ler a pagina armazenada no rrn para pag
        pagina : Pag = Pag(self.ORDEM)
        pagina = self.ler_pagina(rrn)

        achou, pos = self.buscar_na_pagina(chave, pagina)

        if achou:
            return True, rrn, pos
        else:
            #busca na arvore filha
            return self.buscar_na_arvore(chave, pagina.filhos[pos])

    def novo_rrn(self) -> int:
        self.btree.seek(4)
        q_paginas : int = struct.unpack("I", self.btree.read(4))[0]
        #Outra forma de fazer é armazena a quantide de paginas no arquivo btree 
        #no cabeçalho e fazer o calculo (cabeçalho + (tam_pagina * q_paginas))
        offset : int = q_paginas * self.tamanho_registro
        return (offset + 8) // self.tamanho_registro

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
        if rrnAtual == -1 :
            chavePro = chave
            filhoDpro = -1
            return chavePro, filhoDpro, True
        
        else:
            #TO-DO - FEITO
            #ler pagina armazenada no rrnAtual
            pag : Pag = self.ler_pagina(rrnAtual)
            achou, pos = self.buscar_na_pagina(chave, pag)
            
            if achou:
                raise ValueError("Chave duplicada")
            else:
                chavePro, filhoDpro, promo = self.inserir_na_arvore(chave, byteOffset, pag.filhos[pos])
                if promo:
                    if pag.n_chaves - (self.ORDEM - 1) <=0:
                        #TO-DO - Verificar a lógica
                        #inserir chavePro e filhoDpro em pag
                        self.inserir_na_pagina(chavePro,filhoDpro, pag, byteOffset)
                        #escrever pag no arquivo em rrnAtual
                        self.escrever_pagina(rrnAtual ,pag)
                        
                    else:
                        #TO-DO
                        #criar função divide
                        chavePro, byteOffsert, filhoDpro, pag, novaPag = self.divide(chavePro, filhoDpro, promo)
                        #TO-DO
                        #escrever pag no arquivo em rrnAtual
                        self.escrever_pagina(rrnAtual, pag)
                        #escrever novaPag no arquivo em filhoDpro
                        self.escrever_pagina(filhoDpro, novaPag)
                        return chavePro, filhoDpro, True
                else:
                    return -1, -1, False

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


    #Finalizado e testado
    def escrever_pagina(self, rrn : int, pagina : Pag) -> None:
        byteOffset : int = rrn * self.tamanho_registro + 8
        buffer = b''
        buffer += struct.pack("H", pagina.n_chaves)
        
        for x in pagina.chaves:
            buffer += struct.pack("i", x[0]) #chave
            buffer += struct.pack("i", x[1]) #byteOffset
        
        for i in pagina.filhos:
            buffer += struct.pack("i", i) #filho

        self.btree.seek(byteOffset)
        self.btree.write(buffer)

    #Finalizado e testado
    def ler_pagina(self, rrnPagina : int) -> Pag:
        pagina : Pag = Pag(self.ORDEM)
        byteOffsetPagina : int = rrnPagina * self.tamanho_registro + 8
        self.btree.seek(byteOffsetPagina)
        
        pagina.n_chaves = struct.unpack("H", self.btree.read(2))[0]

        for x in range(self.ORDEM - 1):
            chave : int = struct.unpack("i", self.btree.read(4))[0]
            pagina.chaves[x][0] = chave
            byteOffset : int = struct.unpack("i", self.btree.read(4))[0]
            pagina.chaves[x][1] = byteOffset

        for i in range(self.ORDEM):
            filho : int = struct.unpack("i", self.btree.read(4))[0]
            pagina.filhos[i] = filho

        return pagina