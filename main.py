import sys, os, struct
from Pag import Pag
from BTree import BTree

def ler_opracoes(arquivo_operacoes):
    try:
            linha : str = arquivo_operacoes.readline()
            conteudo : list[str] = linha.split(" ", maxsplit=1)
            operacao = conteudo[0]
            dado : str = conteudo[1].rsplit("\n")
            return operacao, dado
    except:
            return None, None

def main():
    ORDEM : int = 8
    bTree : BTree

    if len(sys.argv) < 2:
        print("Uso: programa <opção> || programa <opção> [arquivo_operacoes]")
        return

    option = sys.argv[1]  
    bTree = BTree(ORDEM)
    arquivo_games_name = "games.dat"

    if option == '-c':
        btreeFile = open("btree.dat", 'wb+')
        arquivo_games = open(arquivo_games_name, 'rb+')

        bTree.setBtree(btreeFile)
        bTree.setArqGames(arquivo_games)

        bTree.criar_indice()

        bTree.btree.close()
        bTree.arquivo_games.close()    

        print("Indice criado!\n")  

    elif option == '-p':
        #Verifica se o arquivo btree.dat existe
        if os.path.isfile("./btree.dat"):
            btreeFile = open("btree.dat", 'rb')
            bTree.setBtree(btreeFile)
            bTree.print_btree()
            bTree.btree.close()
            
        else:
            #se não existe lança um erro
            raise FileNotFoundError("Arquivo btree.bat não foi encontrado")
    
    elif option == '-e':
        if len(sys.argv) < 3:
            raise ValueError("Erro: arquivo de operações não especificado")
        else:
            #ler e executar as opração do arquivo de operações
            nome_arquivo_operacoes : str = sys.argv[2]
            arquivo_operacoes = open(nome_arquivo_operacoes, 'r')
            operacao, dado = ler_opracoes(arquivo_operacoes)

            while operacao != None:
                if operacao == "b":
                    btreeFile = open("btree.dat", 'rb')
                    bTree.setBtree(btreeFile)
                    raiz : int = bTree.ler_raiz()
                    chave : int = int(dado[0])
                    achou, rrn, pos = bTree.buscar_na_arvore(chave, raiz)
                    
                    if achou:
                        pagina : Pag = bTree.ler_pagina(rrn)
                        byteOffset = pagina.chaves[pos][1]
                        arquivo_games = open(arquivo_games_name, 'rb')
                        bTree.setArqGames(arquivo_games)
                        bTree.arquivo_games.seek(byteOffset)
                        tam = struct.unpack("H", arquivo_games.read(2))[0]
                        reg = bTree.arquivo_games.read(tam).decode()
                        print(f"Registro de chave {chave} encontrado {reg}\n")
                        bTree.arquivo_games.close()
                        bTree.btree.close()
                    else:
                        bTree.btree.close()
                        print("Registro não encontrado!\n")

                elif operacao == "i":
                    btreeFile = open("btree.dat", 'rb+')
                    bTree.setBtree(btreeFile)

                    arquivo_games = open(arquivo_games_name, 'rb+')
                    bTree.setArqGames(arquivo_games)
                    dado = dado[0]
                    tam = len(dado)
                    chave = int(dado.split("|")[0])

                   
                    try:
                         #inserir no arquivo btree.dat
                        bTree.gerenciador(chave, byteOffset)
                        
                        bTree.arquivo_games.seek(0, 2)
                        byteOffset : int = bTree.arquivo_games.tell()
                        print(f"Registro sendo inserido: {dado} \n")
                        bTree.arquivo_games.write(struct.pack("H", tam))
                        bTree.arquivo_games.write(dado.encode())
                        
                        bTree.arquivo_games.seek(0)
                        q_reg : int = struct.unpack("I" , bTree.arquivo_games.read(4))[0]
                        q_reg+=1
                        bTree.arquivo_games.seek(0)
                        bTree.arquivo_games.write(struct.pack("I", q_reg))

                        bTree.arquivo_games.close()
                        bTree.btree.close()
                    except:
                        print(f"Registro de chave {chave} duplicado!\n")
                        bTree.arquivo_games.close()
                        bTree.btree.close()

                operacao, dado = ler_opracoes(arquivo_operacoes)
        
            print("Operaçãoes finalizadas!")
            arquivo_operacoes.close()
    else:
        print("Opção inválida")

if __name__ == "__main__":
    main()