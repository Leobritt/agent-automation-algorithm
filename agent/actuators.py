from .utils import DIRECTIONS

class Actuators:
    def __init__(self, env, i: int, j: int, direction: str):
        # armazena referência ao ambiente e estado local (posição e direção)
        self.env = env
        self.i = i
        self.j = j
        self.dir = direction

    def set_direction(self, new_dir: str):
        # atualiza a direção se for uma direção válida
        if new_dir in DIRECTIONS:
            self.dir = new_dir

    def move(self) -> tuple[bool, int, int]:
        # calcula o delta a partir da direção atual e a nova posição candidata
        di, dj = DIRECTIONS[self.dir]
        ni, nj = self.i + di, self.j + dj

        # logs de depuração para inspecionar a tentativa de movimento
        print(f"[DEBUG] Trying to move {self.dir}: delta=({di},{dj}), new_pos=({ni},{nj})")
        cell_value = self.env.cell(ni, nj)
        print(f"[DEBUG] Cell value at ({ni},{nj}): {cell_value}")

        # se a célula não for parede ('X'), atualiza a posição local e retorna sucesso
        if cell_value != 'X':
            # evita reatribuição desnecessária à mesma posição
            if (ni, nj) != (self.i, self.j):
                self.i, self.j = ni, nj
            return True, ni, nj
        # movimento inválido (parede) -> retorna falso e posição atual
        return False, self.i, self.j
