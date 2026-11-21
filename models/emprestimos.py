from datetime import date


class Emprestimo:
    def __init__(self, codigo, codigo_equipamento, codigo_usuario, data_retirada,
                 data_devolucao, finalizado=False, data_retorno=None):
        self.codigo = str(codigo).strip().lower()
        self.codigo_equipamento = str(codigo_equipamento).strip().lower()
        self.codigo_usuario = str(codigo_usuario).strip().lower()
        self.data_retirada = data_retirada
        self.data_devolucao = data_devolucao
        self._finalizado = bool(finalizado)
        self.data_retorno = data_retorno
        if self._finalizado and self.data_retorno is None:
            raise ValueError("Empréstimo finalizado precisa ter data de retorno.")

    @property
    def finalizado(self):
        return self._finalizado

    def esta_em_atraso(self, hoje=None):
        if self._finalizado:
            return False
        return (hoje or date.today()) > self.data_devolucao

    def esta_ativo(self):
        return not self._finalizado

    def finalizar(self, data_retorno):
        if self._finalizado:
            raise ValueError("Este empréstimo já foi finalizado.")
        if data_retorno < self.data_retirada:
            raise ValueError("A data de retorno não pode ser anterior à retirada.")
        self._finalizado = True
        self.data_retorno = data_retorno
