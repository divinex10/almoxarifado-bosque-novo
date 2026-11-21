import contextlib
import io
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parent.parent))

from menus.menu_principal import (
    OperacaoCancelada,
    confirmar,
    ler_data,
    ler_texto,
    menu_avarias,
    menu_cadastros,
    menu_emprestimos,
    menu_principal,
    menu_reservas,
)
from models.equipamentos import Equipamento
from models.usuarios import Usuario
from models.emprestimos import Emprestimo
from models.avarias import Avaria
from services.repositorio_json import RepositorioJSON
from services.sistema_almoxarifado import SistemaAlmoxarifado


class TestesCancelamentoMenus(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.sistema = SistemaAlmoxarifado(RepositorioJSON(self.temp.name))
        self.eqp = Equipamento("eqp001", "Projetor", "Projetor de teste", "disponivel")
        self.usr = Usuario("usr001", "Usuário teste", "teste@email.com")
        self.assertTrue(self.sistema.cadastrar_equipamento(self.eqp))
        self.assertTrue(self.sistema.cadastrar_usuario(self.usr))

    def tearDown(self):
        self.temp.cleanup()

    def executar_menu(self, funcao, entradas):
        saida = io.StringIO()
        with patch("builtins.input", side_effect=entradas), contextlib.redirect_stdout(saida):
            funcao(self.sistema)
        return saida.getvalue()

    def test_entrada_de_texto_reconhece_comando_cancelar(self):
        with patch("builtins.input", return_value="!cancelar"):
            with self.assertRaises(OperacaoCancelada):
                ler_texto("Nome: ")

    def test_entrada_de_data_reconhece_comando_cancelar(self):
        with patch("builtins.input", return_value="!cancelar"):
            with self.assertRaises(OperacaoCancelada):
                ler_data("Data: ")

    def test_confirmacao_reconhece_comando_cancelar(self):
        with patch("builtins.input", return_value="!cancelar"):
            with self.assertRaises(OperacaoCancelada):
                confirmar("Confirmar ação?")

    def test_cancelar_cadastro_de_usuario_nao_salva_dados_parciais(self):
        saida = self.executar_menu(menu_cadastros, ["3", "usr002", "!cancelar", "0"])
        self.assertIsNone(self.sistema.buscar_usuario("usr002"))
        self.assertIn("Operação cancelada", saida)

    def test_cancelar_cadastro_de_emprestimo_nao_altera_equipamento(self):
        saida = self.executar_menu(menu_emprestimos, ["1", "emp001", "eqp001", "usr001", "!cancelar", "0"])
        self.assertEqual(self.sistema.listar_emprestimos(), [])
        self.assertEqual(self.eqp.estado, "disponivel")
        self.assertIn("Operação cancelada", saida)

    def test_cancelar_cadastro_de_reserva_nao_salva_dados_parciais(self):
        saida = self.executar_menu(menu_reservas, ["1", "res001", "eqp001", "usr001", "!cancelar", "0"])
        self.assertEqual(self.sistema.listar_reservas(), [])
        self.assertIn("Operação cancelada", saida)

    def test_cancelar_devolucao_mantem_emprestimo_ativo(self):
        emprestimo = Emprestimo("emp001", "eqp001", "usr001", date.today(), date.today() + timedelta(days=5))
        self.assertTrue(self.sistema.cadastrar_emprestimo(emprestimo))
        saida = self.executar_menu(menu_emprestimos, ["2", "eqp001", "!cancelar", "0"])
        self.assertEqual(len(self.sistema.listar_emprestimos_ativos()), 1)
        self.assertEqual(self.eqp.estado, "emprestado")
        self.assertIn("Operação cancelada", saida)

    def test_cancelar_resolucao_de_avaria_mantem_avaria_pendente(self):
        emprestimo = Emprestimo("emp001", "eqp001", "usr001", date.today(), date.today() + timedelta(days=5))
        self.assertTrue(self.sistema.cadastrar_emprestimo(emprestimo))
        avaria = Avaria("avr001", "eqp001", "emp001", "Defeito", date.today())
        self.assertTrue(self.sistema.registrar_devolucao("eqp001", date.today(), avaria))
        saida = self.executar_menu(menu_avarias, ["3", "avr001", "!cancelar", "0"])
        self.assertTrue(self.sistema.listar_avarias_pendentes()[0].esta_ativa())
        self.assertEqual(self.eqp.estado, "danificado")
        self.assertIn("Operação cancelada", saida)

    def test_cancelar_indisponibilizacao_nao_altera_equipamento(self):
        saida = self.executar_menu(menu_principal, ["6", "eqp001", "!cancelar", "0"])
        self.assertEqual(self.eqp.estado, "disponivel")
        self.assertIn("Operação cancelada", saida)


if __name__ == "__main__":
    unittest.main()
