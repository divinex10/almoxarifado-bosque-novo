from datetime import date
from services.repositorio_json import RepositorioJSON
from models.emprestimos import Emprestimo

repositorio = RepositorioJSON()
emprestimo = Emprestimo("001", "usr001", date(2026, 11, 16), date(2026, 11, 20))

dados = repositorio.emprestimo_para_dict(emprestimo)
repositorio.salvar("teste_emprestimos.json", [dados])

dados_carregados = repositorio.carregar("teste_emprestimos.json")
emprestimo_recuperado = repositorio.dict_para_emprestimo(dados_carregados[0])

print(type(emprestimo_recuperado.data_retirada))
print(type(emprestimo_recuperado.data_devolucao))
print(emprestimo_recuperado.data_retorno)
print(type(emprestimo_recuperado))
