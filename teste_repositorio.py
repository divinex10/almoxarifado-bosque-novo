
from datetime import date

from services.repositorio_json import RepositorioJSON
from models.equipamentos import Equipamento
from models.usuarios import Usuario
from models.emprestimos import Emprestimo
from models.reservas import Reserva
from models.avarias import Avaria


# 1. Criar o repositório de teste
repositorio = RepositorioJSON(pasta_dados="dados_teste")


# 2. Criar objetos de cada classe
equipamento = Equipamento(
    "001", "Projetor", "Projetor de alta definição", "disponivel"
)

usuario = Usuario(
    "usr001", "João Silva", "61999999999"
)

emprestimo = Emprestimo(
    "001", "usr001",
    date(2026, 11, 16),
    date(2026, 11, 20)
)

reserva = Reserva(
    "res001", "001", "usr001",
    date(2026, 11, 22),
    date(2026, 11, 25)
)

avaria = Avaria(
    "ava001", "001", "emp001",
    "Lente danificada",
    date(2026, 11, 20)
)


# 3. Salvar os objetos nos arquivos JSON
repositorio.salvar_equipamentos([equipamento])
repositorio.salvar_usuarios([usuario])
repositorio.salvar_emprestimos([emprestimo])
repositorio.salvar_reservas([reserva])
repositorio.salvar_avarias([avaria])


# 4. Carregar os dados dos arquivos JSON
equipamentos_carregados = repositorio.carregar_equipamentos()
usuarios_carregados = repositorio.carregar_usuarios()
emprestimos_carregados = repositorio.carregar_emprestimos()
reservas_carregadas = repositorio.carregar_reservas()
avarias_carregadas = repositorio.carregar_avarias()


# 5. Verificar se os objetos foram reconstruídos corretamente
assert isinstance(equipamentos_carregados[0], Equipamento)
assert isinstance(usuarios_carregados[0], Usuario)
assert isinstance(emprestimos_carregados[0], Emprestimo)
assert isinstance(reservas_carregadas[0], Reserva)
assert isinstance(avarias_carregadas[0], Avaria)

# Verificar se as datas foram recuperadas como objetos date
assert isinstance(emprestimos_carregados[0].data_retirada, date)
assert isinstance(reservas_carregadas[0].data_inicio, date)
assert isinstance(avarias_carregadas[0].data_registro, date)


print("Todos os testes passaram!")
print("Os objetos foram salvos e recuperados corretamente.")
