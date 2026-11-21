class Reserva:
    def __init__(self, codigo, codigo_equipamento, codigo_usuario, data_inicio,
                 data_fim, cancelada=False, atendida=False):
        self.codigo = str(codigo).strip().lower()
        self.codigo_equipamento = str(codigo_equipamento).strip().lower()
        self.codigo_usuario = str(codigo_usuario).strip().lower()
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self._cancelada = bool(cancelada)
        self._atendida = bool(atendida)

    @property
    def cancelada(self):
        return self._cancelada

    @property
    def atendida(self):
        return self._atendida

    def cancelar(self):
        if not self.esta_ativa():
            raise ValueError("Somente reservas ativas podem ser canceladas.")
        self._cancelada = True

    def marcar_como_atendida(self):
        if not self.esta_ativa():
            raise ValueError("Somente reservas ativas podem ser atendidas.")
        self._atendida = True

    def esta_ativa(self):
        return not self._cancelada and not self._atendida
