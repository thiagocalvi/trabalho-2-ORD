import sys, os, struct
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
    ORDEM : int
    btree : BTree

    

    if len(sys.argv) < 2:
        print("Uso: programa <opção> || programa <opção> [arquivo_operacoes]")
        return

    option = sys.argv[1]

    if option == '-c':
        #Verificar se arquivo btree.dat já existe 
        if os.path.isfile("./btree.dat"):
            #se existir pede para usuario se quer substituir
            op : str = input("Já existe um arquivo btree.dat, quer substituilo? [s/N]: ")
            if op == "N" or op == "n":
                return
        
        #Receber do usuario a ordem da arvore
        ORDEM = int(input("Informe a ordem da arvore (inteiro maior ou igual a 2): "))
        #Cria objeto btree
        btree = BTree("games.dat", ORDEM)
        #Cria o indece em btree.dat
        btree.criar_indice()
        btree.btree.close()
        
    elif option == '-p':
        #Verifica se o arquivo btree.bat existe
        if os.path.isfile("./btree.bat"):
            #se existe
            #Imprimir a arvore no cosole
            #-> chamar função btree.print_btree()
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
                    raiz : int = btree.ler_raiz()
                    chave : int = int(dado)
                    achou, rrn, pos = btree.buscar_na_arvore(chave, raiz)

                
                elif operacao == "i":

                    pass
        
    else:
        print("Opção inválida")

if __name__ == "__main__":
    main()