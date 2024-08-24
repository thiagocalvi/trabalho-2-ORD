import sys, os, struct
from Pag import Pag
from BTree import BTree

def ler_opracoes(arquivo_operacoes):
    linha : str = arquivo_operacoes.readline()
    if linha != " ":
        conteudo : list[str] = linha.split(maxsplit=1)
        operacao = conteudo[0]
        dado : str = conteudo[1].rsplit("\n")
        return operacao, dado
    
    else:
        return None, None

def main():
    ORDEM : int = 8
    bTree : BTree

    

    if len(sys.argv) < 2:
        print("Uso: programa <opção> || programa <opção> [arquivo_operacoes]")
        return

    option = sys.argv[1]
    
    bTree = BTree("games.dat", ORDEM)

    if option == '-c':
        
        btreeFile = open("btree.dat", 'wb+')
        bTree.setBtree(btreeFile)

        bTree.escrever_raiz(0)
    
        raiz = bTree.gerenciadorInsercao(0)
        bTree.escrever_raiz(raiz)
        bTree.btree.close()
        
    elif option == '-p':
        #Verifica se o arquivo btree.dat existe
        if os.path.isfile("./btree.dat"):
            #se existe
            #Imprimir a arvore no cosole
            #-> chamar função btree.print_btree()
            btreeFile = open("btree.dat", 'rb')
            bTree.setBtree(btreeFile)
            bTree.print_btree()
            bTree.btree.close()
            pass
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
                    raiz : int = bTree.ler_raiz()
                    chave : int = int(dado)
                    achou, rrn, pos = bTree.buscar_na_arvore(chave, raiz)

                
                elif operacao == "i":

                    pass
        
    else:
        print("Opção inválida")

if __name__ == "__main__":
    main()