from services.repositorio_json import RepositorioJSON
from models.equipamentos import Equipamento

repositorio = RepositorioJSON()

projetor = Equipamento("001", "Projetor", "Projetor de alta definição", "disponivel")

dados = repositorio.equipamento_para_dict(projetor)
repositorio.salvar("teste_equipamentos.json", [dados])

dados_carregados = repositorio.carregar("teste_equipamentos.json")
equipamento_recuperado = repositorio.dict_para_equipamento(dados_carregados[0])

print(equipamento_recuperado.codigo)
print(equipamento_recuperado.nome)
print(equipamento_recuperado.descricao)
print(equipamento_recuperado.estado)

print(type(equipamento_recuperado))


