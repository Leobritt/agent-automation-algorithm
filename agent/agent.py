from typing import Optional, List

from agent.utils import DIRECTIONS
from .sensors import Sensors
from .actuators import Actuators
from .memory import Memory
from .planner import Planner

class Agent:
    def __init__(self, env, initial_direction: str = 'N', target_food: Optional[int] = None):
        self.env = env
        self.i, self.j = self.env.entry
        self.dir = initial_direction

        self.steps = 0
        self.collected_food = 0
        self.target_food = target_food if target_food is not None else self.env.total_food

        # Componentes
        self.sensors = Sensors(env, self.i, self.j, self.dir)
        self.actuators = Actuators(env, self.i, self.j, self.dir)
        self.memory = Memory()
        self.planner = Planner(self.memory.memory, self.memory.visits)

        self.plan: List[str] = []
        self._update_memory()

    def _update_memory(self):
        sensor = self.sensors.get_sensor()
        self.memory.update(self.i, self.j, sensor, self.env)

    def set_direction(self, new_dir: str):
        """Atualiza a direção do agente e sincroniza os componentes."""
        if new_dir in DIRECTIONS:
            self.dir = new_dir
            # keep sensors and actuators in sync
            try:
                self.sensors.dir = new_dir
                self.actuators.dir = new_dir
            except Exception:
                pass

    def move(self) -> bool:
        """Realiza um movimento através de Actuators e atualiza estado e memória do agente.

        Retorna True se o movimento ocorreu, False caso contrário.
        """
        prev = (self.i, self.j)
        # sincroniza actuators/sensors com o estado atual do agente
        self.actuators.i, self.actuators.j = self.i, self.j
        self.actuators.dir = self.dir
        self.sensors.i, self.sensors.j = self.i, self.j
        self.sensors.dir = self.dir

        ok, ni, nj = self.actuators.move()

        if ok and (ni, nj) != prev:
            # atualiza a posição do agente
            self.i, self.j = ni, nj
            self.steps += 1
            # coleta comida se presente
            if self.env.collect_if_food(self.i, self.j):
                self.collected_food += 1
            # atualiza last_position na memória para evitar bounce
            try:
                self.memory.last_position = prev
            except Exception:
                pass
            # atualiza memória e sensores
            self._update_memory()
            # sincroniza posições nos componentes
            self.actuators.i, self.actuators.j = self.i, self.j
            self.sensors.i, self.sensors.j = self.i, self.j
            return True

        return False

    def step(self):
        if not self.plan:
            self._plan()

        if self.plan:
            next_dir = self.plan.pop(0)
            self.set_direction(next_dir)
            self.move()
            return

        # Fallback 1: Explorar vizinho desconhecido e evitar retornar para last_position quando possível
        for d in self._ordered_directions():
            di, dj = DIRECTIONS[d]
            q = (self.i + di, self.j + dj)
            if q not in self.memory.memory and self.env.cell(*q) != 'X':
                self.set_direction(d)
                self.move()
                return

        # Fallback 2: Andar para vizinho conhecido livre, evitando reversão imediata
        for d in self._ordered_directions():
            di, dj = DIRECTIONS[d]
            q = (self.i + di, self.j + dj)
            if self.memory.memory.get(q, 'X') != 'X':
                self.set_direction(d)
                self.move()
                return
        
    # ===== ESTADO =====
    def finished(self) -> bool:
        at_exit = (self.i, self.j) in self.env.exits
        return self.collected_food >= self.target_food and at_exit

    def score(self) -> int:
        return self.collected_food * 10 - self.steps

    def _plan(self):
        origin = (self.i, self.j)

        # 1) Comida conhecida mais próxima
        foods = [p for p, ch in self.memory.memory.items() if ch == 'o']
        if foods:
            target_set = set(foods)
            path = self.planner.bfs(origin, lambda p: p in target_set)
            if path and len(path) > 1:
                self.plan = self.planner.translate_path(path)
                return

        # 2) Fronteira de exploração mais próxima
        frontiers = []
        for (i, j), ch in self.memory.memory.items():
            if ch == 'X':
                continue
            if ch not in ('_', 'E', 'S', 'o'):
                continue
            for di, dj in DIRECTIONS.values():
                q = (i + di, j + dj)
                if q not in self.memory.memory:  # desconhecido
                    frontiers.append((i, j))
                    break
        if frontiers:
            target_set = set(frontiers)
            path = self.planner.bfs(origin, lambda p: p in target_set)
            if path and len(path) > 1:
                # sanity check: verify path steps are not walls in the real environment
                bad = [(x,y) for (x,y) in path if self.env.cell(x,y) == 'X']
                if bad:
                    # mark bad cells in memory as walls so we don't keep planning to them
                    for bx, by in bad:
                        self.memory.memory[(bx, by)] = 'X'
                else:
                    # also record memory vs env for path nodes if needed
                    self.plan = self.planner.translate_path(path)
                    return

        # 3) Se toda comida foi coletada, vai para a saída mais próxima
        if self.collected_food >= self.target_food:
            exits = [p for p, ch in self.memory.memory.items() if ch == 'S']
            if exits:
                target_set = set(exits)
                path = self.planner.bfs(origin, lambda p: p in target_set)
                if path and len(path) > 1:
                    self.plan = self.planner.translate_path(path)
                    return

        # Se nada encontrado, zera plano
        self.plan = []

    def _ordered_directions(self) -> List[str]:
        """Retorna direções ordenadas para evitar retorno imediato e priorizar células menos visitadas.

        Usa `self.memory.last_position` e `self.memory.visits`.
        """
        candidates = []
        for d, (di, dj) in DIRECTIONS.items():
            q = (self.i + di, self.j + dj)
            # skip real walls
            if self.env.cell(*q) == 'X':
                continue
            is_last = 1 if getattr(self.memory, 'last_position', None) == q else 0
            visits = self.memory.visits.get(q, 0)
            score = (is_last, visits)
            candidates.append((score, d))
        candidates.sort(key=lambda x: x[0])
        return [d for _, d in candidates]
