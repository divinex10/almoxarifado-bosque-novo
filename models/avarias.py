class Avaria:
    def __init__(self, codigo, codigo_equipamento, codigo_emprestimo, descricao,
                 data_registro, resolvida=False, data_resolucao=None):
        self.codigo = str(codigo).strip().lower()
        self.codigo_equipamento = str(codigo_equipamento).strip().lower()
        self.codigo_emprestimo = str(codigo_emprestimo).strip().lower()
        self.descricao = str(descricao).strip()
        self.data_registro = data_registro
        self._resolvida = bool(resolvida)
        self.data_resolucao = data_resolucao
        if not self.codigo or not self.descricao:
            raise ValueError("Código e descrição da avaria são obrigatórios.")

    @property
    def resolvida(self):
        return self._resolvida

    def resolver(self, data_resolucao):
        if self._resolvida:
            raise ValueError("Esta avaria já foi resolvida.")
        if data_resolucao < self.data_registro:
            raise ValueError("A data de resolução não pode ser anterior ao registro.")
        self._resolvida = True
        self.data_resolucao = data_resolucao

    def esta_ativa(self):
        return not self._resolvida
