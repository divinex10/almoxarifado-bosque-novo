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

    def dict_para_equipamento(self, dicionario):
        return Equipamento(dicionario["codigo"], dicionario["nome"], dicionario["descricao"], dicionario["estado"])

    def usuario_para_dict(self, objeto):
        codigo = objeto.codigo
        nome = objeto.nome
        contato = objeto.contato

        return {
            "codigo":codigo,
            "nome": nome,
            "contato":contato
        }

    def dict_para_usuario(self, dicionario):
        return Usuario(dicionario["codigo"], dicionario["nome"], dicionario["contato"])

    def avaria_para_dict(self, objeto):
        codigo = objeto.codigo
        codigo_equipamento = objeto.codigo_equipamento
        codigo_emprestimo = objeto.codigo_emprestimo
        descricao = objeto.descricao
        data_registro = objeto.data_registro.isoformat()
        resolvida = objeto.resolvida
        data_resolucao = objeto.data_resolucao.isoformat() if objeto.data_resolucao is not None else None

        return {
            "codigo":codigo,
            "codigo_equipamento":codigo_equipamento,
            "codigo_emprestimo": codigo_emprestimo,
            "descricao":descricao,
            "data_registro":data_registro,
            "resolvida":resolvida,
            "data_resolucao":data_resolucao
        }

    def dict_para_avaria(self, dicionario):
        return Avaria(
            dicionario["codigo"],
            dicionario["codigo_equipamento"],
            dicionario["codigo_emprestimo"],
            dicionario["descricao"],
            date.fromisoformat(dicionario["data_registro"]),
            dicionario["resolvida"],
            date.fromisoformat(dicionario["data_resolucao"]) if dicionario["data_resolucao"] is not None else None
        )

    def emprestimo_para_dict(self, objeto):
        codigo_equipamento = objeto.codigo_equipamento
        codigo_usuario = objeto.codigo_usuario
        data_retirada = objeto.data_retirada.isoformat()
        data_devolucao = objeto.data_devolucao.isoformat()
        finalizado = objeto.finalizado

        if objeto.data_retorno is not None:
            data_retorno = objeto.data_retorno.isoformat()

        else:
            data_retorno = None

        return {
            "codigo_equipamento":codigo_equipamento,
            "codigo_usuario":codigo_usuario,
            "data_retirada":data_retirada,
            "data_devolucao":data_devolucao,
            "finalizado":finalizado,
            "data_retorno":data_retorno
        }

    def dict_para_emprestimo(self, dicionario):
        return Emprestimo(
            dicionario["codigo_equipamento"],
            dicionario["codigo_usuario"],
            date.fromisoformat(dicionario["data_retirada"]),
            date.fromisoformat(dicionario["data_devolucao"]),
            dicionario["finalizado"],
            date.fromisoformat(dicionario["data_retorno"]) if dicionario["data_retorno"] is not None else None
        )

    def reserva_para_dict(self, objeto):
        codigo = objeto.codigo
        codigo_equipamento = objeto.codigo_equipamento
        codigo_usuario = objeto.codigo_usuario
        data_inicio = objeto.data_inicio.isoformat()
        data_fim = objeto.data_fim.isoformat()
        cancelada = objeto.cancelada
        atendida = objeto.atendida

        return {
            "codigo":codigo,
            "codigo_equipamento":codigo_equipamento,
            "codigo_usuario":codigo_usuario,
            "data_inicio":data_inicio,
            "data_fim":data_fim,
            "cancelada":cancelada,
            "atendida":atendida
        }

    def dict_para_reserva(self, dicionario):
        return Reserva(
            dicionario["codigo"],
            dicionario["codigo_equipamento"],
            dicionario["codigo_usuario"],
            date.fromisoformat(dicionario["data_inicio"]),
            date.fromisoformat(dicionario["data_fim"]),
            dicionario["cancelada"],
            dicionario["atendida"]
        )