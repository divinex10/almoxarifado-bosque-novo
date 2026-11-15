class Reserva:
    def __init__(self, codigo, codigo_equipamento, codigo_usuario, data_inicio, data_fim, cancelada=False, atendida=False):
        self.codigo = codigo
        self.codigo_equipamento = codigo_equipamento
        self.codigo_usuario = codigo_usuario
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.cancelada = cancelada
        self.atendida = atendida

    def cancelar(self):
        self.cancelada = True
        

    def marcar_como_atendida(self):
        self.atendida = True
        

    def esta_ativa(self):
        return not self.cancelada and not self.atendida
         

