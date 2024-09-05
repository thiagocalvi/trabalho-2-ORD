import struct
from Pag import Pag

'''
No arquivo btree.dat os 4 primeiros bytes armazenam a quatidade de paginas
e os proximos 4 bits armazenam o rrn da raiz
'''

class BTree:
    def __init__(self, ORDEM : int = 4) -> None:   
        self.arquivo_games = None
        self.btree = None
        self.ORDEM : int = ORDEM
        self.tamanho_registro : int = 2 + ((2 * (self.ORDEM - 1)) * 4) + (self.ORDEM * 4)
        #4 bytes para cada: chave, byteoffser e rrn das filhas
        #2 bytes são do numero de chaves na pagina 

    def setBtree(self, bt) -> None:
        self.btree = bt

    def setArqGames(self, arquivo_games_name):
        self.arquivo_games = arquivo_games_name

        
    def ler_raiz(self) -> int:
        #Lê a raiz da arvore no arquivo btree.dat
        self.btree.seek(4)
        raiz : int = struct.unpack("I", self.btree.read(4))[0]
        return raiz
    
    def escrever_raiz(self, nova_raiz) -> None:
        #Escreve a raiz no arquivo btree.dat
        raiz : bytes = struct.pack("I", nova_raiz)
        self.btree.seek(4)
        self.btree.write(raiz)

    def ler_q_paginas(self) -> int:
        #Lê a quantidade de paginas no arquivo btree.dat
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
        #Lê os registro do arquivo games
        try:
            byteOffset = self.arquivo_games.tell()
            tam_registro = struct.unpack("H", self.arquivo_games.read(2))[0]
            reg = self.arquivo_games.read(tam_registro).decode()
            reg = reg.split("|")
            chave = int(reg[0])
            return chave, byteOffset
        except:
            return False, False
        
    def buscar_na_arvore(self, chave : int, rrn : int) -> tuple:
        #Busca uma chave na arvore
        if rrn == -1 : return False, None, None

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

    def divide(self, chave: int, filhoD: int, byteOffset: int, pagina: Pag):
        #Divide uma pagina 
        self.inserir_na_pagina(chave, filhoD, pagina, byteOffset)
        meio: int = self.ORDEM // 2
        
        chavePro = pagina.chaves[meio][0]
        byteoffsetPro = pagina.chaves[meio][1]
        filhoDpro = self.novo_rrn()
        self.add_q_paginas()
        
        pAtual = Pag(self.ORDEM)
        pNova = Pag(self.ORDEM)
        
        # Atribuir chaves e filhos para pAtual
        pAtual.n_chaves = meio
        for i in range(meio):
            pAtual.chaves[i] = pagina.chaves[i]
        for i in range(meio + 1):
            pAtual.filhos[i] = pagina.filhos[i]
        
        # pNova recebe o restante das chaves e filhos
        pNova.n_chaves = pagina.n_chaves - meio - 1
        for i in range(pNova.n_chaves):
            pNova.chaves[i] = pagina.chaves[meio + 1 + i]
        for i in range(pNova.n_chaves + 1):
            pNova.filhos[i] = pagina.filhos[meio + 1 + i]

        return chavePro, byteoffsetPro, filhoDpro, pAtual, pNova

    def inserir_na_arvore(self, chave : int, byteOffset : int, rrnAtual : int, x = -1):
        #Insere uma chave\byteoffser na arvore
        if rrnAtual == -1 :
            chavePro = chave
            filhoDpro = -1
            return chavePro, filhoDpro, True, -1
        
        else:
            pag : Pag = self.ler_pagina(rrnAtual)
            achou, pos = self.buscar_na_pagina(chave, pag)
            
        if achou:
            raise ValueError("Chave duplicada")
            
        chavePro, filhoDpro, promo, byteoffsetPro = self.inserir_na_arvore(chave, byteOffset, pag.filhos[pos])
        
        if not promo:
            return -1, -1, False, -1
        
        else:
            if pag.n_chaves < (self.ORDEM - 1):
                self.inserir_na_pagina(chavePro, filhoDpro, pag, byteOffset)
                self.escrever_pagina(rrnAtual ,pag)
                return -1, -1, False, -1
                        
            else:
                chavePro, byteoffsetPro, filhoDpro, pag, novaPag = self.divide(chavePro, filhoDpro, byteOffset, pag)
                self.escrever_pagina(rrnAtual, pag)
                self.escrever_pagina(filhoDpro, novaPag)
                return chavePro, filhoDpro, True, byteoffsetPro
            
    def buscar_na_pagina(self, chave, pagina : Pag) -> list:
        #Busca uma chave na pagina informada
        pos : int = 0
        while pos < pagina.n_chaves and chave > pagina.chaves[pos][0]:
            pos += 1
        
        if pos < pagina.n_chaves and chave == pagina.chaves[pos][0]:
            return True, pos
        else:
            return False, pos

    def inserir_na_pagina(self, chave : int, filhoD : int, pagina : Pag, byteOffset : int) -> None:
        #Insere uma chave\byteoffset e filho direito na pagina informada
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
        #Escreve uma pagina no rrn informado
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

    def ler_pagina(self, rrnPagina : int) -> Pag:
        #Lê uma pagina armazenada no rrn informado
        pagina : Pag = Pag(self.ORDEM)
        byteOffsetPagina : int = rrnPagina * self.tamanho_registro + 8
        self.btree.seek(byteOffsetPagina)
        buffer = self.btree.read(self.tamanho_registro)
        
        pagina.n_chaves = struct.unpack("H", buffer[:2])[0]
        # Separar chaves e byteOffsets
        offset = 2
        for x in range(self.ORDEM - 1):
            chave: int = struct.unpack("i", buffer[offset:offset + 4])[0]
            offset += 4
            byteOffset: int = struct.unpack("i", buffer[offset:offset + 4])[0]
            offset += 4
            pagina.chaves[x] = [chave, byteOffset]

        # Separar filhos
        for i in range(self.ORDEM):
            filho: int = struct.unpack("i", buffer[offset:offset + 4])[0]
            offset += 4
            pagina.filhos[i] = filho
        
        return pagina

    def criar_indice(self) -> None:
        #Cria o indece da arvore b no arquivo btree.dat
        self.escrever_raiz(0)
        raiz : int = 0
        self.add_q_paginas()
        self.arquivo_games.seek(4)
        pg = Pag(self.ORDEM)
        self.escrever_pagina(raiz, pg)

        chave, byteOffset = self.ler_registro()
        while chave != False:
            
            chavePro, filhoDpro, promocao, byteoffsetPro = self.inserir_na_arvore(chave, byteOffset, raiz)
            
            if promocao:
                pagina = Pag(self.ORDEM)
                self.add_q_paginas()
                dado = [chavePro, byteoffsetPro]
                pagina.chaves[0] = dado
                pagina.filhos[0] = raiz
                pagina.filhos[1] = filhoDpro
                pagina.n_chaves += 1
                raiz = self.novo_rrn()
                self.escrever_raiz(raiz)
                self.escrever_pagina(raiz, pagina)

            chave, byteOffset = self.ler_registro()

    def print_btree(self) -> None:
        #Imprime o indice da arvore b que está no arquivo btree.dat
        q_paginas : int = self.ler_q_paginas()
        raiz : int = self.ler_raiz()
        for x in range(q_paginas):
            pagina : Pag = self.ler_pagina(x)
            chaves : list = [chave[0] for chave in pagina.chaves if chave[0] != -1] + [-1] * (self.ORDEM - 1 - pagina.n_chaves)  
            bytesOffset : list = [chave[1] for chave in pagina.chaves if chave[1] != -1] + [-1] * (self.ORDEM - 1 - pagina.n_chaves)
            if x == raiz:
                print(f"----------------------------- Raiz -----------------------------")
                print(f"Pagina: {x}")
                print(f"Chaves: {chaves}")
                print(f"Offsets: {bytesOffset}")
                print(f"Filhos: {pagina.filhos}")
                print(f"----------------------------------------------------------------\n")

            else:
                print(f"Pagina: {x}")
                print(f"Chaves: {chaves}")
                print(f"Offsets: {bytesOffset}")
                print(f"Filhos: {pagina.filhos}\n")
        
        print("O índice \"btree.dat\" foi impresso com sucesso!")


    def gerenciador(self, chave : int, byteOffset : int):
        raiz : int = self.ler_raiz()
        chavePro, filhoDpro, promocao, byteoffsetPro = self.inserir_na_arvore(chave, byteOffset, raiz)
        if promocao:
            pagina = Pag(self.ORDEM)
            self.add_q_paginas()
            dado = [chavePro, byteoffsetPro]
            pagina.chaves[0] = dado
            pagina.filhos[0] = raiz
            pagina.filhos[1] = filhoDpro
            pagina.n_chaves += 1
            raiz = self.novo_rrn()
            self.escrever_raiz(raiz)
            self.escrever_pagina(raiz, pagina)