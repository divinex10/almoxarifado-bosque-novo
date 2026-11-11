from models.equipamentos import Equipamento

projetor = Equipamento("projer001", "Projetor", "Projetor de marca tal", "disponive")
microfone = Equipamento("mic001", "Microfone Wireless", "Microfone de marca tal", "disponivel")

print(projetor.codigo, projetor.nome, projetor.descricao, projetor.estado)
projetor.alterar_estado("emprestado")
print(projetor.esta_disponivel())
print(microfone.esta_disponivel())