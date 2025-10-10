from typing import List, Tuple  # apenas dicas de tipo

class Environment:
    def __init__(self, txt_path: str):
        # Carrega o mapa do arquivo txt e salva em uma matriz de caracteres
        self.grid: List[List[str]] = self._load(txt_path)

        # altura = número de linhas, largura = número de colunas
        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.height > 0 else 0

        # guarda onde está a entrada e todas as saídas
        self.entry = self._find('E')
        self.exits = self._find_all('S')

        # conta quantas comidas existem no mapa
        self.total_food = sum(row.count('o') for row in self.grid)

    def _load(self, path: str) -> List[List[str]]:
        # abre o arquivo de texto e lê todas as linhas (ignora linhas vazias finais)
        with open(path, 'r', encoding='utf-8') as f:
            lines = [list(l.strip('\n')) for l in f.readlines() if l.strip('\n')]
        # valida se todas as linhas têm o mesmo tamanho
        width = len(lines[0])
        assert all(len(l) == width for l in lines), "Mapa com larguras diferentes."
        return lines

    def _find(self, target: str) -> Tuple[int, int]:
        # procura a primeira ocorrência de um símbolo (ex: 'E')
        for i, row in enumerate(self.grid):
            for j, c in enumerate(row):
                if c == target:
                    return (i, j)
        raise ValueError(f"Símbolo '{target}' não encontrado no mapa.")

    # 3x3 sensor
    def get_sensor(self, i: int, j: int, direction: str) -> List[List[str]]:
        """
        Retorna uma matriz 3x3 com o entorno do agente.
        """
        sensor = [['X' for _ in range(3)] for _ in range(3)]

        # vizinhança relativa ao (i,j)
        rel = [
            (-1, -1), (-1, 0), (-1, 1),
            (0,  -1), (0,  0), (0,  1),
            (1,  -1), (1,  0), (1,  1),
        ]

        idx = 0
        for r in range(3):
            for c in range(3):
                if r == 2 and c == 2:
                    # posição de direção do agente (exigência do enunciado)
                    sensor[r][c] = direction
                else:
                    di, dj = rel[idx]
                    sensor[r][c] = self.cell(i + di, j + dj)
                idx += 1

        return sensor
    
    def _find_all(self, target: str) -> List[Tuple[int, int]]:
        # retorna todas as posições de um símbolo (ex: todas as saídas 'S')
        coords = []
        for i, row in enumerate(self.grid):
            for j, c in enumerate(row):
                if c == target:
                    coords.append((i, j))
        return coords

    def inside(self, i: int, j: int) -> bool:
        # verifica se uma posição está dentro do mapa
        return 0 <= i < self.height and 0 <= j < self.width

    def cell(self, i: int, j: int) -> str:
        # retorna o que existe na posição (i,j)
        # se estiver fora do mapa, conta como parede 'X'
        if not self.inside(i, j):
            return 'X'
        return self.grid[i][j]

    def collect_if_food(self, i: int, j: int) -> bool:
        # se houver comida na posição, substitui por '_' e retorna True
        if self.grid[i][j] == 'o':
            self.grid[i][j] = '_'
            return True
        return False
