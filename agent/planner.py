from collections import deque
from typing import Dict, List, Optional, Tuple
from .utils import DIRECTIONS, DELTA_TO_DIR

class Planner:
    """Planejador simples baseado em BFS que usa a memória local do agente."""
    def __init__(self, memory, visits):
        self.memory = memory
        self.visits = visits

    def bfs(self, start: Tuple[int, int], goal: callable) -> Optional[List[Tuple[int, int]]]:
        queue = deque([start])
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        while queue:
            u = queue.popleft()
            if goal(u):
                path: List[Tuple[int, int]] = []
                v = u
                while v is not None:
                    path.append(v)
                    v = came_from[v]
                path.reverse()
                return path
            neighbors = self._free_neighbors(u)
            # prioriza vizinhos menos visitados para reduzir loops
            neighbors.sort(key=lambda x: self.visits.get(x, 0))
            for v in neighbors:
                if v not in came_from:
                    came_from[v] = u
                    queue.append(v)
        return None

    def translate_path(self, path: List[Tuple[int, int]]) -> List[str]:
        directions: List[str] = []
        for k in range(1, len(path)):
            i0, j0 = path[k - 1]
            i1, j1 = path[k]
            di, dj = i1 - i0, j1 - j0
            d = DELTA_TO_DIR.get((di, dj))
            if d:
                directions.append(d)
        return directions


    def _free_neighbors(self, p: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Retorna vizinhos livres (não paredes) a partir da memória conhecida."""
        i, j = p
        res = []
        for di, dj in DIRECTIONS.values():
            q = (i + di, j + dj)
            ch = self.memory.get(q)
            if ch is None:
                continue
            if ch != 'X':
                res.append(q)
        return res