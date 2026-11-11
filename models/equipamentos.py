class Equipamento:
    opcoes = ["disponivel", "emprestado", "danificado"]
    def __init__(self, codigo, nome, descricao, estado):
        self.codigo = codigo
        self.nome = nome
        self.descricao = descricao
        if estado in self.opcoes:
            self._estado = estado
        else:
            raise ValueError("Tipo de estado inválido! Tente novamente")

    def alterar_estado(self, estado):
        if estado in self.opcoes: 
            self._estado = estado
        else:
            print("Erro! Não é possível alterar para esse estado.")

    def esta_disponivel(self):
        return self._estado == "disponivel"

    @property
    def estado(self):
        return self._estado