import json
import os
import tempfile
from datetime import date
from pathlib import Path

from models.equipamentos import Equipamento
from models.avarias import Avaria
from models.emprestimos import Emprestimo
from models.reservas import Reserva
from models.usuarios import Usuario


class RepositorioJSON:
    ARQUIVOS = {
        "equipamentos": ("equipamentos.json", "equipamento_para_dict", "dict_para_equipamento"),
        "usuarios": ("usuarios.json", "usuario_para_dict", "dict_para_usuario"),
        "emprestimos": ("emprestimos.json", "emprestimo_para_dict", "dict_para_emprestimo"),
        "reservas": ("reservas.json", "reserva_para_dict", "dict_para_reserva"),
        "avarias": ("avarias.json", "avaria_para_dict", "dict_para_avaria"),
    }

    def __init__(self, pasta_dados="dados"):
        self.pasta_dados = Path(pasta_dados)

    def _obter_caminho(self, nome_arquivo):
        return self.pasta_dados / nome_arquivo

    def carregar(self, nome_arquivo):
        caminho = self._obter_caminho(nome_arquivo)
        self.pasta_dados.mkdir(parents=True, exist_ok=True)
        if not caminho.exists():
            self.salvar(nome_arquivo, [])
            return []
        try:
            with caminho.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except json.JSONDecodeError as erro:
            raise ValueError(f"O arquivo {nome_arquivo} contém JSON inválido.") from erro
        if not isinstance(dados, list):
            raise ValueError(f"O conteúdo de {nome_arquivo} deve ser uma lista JSON.")
        return dados

    def salvar(self, nome_arquivo, dados):
        self.salvar_varios({nome_arquivo: dados})

    def salvar_varios(self, dados_por_arquivo):
        """Grava um conjunto de arquivos. Se a gravação falhar, tenta restaurar os originais."""
        self.pasta_dados.mkdir(parents=True, exist_ok=True)
        temporarios = {}
        originais = {}
        substituidos = []
        try:
            for nome_arquivo, dados in dados_por_arquivo.items():
                destino = self._obter_caminho(nome_arquivo)
                originais[destino] = destino.read_bytes() if destino.exists() else None
                fd, temporario = tempfile.mkstemp(prefix=f".{destino.name}.", suffix=".tmp", dir=self.pasta_dados)
                temporarios[destino] = temporario
                with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
                    json.dump(dados, arquivo, ensure_ascii=False, indent=4)
                    arquivo.flush()
                    os.fsync(arquivo.fileno())
            for destino, temporario in temporarios.items():
                os.replace(temporario, destino)
                substituidos.append(destino)
        except Exception:
            for destino in reversed(substituidos):
                conteudo = originais[destino]
                if conteudo is None:
                    destino.unlink(missing_ok=True)
                else:
                    destino.write_bytes(conteudo)
            raise
        finally:
            for temporario in temporarios.values():
                if os.path.exists(temporario):
                    os.unlink(temporario)

    def equipamento_para_dict(self, obj):
        return {"codigo": obj.codigo, "nome": obj.nome, "descricao": obj.descricao, "estado": obj.estado}

    def dict_para_equipamento(self, d):
        return Equipamento(d["codigo"], d["nome"], d["descricao"], d["estado"])

    def usuario_para_dict(self, obj):
        return {"codigo": obj.codigo, "nome": obj.nome, "contato": obj.contato}

    def dict_para_usuario(self, d):
        return Usuario(d["codigo"], d["nome"], d["contato"])

    def emprestimo_para_dict(self, obj):
        return {
            "codigo": obj.codigo,
            "codigo_equipamento": obj.codigo_equipamento,
            "codigo_usuario": obj.codigo_usuario,
            "data_retirada": obj.data_retirada.isoformat(),
            "data_devolucao": obj.data_devolucao.isoformat(),
            "finalizado": obj.finalizado,
            "data_retorno": obj.data_retorno.isoformat() if obj.data_retorno else None,
        }

    def dict_para_emprestimo(self, d):
        return Emprestimo(
            d["codigo"], d["codigo_equipamento"], d["codigo_usuario"],
            date.fromisoformat(d["data_retirada"]), date.fromisoformat(d["data_devolucao"]),
            d.get("finalizado", False),
            date.fromisoformat(d["data_retorno"]) if d.get("data_retorno") else None,
        )

    def reserva_para_dict(self, obj):
        return {
            "codigo": obj.codigo,
            "codigo_equipamento": obj.codigo_equipamento,
            "codigo_usuario": obj.codigo_usuario,
            "data_inicio": obj.data_inicio.isoformat(),
            "data_fim": obj.data_fim.isoformat(),
            "cancelada": obj.cancelada,
            "atendida": obj.atendida,
        }

    def dict_para_reserva(self, d):
        return Reserva(
            d["codigo"], d["codigo_equipamento"], d["codigo_usuario"],
            date.fromisoformat(d["data_inicio"]), date.fromisoformat(d["data_fim"]),
            d.get("cancelada", False), d.get("atendida", False),
        )

    def avaria_para_dict(self, obj):
        return {
            "codigo": obj.codigo,
            "codigo_equipamento": obj.codigo_equipamento,
            "codigo_emprestimo": obj.codigo_emprestimo,
            "descricao": obj.descricao,
            "data_registro": obj.data_registro.isoformat(),
            "resolvida": obj.resolvida,
            "data_resolucao": obj.data_resolucao.isoformat() if obj.data_resolucao else None,
        }

    def dict_para_avaria(self, d):
        return Avaria(
            d["codigo"], d["codigo_equipamento"], d["codigo_emprestimo"], d["descricao"],
            date.fromisoformat(d["data_registro"]), d.get("resolvida", False),
            date.fromisoformat(d["data_resolucao"]) if d.get("data_resolucao") else None,
        )

    def _carregar_lista(self, chave):
        arquivo, _, conversor = self.ARQUIVOS[chave]
        return [getattr(self, conversor)(item) for item in self.carregar(arquivo)]

    def carregar_equipamentos(self): return self._carregar_lista("equipamentos")
    def carregar_usuarios(self): return self._carregar_lista("usuarios")
    def carregar_emprestimos(self): return self._carregar_lista("emprestimos")
    def carregar_reservas(self): return self._carregar_lista("reservas")
    def carregar_avarias(self): return self._carregar_lista("avarias")

    def _salvar_lista(self, chave, objetos):
        arquivo, conversor, _ = self.ARQUIVOS[chave]
        self.salvar(arquivo, [getattr(self, conversor)(obj) for obj in objetos])

    def salvar_equipamentos(self, objetos): self._salvar_lista("equipamentos", objetos)
    def salvar_usuarios(self, objetos): self._salvar_lista("usuarios", objetos)
    def salvar_emprestimos(self, objetos): self._salvar_lista("emprestimos", objetos)
    def salvar_reservas(self, objetos): self._salvar_lista("reservas", objetos)
    def salvar_avarias(self, objetos): self._salvar_lista("avarias", objetos)

    def salvar_estado(self, sistema, chaves):
        dados = {}
        for chave in chaves:
            arquivo, conversor, _ = self.ARQUIVOS[chave]
            dados[arquivo] = [getattr(self, conversor)(obj) for obj in getattr(sistema, chave)]
        self.salvar_varios(dados)
