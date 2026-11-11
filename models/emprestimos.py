from datetime import date

class Emprestimo:
    def __init__(self, codigo_equipamento, codigo_usuario, data_retirada, data_devolucao, finalizado = False):
        self.codigo_equipamento = codigo_equipamento
        self.codigo_usuario = codigo_usuario
        self.data_retirada = data_retirada
        self.data_devolucao = data_devolucao
        self.finalizado = finalizado

    def esta_em_atraso(self):
        if self.finalizado:
            return False
        data_atual = date.today()
        return data_atual > self.data_devolucao

    def esta_ativo(self):
        if self.finalizado:
            return False

        return not self.esta_em_atraso()

    def finalizar(self):
        self.finalizado = True