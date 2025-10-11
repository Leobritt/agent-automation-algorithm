import time
import subprocess
import shutil
from pathlib import Path
from typing import Optional

from agent.agent import Agent
from environment.environment import Environment

# ===== CONFIG FOR RECORDING / PLAYER =====
RECORD_VIDEO = True
VIDEO_NAME_MP4 = "agent_simulation.mp4"
VIDEO_NAME_AVI = "agent_simulation.avi"
FPS = 10.0
CELL_SIZE = 22


def render(env: Environment, ag: Agent):
    """Desenha o mapa no console com a letra da direção do agente."""
    lines = []
    for r in range(env.height):
        row = []
        for c in range(env.width):
            if (r, c) == (ag.i, ag.j):
                row.append(ag.dir)  # N/L/S/O na posição do agente
            else:
                row.append(env.grid[r][c])
        lines.append(''.join(row))
    print('\n'.join(lines))


def _try_import_cv2():
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
        return cv2, np
    except Exception:
        return None, None


def _open_videowriters(cv2, width_cells: int, height_cells: int):
    frame_size = (width_cells * CELL_SIZE, height_cells * CELL_SIZE)
    writers = {}

    # MP4
    fourcc_mp4 = cv2.VideoWriter_fourcc(*'mp4v')
    out_mp4 = cv2.VideoWriter(VIDEO_NAME_MP4, fourcc_mp4, FPS, frame_size)
    if out_mp4.isOpened():
        writers["mp4"] = out_mp4
        print(f"[VIDEO] Gravando MP4 em {VIDEO_NAME_MP4}")

    # AVI
    fourcc_avi = cv2.VideoWriter_fourcc(*'XVID')
    out_avi = cv2.VideoWriter(VIDEO_NAME_AVI, fourcc_avi, FPS, frame_size)
    if out_avi.isOpened():
        writers["avi"] = out_avi
        print(f"[VIDEO] Gravando AVI em {VIDEO_NAME_AVI}")

    if not writers:
        print("[VIDEO] Aviso: não foi possível inicializar nenhum VideoWriter")

    return writers


def _frame_from_state(cv2, np, env: Environment, ag: Agent):
    h_px = env.height * CELL_SIZE
    w_px = env.width * CELL_SIZE
    img = np.ones((h_px, w_px, 3), dtype=np.uint8) * 255

    colors = {
        'X': (0, 0, 0),         # parede
        '_': (200, 200, 200),   # corredor
        'E': (0, 255, 0),       # entrada
        'S': (255, 0, 0),       # saída
        'o': (0, 200, 200),     # comida
    }

    for i in range(env.height):
        for j in range(env.width):
            ch = env.grid[i][j]
            col = colors.get(ch, (220, 220, 220))
            y1, y2 = i * CELL_SIZE, (i + 1) * CELL_SIZE
            x1, x2 = j * CELL_SIZE, (j + 1) * CELL_SIZE
            cv2.rectangle(img, (x1, y1), (x2, y2), col, -1)

    # agente
    ai, aj = ag.i, ag.j
    cx = aj * CELL_SIZE + CELL_SIZE // 2
    cy = ai * CELL_SIZE + CELL_SIZE // 2
    cv2.circle(img, (cx, cy), CELL_SIZE // 2 - 2, (0, 0, 255), -1)

    # direção
    dx = dy = 0
    if ag.dir == 'N':
        dy = -CELL_SIZE // 2 + 3
    elif ag.dir == 'S':
        dy = CELL_SIZE // 2 - 3
    elif ag.dir == 'L':
        dx = CELL_SIZE // 2 - 3
    elif ag.dir == 'O':
        dx = -CELL_SIZE // 2 + 3
    cv2.line(img, (cx, cy), (cx + dx, cy + dy), (255, 255, 255), 2)

    return img


def main():
    map_path = Path("input") / "maze.txt"
    if not map_path.exists():
        print(f"[ERROR] Mapa não encontrado: {map_path}")
        return

    env = Environment(str(map_path))
    ag = Agent(env, initial_direction='N', target_food=env.total_food)

    print("=== AMBIENTE ===")
    print(f"Tamanho: {env.height} x {env.width}")
    print(f"Entrada: {env.entry}")
    print(f"Saídas: {env.exits}")
    print(f"Comidas: {env.total_food}\n")

    cv2 = np = None
    writers = {}
    if RECORD_VIDEO:
        cv2, np = _try_import_cv2()
        if cv2:
            writers = _open_videowriters(cv2, env.width, env.height)

    print("Mapa inicial:")
    render(env, ag)

    if writers and cv2 and np:
        frame = _frame_from_state(cv2, np, env, ag)
        for w in writers.values():
            w.write(frame)

    # loop
    max_steps = env.height * env.width * 50
    for step in range(max_steps):
        if ag.finished():
            break
        ag.step()

        print("\033[H\033[J", end="")
        render(env, ag)

        if writers and cv2 and np:
            frame = _frame_from_state(cv2, np, env, ag)
            for w in writers.values():
                w.write(frame)

        time.sleep(0.05)

    for w in writers.values():
        w.release()
    if writers:
        print(f"[VIDEO] Arquivos gerados: {VIDEO_NAME_MP4} e {VIDEO_NAME_AVI}")

    print("\nSimulação encerrada.")
    print(f"Comidas coletadas: {ag.collected_food}/{env.total_food}")
    print(f"Passos: {ag.steps}")
    print(f"Pontuação: {ag.score()}")


if __name__ == "__main__":
    main()