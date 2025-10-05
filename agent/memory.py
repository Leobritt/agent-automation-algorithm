from typing import Dict, Set, Tuple, Optional

class Memory:
    def __init__(self):
        self.memory: Dict[Tuple[int, int], str] = {}
        self.visited: Set[Tuple[int, int]] = set()
        self.visits: Dict[Tuple[int, int], int] = {}
        self.last_position: Optional[Tuple[int, int]] = None

    def update(self, i, j, sensor, env):
        current = (i, j)
        # Sempre confia no ambiente para a célula atual
        self.memory[current] = env.cell(i, j)

        # Atualiza os vizinhos usando o ambiente real para evitar inconsistências sensor/mapa
        for r in range(3):
            for c in range(3):
                if r == 2 and c == 2:
                    continue
                ai = i + (r - 1)
                aj = j + (c - 1)
                if env.inside(ai, aj):
                    self.memory[(ai, aj)] = env.cell(ai, aj)

        self.visited.add(current)
        self.visits[current] = self.visits.get(current, 0) + 1
