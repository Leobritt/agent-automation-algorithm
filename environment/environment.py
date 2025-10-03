class Environment:
    def __init__(self, map_file):
        self.map = self.load_map(map_file)

    def load_map(self, map_file):
        maze = []
        """
        O with as context manager é usado para abrir o arquivo
        garantindo que ele seja fechado corretamente após a leitura.
        'r' = modo de leitura
        """
        with open(map_file, 'r') as file:
            """Cada iteração da for retorna uma string 
            correspondente a uma linha do arquivo"""
            for line in file:
                """
                maze.append(...) adiciona essa lista de caracteres como uma nova linha na matriz.
                list(string) transforma a string em lista de caracteres.
                line.strip() Remove espaços em branco e 
                quebras de linha do início e do fim da string.
                """
                maze.append(list(line.strip()))
        return maze

    def get_perception(self, position):
        """
        esse método devolve uma matriz 3x3 em volta da posição atual do agente.
        tupla (x, y) representando a posição atual do agente.
        """
        x, y = position 
        """
        cria lista vazia para armazenar a percepção
        as 3 linhas da percepção.
        """
        perception = []

        """
        range(inicio, fim) gera uma sequência de 
        números de inicio até fim - 1 -que não é incluido
        x - 1 a linha de cima do agente
        x a linha onde o agente está
        x + 1 a linha de baixo do agente

        0
        1
        2 -> agente está aqui 
        3

        x = 2
        x - 1 = 1 (linha de cima do agente)
        x = 2 (linha do agente) 
        x + 1 = 3 (linha de baixo do agente)
        range(1, 4) -> 1, 2, 3
        """
        for i in range(x - 1, x + 2):
            """armazena valores de uma linha da percepção"""
            row = []
            """percorre as colunas vizinhas (esquerda, atual, direita)"""
            for j in range(y - 1, y + 2):
                """
                verifica se os índices estão dentro dos limites do mapa 
                len(self.map) quantidade de linhas (altura).
                len(self.map[0]) quantidade de colunas (largura).
                """
                if 0 <= i < len(self.map) and 0 <= j < len(self.map[0]):
                    """
                    (self.map[i][j]) Se a posição (i, j) for válida, 
                    pega o caractere correspondente do mapa e adiciona na linha da percepção.
                    """
                    row.append(self.map[i][j])
                else:
                    """Se a posição (i, j) for fora do mapa, adiciona '#'"""
                    row.append('#')  # Paredes fora do limite
            """Depois de preencher uma linha de 3 elementos, adiciona essa linha à matriz de percepção."""
            perception.append(row)
            """Retorna a percepção final: uma matriz 3x3 (lista de listas)."""
        return perception