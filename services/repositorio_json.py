import json
import os
from datetime import date
from models.equipamentos import Equipamento
from models.avarias import Avaria
from models.emprestimos import Emprestimo
from models.reservas import Reserva
from models.usuarios import Usuario


class RepositorioJSON:
    def __init__(self, pasta_dados = "dados"):
        self.pasta_dados = pasta_dados

    def _obter_caminho(self, nome_arquivo):
        return os.path.join(self.pasta_dados, nome_arquivo)

    def carregar(self, nome_arquivo):
        caminho = self._obter_caminho(nome_arquivo)

        os.makedirs(self.pasta_dados, exist_ok=True)

        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as arquivo:
                    dados = json.load(arquivo)
                return dados
            except json.JSONDecodeError as erro:
                raise ValueError(f"Arquivo JSON inválido: {nome_arquivo}") from erro
        else:
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump([], arquivo, ensure_ascii=False, indent=4)

            return []

    def salvar(self, nome_arquivo, dados):
        caminho = self._obter_caminho(nome_arquivo)
        os.makedirs(self.pasta_dados, exist_ok=True)

        with open(caminho, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)

    def equipamento_para_dict(self, objeto):
        codigo = objeto.codigo
        nome = objeto.nome
        descricao = objeto.descricao
        estado = objeto.estado

        return {
            "codigo":codigo,
            "nome": nome,
            "descricao":descricao,
            "estado":estado
        }

