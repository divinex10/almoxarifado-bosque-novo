class Avaria:
    def __init__(self, codigo, codigo_equipamento, codigo_emprestimo, descricao, data_registro, resolvida = False, data_resolucao=None):
        self.codigo = codigo
        self.codigo_equipamento = codigo_equipamento
        self.codigo_emprestimo = codigo_emprestimo
        self.descricao = descricao
        self.data_registro = data_registro
        self.resolvida = resolvida
        self.data_resolucao = data_resolucao

    def resolver(self, data_resolucao):
        self.resolvida = True
        self.data_resolucao = data_resolucao

    def esta_ativa(self):
        return self.resolvida
        