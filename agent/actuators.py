class Actuators:
    def __init__(self):
        """
        Inicializa os atuadores com a direção padrão.
        """
        self.direction = "UP"  # Direção inicial padrão 


    def set_direction(self, direction):
        """
        ele não move o agente, apenas ajusta a direção
        :param direction: Nova direção ("UP", "DOWN", "LEFT", "RIGHT").
        """
        self.direction = direction

    def move(self, position):
        """
        Move o agente na direção atual.
        :param position: Tupla (x, y) representando a posição atual do agente.
        :return: Nova posição (x, y) após o movimento.
        """

        """desempacota a tupla position em x e y"""
        x, y = position

        """verifica a direção e ajusta x ou y conforme necessário"""
        """caso haja troca do left para o right no eixo y iria  inverter o eixo"""
        if self.direction == "UP":
            x -= 1
        elif self.direction == "DOWN":
            x += 1
        elif self.direction == "LEFT":
            y -= 1
        elif self.direction == "RIGHT":
            y += 1
            """retorna a tupla com a nova posição"""
        return x, y