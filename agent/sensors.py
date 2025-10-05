from typing import List
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
