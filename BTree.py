import struct
from Pag import Pag

'''
No arquivo btree.dat os 4 primeiros bytes armazenam a quatidade de paginas
e os proximos 4 bits armazenam o rrn da raiz
'''

class BTree:
    def __init__(self, arquivo_games : str, ORDEM : int = 4) -> None:   
        self.arquivo_games = open(arquivo_games, 'rb+')
        self.btree = None
        self.ORDEM : int = ORDEM
        self.tamanho_registro : int = 2 + ((2 * (self.ORDEM - 1)) * 4) + (self.ORDEM * 4)
        #4 bytes para cada: chave, byteoffser e rrn das filhas
        #2 bytes são do numero de chaves na pagina 

    def setBtree(self, bt):
        self.btree = bt
        
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

    def ler_registro(self) -> tuple:
        #retorna a chave e o byteOffset do registro
        try:
            byteOffset = self.arquivo_games.tell()
            tam_registro = struct.unpack("H", self.arquivo_games.read(2))[0]
            reg = self.arquivo_games.read(tam_registro).decode()
            reg = reg.split("|")
            print(reg)
            chave = int(reg[0])
            print(chave, byteOffset)
            return chave, byteOffset
        except:
            return False, False
        
    def buscar_na_arvore(self, chave : int, rrn : int) -> tuple:
        if rrn == None : return False, None, None

        pagina : Pag = Pag(self.ORDEM)
        pagina = self.ler_pagina(rrn)

        achou, pos = self.buscar_na_pagina(chave, pagina)

        if achou:
            return True, rrn, pos
        else:
            #busca na arvore filha
            return self.buscar_na_arvore(chave, pagina.filhos[pos])

    def novo_rrn(self) -> int:
        self.btree.seek(0, 2)
        offset = self.btree.tell()
        return (offset - 8) // self.tamanho_registro

    def divide(self, chave : int, filhoD : int, byteOffset : int, pagina : Pag):
        print("Função divide")
        print(pagina.chaves, pagina.filhos)
        
        # Inserir a chave na página antes de dividir
        self.inserir_na_pagina(chave, filhoD, pagina, byteOffset)
        print(pagina.chaves, pagina.filhos)
        
        # Encontrar o ponto de divisão
        meio : int = self.ORDEM // 2
        
        # Chave e byteOffset a serem promovidos
        chavePro = pagina.chaves[meio][0]
        byteoffsetPro = pagina.chaves[meio][1]
        filhoDpro = self.novo_rrn()
        
        # Criar as novas páginas
        pAtual = Pag(self.ORDEM)
        pNova = Pag(self.ORDEM)

        # Atribuir chaves e filhos para pAtual e pNova
        pAtual.chaves = pagina.chaves[:meio] + [[-1, -1]] * (self.ORDEM - 1 - meio)
        pAtual.filhos = pagina.filhos[:meio + 1] + [-1] * (self.ORDEM - (meio + 1))
        pAtual.n_chaves = meio

        # pNova recebe o restante das chaves e filhos
        pNova.chaves = pagina.chaves[meio + 1:] + [[-1, -1]] * (self.ORDEM - 1 - (pagina.n_chaves - (meio + 1)))
        pNova.filhos = pagina.filhos[meio + 1:] + [-1] * (self.ORDEM - (pagina.n_chaves - (meio + 1)))
        pNova.n_chaves = len(pNova.chaves)
        
        print(f"Pagina atual: {pAtual.chaves}, {pAtual.filhos}")
        print(f"Pagina nova: {pNova.chaves}, {pNova.filhos}")

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
            
        chavePro, filhoDpro, promo = self.inserir_na_arvore(chave, byteOffset, pag.filhos[pos])
        
        if not promo:
            return -1, -1, False
        
        else:
            if pag.n_chaves < (self.ORDEM - 1):
                #TO-DO - Verificar a lógica
                #inserir chavePro e filhoDpro em pag
                print(pag.chaves, pag.filhos)
                self.inserir_na_pagina(chavePro, filhoDpro, pag, byteOffset)
                #escrever pag no arquivo em rrnAtual
                self.escrever_pagina(rrnAtual ,pag)
                return -1, -1, False
                        
            else:
                #TO-DO
                #criar função divide
                chavePro, byteOffset, filhoDpro, pag, novaPag = self.divide(chavePro, filhoDpro, byteOffset, pag)
                #TO-DO
                #escrever pag no arquivo em rrnAtual
                self.escrever_pagina(rrnAtual, pag)
                #escrever novaPag no arquivo em filhoDpro
                self.escrever_pagina(filhoDpro, novaPag)
                #self.add_q_paginas()
                return chavePro, filhoDpro, True
            
    def buscar_na_pagina(self, chave, pagina : Pag) -> list:
        pos : int = 0
        while pos < pagina.n_chaves & chave > pagina.chaves[pos][0]:
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
        print(f"Pagiana sendo escrita: chaves: {pagina.chaves}, \n filhos: {pagina.filhos}")
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
       # print(pagina.n_chaves)

        for x in range(self.ORDEM - 1):
            chave : int = struct.unpack("i", self.btree.read(4))[0]
            byteOffset : int = struct.unpack("i", self.btree.read(4))[0]
            pagina.chaves[x] = [chave, byteOffset]

            #pagina.chaves[x][0] = chave
            #print(pagina.chaves[x][0])
            #pagina.chaves[x][1] = byteOffset
            #print(pagina.chaves[x][1])

        for i in range(self.ORDEM):
            filho : int = struct.unpack("i", self.btree.read(4))[0]
            pagina.filhos[i] = filho
            #print(pagina.filhos[i])

        #print(pagina.chaves, pagina.filhos)

        return pagina

    def gerenciadorInsercao(self, raiz):
        self.arquivo_games.seek(4)
        pg = Pag(self.ORDEM)
        self.escrever_pagina(raiz, pg)
        self.add_q_paginas()

        chave, byteOffset = self.ler_registro()
        while chave != False:
            raiz = self.ler_raiz()
            print(f"Raiz: {raiz}")
            
            chavePro, filhoDpro, promocao = self.inserir_na_arvore(chave, byteOffset, raiz)

            if promocao:
                pagina = Pag(self.ORDEM)
                self.add_q_paginas()
                dado = [chavePro, byteOffset]
                pagina.chaves[0] = dado
                pagina.filhos[0] = raiz
                pagina.filhos[1] = filhoDpro
                pagina.n_chaves += 1
                print(pagina.chaves, pagina.filhos)
                self.escrever_raiz(self.ler_q_paginas())
                
                self.escrever_pagina(self.ler_raiz(), pagina)
                print(f"NOVA Raiz: {self.ler_raiz()}")

            chave, byteOffset = self.ler_registro()

        return raiz


    def print_btree(self):
        q_paginas = self.ler_q_paginas()
        print(q_paginas)
        raiz = self.ler_raiz()
        for x in range(19):
            print(x)
            pagina : Pag = self.ler_pagina(x)
            print(pagina.chaves, pagina.filhos)