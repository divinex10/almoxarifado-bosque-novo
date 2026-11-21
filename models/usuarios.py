class Usuario:
    def __init__(self, codigo, nome, contato):
        self.codigo = str(codigo).strip().lower()
        self.nome = str(nome).strip()
        self.contato = str(contato).strip()
        if not self.codigo or not self.nome or not self.contato:
            raise ValueError("Código, nome e contato são obrigatórios.")
