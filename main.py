import time
from pathlib import Path
from agent.agent import Agent
from environment.environment import Environment

def render(env: Environment, ag: Agent):
    """Desenha o mapa com o agente (mostra a letra da direção na posição atual)."""
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

def main():
    # Arquivo do labirinto (input/maze.txt)
    map_path = Path("input") / "maze.txt"
    if not map_path.exists():
        print(f"[ERRO] Não foi possível localizar o arquivo do mapa em: {map_path}")
        return

    # Instancia ambiente e agente
    env = Environment(str(map_path))
    # passa explicitamente a quantidade de comidas para cumprir o enunciado literalmente
    ag = Agent(env, initial_direction='N', target_food=env.total_food)

    # Informações do ambiente
    print("=== AMBIENTE ===")
    print(f"Tamanho (alt x larg): {env.height} x {env.width}")
    print(f"Entrada (E): {env.entry}")
    print(f"Saídas (S): {env.exits}")
    print(f"Total de comidas no mapa: {env.total_food}\n")

    # Render inicial
    print("Mapa inicial:")
    render(env, ag)
    time.sleep(0.03)

    # Loop de simulação
    max_steps = env.height * env.width * 50  # trava de segurança (aumentado)
    # Adiciona um limite de segurança para evitar loops infinitos
    max_iterations = 1000
    for iteration in range(max_iterations):
        if ag.finished():
            break
        ag.step()

        # "animação" no console
        print("\033[H\033[J", end="")  # limpa console (ANSI)
        render(env, ag)
        time.sleep(0.05)

    else:
        print("\n[AVISO] Limite de iterações atingido — possível loop detectado.")

    # Resultado final
    print("\nSimulação encerrada.")
    print(f"Comidas coletadas: {ag.collected_food}/{env.total_food}")
    print(f"Movimentos realizados: {ag.steps}")
    print(f"Pontuação final: {ag.score()}")

if __name__ == "__main__":
    main()