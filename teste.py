from datetime import date
from models.equipamentos import Equipamento
from models.avarias import Avaria
from models.emprestimos import Emprestimo
from models.reservas import Reserva
from models.usuarios import Usuario
from services.repositorio_json import RepositorioJSON

data_retirada = date(2026, 11, 5)
data_devolucao = date(2026, 11, 10)

emprestimo = Emprestimo(
    "projer001",
    "user001",
    data_retirada,
    data_devolucao
)

repositorio = RepositorioJSON()
projetor = Equipamento("proj123", "Projetor", "projetor preto", "disponivel")
dados = repositorio.equipamento_para_dict(projetor)
print(dados)
dados = repositorio.dict_para_equipamento(dados)
print(dados.codigo)
print(dados.nome)
print(dados.descricao)
print(dados.estado)