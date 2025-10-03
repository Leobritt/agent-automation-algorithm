class Sensors:
    def __init__(self, environment):
        self.environment = environment

        """recebe uma tupla (x, y) representando a posição atual do agente."""
    def get_sensor_data(self, position):
        """
        o sensor não tem lógica própria, ele apenas consulta o ambiente
        para obter a percepção ao redor da posição atual do agente.
        sensores só percebem, não decidem nem agem.
        """
        return self.environment.get_perception(position)