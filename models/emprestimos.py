from datetime import date

class Emprestimo:
    def __init__(self, codigo_equipamento, codigo_usuario, data_retirada, data_devolucao, finalizado = False, data_retorno = None):
        self.codigo_equipamento = codigo_equipamento
        self.codigo_usuario = codigo_usuario
        self.data_retirada = data_retirada
        self.data_devolucao = data_devolucao
        self.finalizado = finalizado
        self.data_retorno = data_retorno

    def esta_em_atraso(self):
        if self.finalizado:
            return False
        data_atual = date.today()
        return data_atual > self.data_devolucao

    def esta_ativo(self):
        if self.finalizado:
            return False

        return not self.esta_em_atraso()

    def finalizar(self, data_retorno):
        self.finalizado = True
        self.data_retorno = data_retorno
