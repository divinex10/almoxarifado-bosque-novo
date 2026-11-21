class Equipamento:
    OPCOES = ("disponivel", "emprestado", "danificado", "indisponivel")
    opcoes = list(OPCOES)

    def __init__(self, codigo, nome, descricao, estado):
        self.codigo = str(codigo).strip().lower()
        self.nome = str(nome).strip()
        self.descricao = str(descricao).strip()
        if estado not in self.OPCOES:
            raise ValueError("Estado de equipamento inválido.")
        self._estado = estado
        if not self.codigo or not self.nome or not self.descricao:
            raise ValueError("Código, nome e descrição são obrigatórios.")

    @property
    def estado(self):
        return self._estado

    def esta_disponivel(self):
        return self._estado == "disponivel"

    def marcar_como_emprestado(self):
        if self._estado != "disponivel":
            raise ValueError("Somente equipamentos disponíveis podem ser emprestados.")
        self._estado = "emprestado"

    def marcar_como_disponivel(self):
        if self._estado == "indisponivel":
            raise ValueError("Um equipamento indisponível não pode voltar a ser utilizado.")
        self._estado = "disponivel"

    def marcar_como_danificado(self):
        if self._estado != "emprestado":
            raise ValueError("Avarias devem ser registradas na devolução de um equipamento emprestado.")
        self._estado = "danificado"

    def indisponibilizar(self):
        if self._estado == "emprestado":
            raise ValueError("Finalize o empréstimo antes de indisponibilizar o equipamento.")
        if self._estado == "indisponivel":
            raise ValueError("O equipamento já está indisponível.")
        self._estado = "indisponivel"
