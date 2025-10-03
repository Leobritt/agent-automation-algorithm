class Memory:
    def __init__(self, rows, cols):
        """
        Inicializa a memória local do agente com um mapa vazio.
        """

        # self.discovered_map cria uma matriz rows × cols preenchida com "?" (interrogações).
        # [["?"] * cols for _ in range(rows)] é uma list comprehension que gera as linhas.
        self.discovered_map = [["?"] * cols for _ in range(rows)]  # Mapa descoberto inicial vazio
        self.visited_positions = set()  # Conjunto de posições visitadas
        """TODO: descobrir pq usar o set()"""

    def update_memory(self, position, perception):
        """
        Atualiza a memória local do agente com base na percepção atual.
        :param position: Tupla (x, y) representando a posição atual do agente.
        :param perception: Matriz 3x3 representando a percepção ao redor do agente.
        """

        """desempacota a tupla position em x e y"""
        x, y = position
        """i e j vão de -1 até 1 (3 valores cada → total 9 células). o range ignora o ultimo valor"""
        """
        Esses i e j são deslocamentos relativos à posição do agente.
        (i, j) = (0, 0) → posição do próprio agente.
        (i, j) = (-1, 0) → célula acima.
        (i, j) = (0, +1) → célula à direita.
        """
        for i in range(-1, 2):
            for j in range(-1, 2):
                """
                (map_x, map_y) ajusta para a posição real no mapa global.
                 transforma os deslocamentos locais (i, j) em coordenadas globais no discovered_map.
                 Se o agente está em (2, 3) no mapa (posição atual do agente),
                 e (i, j) = (-1, 0), então (map_x, map_y) = (1, 3) → uma linha acima a mesma coluna.
                """
                map_x, map_y = x + i, y + j
                """
                map_x verifica está dentro das linhas do mapa descoberto
                map_y verifica está dentro das colunas do mapa descoberto
                Se estiver, atualiza a célula correspondente na memória com o valor da percepção.
                sem essa verificação, poderia tentar acessar índices fora dos limites da matriz, causando erros.
                """
                if 0 <= map_x < len(self.discovered_map) and 0 <= map_y < len(self.discovered_map[0]):
                    """
                    perception é uma matriz 3x3, mas i e j vão de -1 a 1.
                    (i, j) = (-1, -1) → percepção [0][0] (canto superior esquerdo).
                    """

                    """
                      o perception sempre tem 3 linhas e 3 colunas índices de 0 até 2.
                      Mas i e j vão de -1 a 1.
                      Se tentássemos acessar perception[-1][-1], 
                      daria errado porque queremos o canto superior esquerdo, que é [0][0].
                      Para alinhar os intervalos, basta somar 1 a i e j.
                    """
                    self.discovered_map[map_x][map_y] = perception[i + 1][j + 1]
                    """adiciona a posição atual ao conjunto de posições visitadas"""
        self.visited_positions.add(position)

    def is_visited(self, position):
        """
        Verifica se uma posição já foi visitada.
        :param position: Tupla (x, y) representando a posição a ser verificada.
        :return: True se a posição já foi visitada, False caso contrário.
        """
        return position in self.visited_positions

    def print_memory(self):
        """
        Imprime o mapa descoberto na saída padrão.
        """
        for row in self.discovered_map:
            print("".join(row))