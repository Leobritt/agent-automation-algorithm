# Movimentos (linha, coluna)
DIRECTIONS = {
    'N': (-1, 0),
    'S': (1, 0),
    'E': (0, 1),
    'W': (0, -1),
}

DELTA_TO_DIR = {v: k for k, v in DIRECTIONS.items()}
