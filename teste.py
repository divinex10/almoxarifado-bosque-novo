from datetime import date
from models.emprestimos import Emprestimo

data_retirada = date(2026, 11, 5)
data_devolucao = date(2026, 11, 10)

emprestimo = Emprestimo(
    "projer001",
    "user001",
    data_retirada,
    data_devolucao
)

print(emprestimo.esta_em_atraso())