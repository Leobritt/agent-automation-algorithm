from collections import deque
from typing import Dict, List, Optional, Set, Tuple
from environment.environment import Environment

# Movements (row, column)
DIRECTIONS = {
    'N': (-1, 0),
    'S': (1, 0),
    'E': (0, 1),
    'W': (0, -1),
}

DELTA_TO_DIR = {v: k for k, v in DIRECTIONS.items()}

class Agent:
    def __init__(self, environment: Environment, initial_direction: str = 'N', target_food: Optional[int] = None):
        # Inicializa o ambiente e os componentes do agente
        self.env = environment
        self.i, self.j = self.env.entry
        self.dir = initial_direction

        # Estatísticas do agente
        self.steps = 0
        self.collected_food = 0
        # The number of target food can now be explicitly passed during instantiation
        self.target_food = target_food if target_food is not None else self.env.total_food

        # Memory of the discovered map
        self.memory: Dict[Tuple[int, int], str] = {}
        self.visited: Set[Tuple[int, int]] = set()
        self.visits: Dict[Tuple[int, int], int] = {}  # Count of times visited
        self.plan: List[str] = []

        self.last_position: Optional[Tuple[int, int]] = None  # Anti-bounce

        self._update_memory()

    # ===== SENSORS =====
    def get_sensor(self) -> List[List[str]]:
        return self.env.get_sensor(self.i, self.j, self.dir)

    def _update_memory(self):
        sensor = self.get_sensor()
        current = (self.i, self.j)
        self.memory[current] = self.env.cell(self.i, self.j)

        for r in range(3):
            for c in range(3):
                ai = self.i + (r - 1)
                aj = self.j + (c - 1)
                if r == 2 and c == 2:
                    continue  # [2][2] stores the direction letter
                self.memory[(ai, aj)] = sensor[r][c]

        self.visited.add(current)
        self.visits[current] = self.visits.get(current, 0) + 1

    # ===== ACTUATORS =====
    def set_direction(self, new_dir: str):
        if new_dir in DIRECTIONS:
            self.dir = new_dir

    def move(self) -> bool:
        di, dj = DIRECTIONS[self.dir]
        ni, nj = self.i + di, self.j + dj

        if self.env.cell(ni, nj) != 'X':
            prev = (self.i, self.j)
            self.i, self.j = ni, nj
            self.steps += 1
            if self.env.collect_if_food(self.i, self.j):
                self.collected_food += 1
            self.last_position = prev
            self._update_memory()
            return True
        return False

    # ===== PLANNING =====
    def _free_neighbors_in_memory(self, p: Tuple[int, int]) -> List[Tuple[int, int]]:
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

    def _bfs_until_predicate(self, start: Tuple[int, int], goal: callable) -> Optional[List[Tuple[int, int]]]:
        queue = deque([start])
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        while queue:
            u = queue.popleft()
            if goal(u):
                # Reconstruct path
                path: List[Tuple[int, int]] = []
                v = u
                while v is not None:
                    path.append(v)
                    v = came_from[v]
                path.reverse()
                return path
            # Expand prioritizing less visited nodes (reduces chance of loops)
            neighbors = self._free_neighbors_in_memory(u)
            neighbors.sort(key=lambda x: self.visits.get(x, 0))
            for v in neighbors:
                if v not in came_from:
                    came_from[v] = u
                    queue.append(v)
        return None

    def _translate_path_to_directions(self, path: List[Tuple[int, int]]) -> List[str]:
        directions: List[str] = []
        for k in range(1, len(path)):
            i0, j0 = path[k - 1]
            i1, j1 = path[k]
            di, dj = i1 - i0, j1 - j0
            d = DELTA_TO_DIR.get((di, dj))
            if d:
                directions.append(d)
        return directions

    def _exploration_frontiers(self) -> List[Tuple[int, int]]:
        frontiers = []
        for (i, j), ch in self.memory.items():
            if ch == 'X':
                continue
            if ch not in ('_', 'E', 'S', 'o'):
                continue
            for di, dj in DIRECTIONS.values():
                q = (i + di, j + dj)
                if q not in self.memory:  # Unknown
                    frontiers.append((i, j))
                    break
        return frontiers

    def _plan(self):
        origin = (self.i, self.j)

        # 1) Closest known food
        foods = [p for p, ch in self.memory.items() if ch == 'o']
        if foods:
            target_set = set(foods)
            path = self._bfs_until_predicate(origin, lambda p: p in target_set)
            if path and len(path) > 1:
                self.plan = self._translate_path_to_directions(path)
                return

        # 2) Closest exploration frontier
        frontiers = self._exploration_frontiers()
        if frontiers:
            target_set = set(frontiers)
            path = self._bfs_until_predicate(origin, lambda p: p in target_set)
            if path and len(path) > 1:
                self.plan = self._translate_path_to_directions(path)
                return

        # 3) If all food is collected, closest exit
        if self.collected_food >= self.target_food:
            exits = [p for p, ch in self.memory.items() if ch == 'S']
            if exits:
                target_set = set(exits)
                path = self._bfs_until_predicate(origin, lambda p: p in target_set)
                if path and len(path) > 1:
                    self.plan = self._translate_path_to_directions(path)
                    return

        self.plan = []

    # ===== ORDER DIRECTIONS WITH ANTI-BOUNCE =====
    def _ordered_directions(self) -> List[str]:
        """Order directions prioritizing not returning to last_position and less visited nodes."""
        candidates = []
        for d, (di, dj) in DIRECTIONS.items():
            q = (self.i + di, self.j + dj)
            if self.env.cell(*q) == 'X':
                continue
            score = (
                0 if (self.last_position is None or q != self.last_position) else 1,
                self.visits.get(q, 0)
            )
            candidates.append((score, d, q))
        # First: avoid returning (score[0]==0), then prioritize less visited
        candidates.sort(key=lambda x: x[0])
        return [d for _, d, _ in candidates]

    # ===== ONE STEP =====
    def step(self):
        if not self.plan:
            self._plan()

        if self.plan:
            next_dir = self.plan.pop(0)
            self.set_direction(next_dir)
            self.move()
            return

        # Fallback 1: Explore unknown neighbor and avoid returning to last_position if possible
        for d in self._ordered_directions():
            di, dj = DIRECTIONS[d]
            q = (self.i + di, self.j + dj)
            if q not in self.memory and self.env.cell(*q) != 'X':
                self.set_direction(d)
                self.move()
                return

        # Fallback 2: Move to a known free neighbor, avoiding immediate reversal
        for d in self._ordered_directions():
            di, dj = DIRECTIONS[d]
            q = (self.i + di, self.j + dj)
            if self.memory.get(q, 'X') != 'X':
                self.set_direction(d)
                self.move()
                return

    # ===== STATE =====
    def finished(self) -> bool:
        at_exit = (self.i, self.j) in self.env.exits
        return self.collected_food >= self.target_food and at_exit

    def score(self) -> int:
        return self.collected_food * 10 - self.steps