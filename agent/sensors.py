from typing import List, Dict
from .utils import DIRECTIONS

class Sensors:
    def __init__(self, env, i: int, j: int, direction: str):
        # referência ao ambiente e estado local (posição e direção)
        self.env = env
        self.i = i
        self.j = j
        self.dir = direction

    def get_sensor(self) -> List[List[str]]:
        # retorna uma matriz 3x3 com o entorno do agente consultando o ambiente
        return self.env.get_sensor(self.i, self.j, self.dir)

    def food_counts_8dirs(self) -> Dict[str, int]:
        i0, j0 = self.i, self.j
        counts: Dict[str, int] = {k: 0 for k in ("N", "NE", "E", "SE", "S", "SW", "W", "NW")}

        for i in range(self.env.height):
            for j in range(self.env.width):
                if i == i0 and j == j0:
                    continue
                if self.env.grid[i][j] != 'o':
                    continue

                di = i - i0
                dj = j - j0

                if di < 0 and dj == 0:
                    counts["N"] += 1
                elif di == 0 and dj > 0:
                    counts["E"] += 1
                elif di > 0 and dj == 0:
                    counts["S"] += 1
                elif di == 0 and dj < 0:
                    counts["W"] += 1
                elif di < 0 and dj > 0:
                    counts["NE"] += 1
                elif di > 0 and dj > 0:
                    counts["SE"] += 1
                elif di > 0 and dj < 0:
                    counts["SW"] += 1
                elif di < 0 and dj < 0:
                    counts["NW"] += 1

        return counts
