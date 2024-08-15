import struct

# Abre o arquivo em modo de leitura binária
file = open("games.dat", 'rb')

# Função para extrair o identificador do registro
def retorna_identificador_registro(registro: str) -> int:
    registro_list = registro.split('|')
    return int(registro_list[0])

try:
    # Lê a quantidade de registros
    quantidade_registros = struct.unpack('I', file.read(4))[0]
    print(f"Quantidade de registros : {quantidade_registros}")

    while True:
        # Lê o tamanho do registro
        tamanho_registro_bytes = file.read(2)
        if not tamanho_registro_bytes:
            break  # Fim do arquivo

        tamanho_registro = struct.unpack("H", tamanho_registro_bytes)[0]

        if tamanho_registro == 0:
            break

        # Lê o registro
        registro_bytes = file.read(tamanho_registro)
        if not registro_bytes:
            break  # Fim do arquivo

        registro = registro_bytes.decode("utf-8")
        print(f"Registros de tamanho {tamanho_registro} : {registro}")
        print(f"Identificador {retorna_identificador_registro(registro)}")

finally:
    file.close()




    def get_identificador_registro(self, registro:str) -> int:
        #Retorna o identificador (int) do registo recebido por parametro
        registro_lista : list[str] = registro.split('|')
        return int(registro_lista[0])

    def get_registro(self) -> tuple:
        #retorna um regitro do arquivo, seu tamanho e seu byteOffset recebido por parametro
        #le o arquivo de forma sequencial
        try:
            tamanho_registro : int = struct.unpack("H", self.arquivo_games.read(2))
            registro : str = self.arquivo_games.read(tamanho_registro).decode("utf-8")
            byteOffset : int = tamanho_registro + 4 + 2
            return (registro, tamanho_registro, byteOffset)
        except:
            return (" ", " ", " ")

    def escrever_raiz(self, rrn_raiz) -> None:
        self.arquivo_games.seek(0)
        self.arquivo_games.write(struct.pack("I", rrn_raiz))

    def criar_arvore(self) -> None:
        self.btree = open("btree.bat", 'wb')
        self.arquivo_games.seek(4) #cabeçalho do arquivo


        #ciar a pagina e inserir no arquivo btree.bat

        fimDoArquivo : bool = False
        registro : tuple = self.get_registro()
        if registro[0] == " " : fimDoArquivo = True
        pagina = Pag(self.ORDEM)

        while fimDoArquivo == False:
            if pagina.pagina_cheia(): pagina = Pag(self.ORDEM)

            pagina.inserir_na_pagina([registro[0], registro[2]])

            registro = self.get_registro()
            if registro[0] == " " : fimDoArquivo = True
            pass
