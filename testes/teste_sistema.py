
import unittest
from datetime import date, timedelta
import sys
import tempfile
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.equipamentos import Equipamento
from models.usuarios import Usuario
from models.emprestimos import Emprestimo
from models.reservas import Reserva
from models.avarias import Avaria

from services.repositorio_json import RepositorioJSON
from services.sistema_almoxarifado import SistemaAlmoxarifado


class TesteSistemaAlmoxarifado(unittest.TestCase):

    def setUp(self):
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        self.repositorio = RepositorioJSON(self.diretorio_temporario.name)
        self.sistema = SistemaAlmoxarifado(self.repositorio)

        # Dados básicos utilizados em vários testes
        self.equipamento = Equipamento(
            "eqp001",
            "Projetor",
            "Projetor de teste",
            "disponivel"
        )

        self.usuario = Usuario(
            "usr001",
            "Usuario Teste",
            "teste@email.com"
        )

        self.sistema.cadastrar_equipamento(self.equipamento)
        self.sistema.cadastrar_usuario(self.usuario)

    def tearDown(self):
        self.diretorio_temporario.cleanup()

    # --------------------------------------------------
    # CADASTROS
    # --------------------------------------------------

    def test_cadastrar_equipamento(self):
        equipamento = Equipamento(
            "eqp002",
            "Notebook",
            "Notebook de teste",
            "disponivel"
        )

        resultado = self.sistema.cadastrar_equipamento(equipamento)

        self.assertTrue(resultado)
        self.assertIsNotNone(
            self.sistema.buscar_equipamento("eqp002")
        )

    def test_rejeitar_equipamento_duplicado(self):
        equipamento = Equipamento(
            "eqp001",
            "Outro Projetor",
            "Duplicado",
            "disponivel"
        )

        resultado = self.sistema.cadastrar_equipamento(equipamento)

        self.assertFalse(resultado)
        self.assertEqual(len(self.sistema.equipamentos), 1)

    def test_cadastrar_usuario(self):
        usuario = Usuario(
            "usr002",
            "Outro Usuario",
            "outro@email.com"
        )

        resultado = self.sistema.cadastrar_usuario(usuario)

        self.assertTrue(resultado)
        self.assertIsNotNone(
            self.sistema.buscar_usuario("usr002")
        )

    def test_rejeitar_usuario_duplicado(self):
        usuario = Usuario(
            "usr001",
            "Usuario Duplicado",
            "duplicado@email.com"
        )

        resultado = self.sistema.cadastrar_usuario(usuario)

        self.assertFalse(resultado)
        self.assertEqual(len(self.sistema.usuarios), 1)

    def test_buscar_equipamento_inexistente(self):
        resultado = self.sistema.buscar_equipamento("INEXISTENTE")

        self.assertIsNone(resultado)

    def test_buscar_usuario_inexistente(self):
        resultado = self.sistema.buscar_usuario("INEXISTENTE")

        self.assertIsNone(resultado)

    # --------------------------------------------------
    # EMPRÉSTIMOS
    # --------------------------------------------------

    def test_cadastrar_emprestimo(self):
        emprestimo = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=5)
        )

        resultado = self.sistema.cadastrar_emprestimo(emprestimo)

        self.assertTrue(resultado)

        self.assertEqual(
            self.sistema.buscar_equipamento("eqp001").estado,
            "emprestado"
        )

        self.assertEqual(
            len(self.sistema.listar_emprestimos_ativos()),
            1
        )

    def test_rejeitar_emprestimo_equipamento_inexistente(self):
        emprestimo = Emprestimo(
            "emp001",
            "eqp999",
            "usr001",
            date.today(),
            date.today() + timedelta(days=5)
        )

        resultado = self.sistema.cadastrar_emprestimo(emprestimo)

        self.assertFalse(resultado)

    def test_rejeitar_emprestimo_usuario_inexistente(self):
        emprestimo = Emprestimo(
            "emp001",
            "eqp001",
            "usr999",
            date.today(),
            date.today() + timedelta(days=5)
        )

        resultado = self.sistema.cadastrar_emprestimo(emprestimo)

        self.assertFalse(resultado)

    def test_rejeitar_emprestimo_equipamento_emprestado(self):
        primeiro = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=5)
        )

        segundo = Emprestimo(
            "emp002",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=3)
        )

        self.sistema.cadastrar_emprestimo(primeiro)

        resultado = self.sistema.cadastrar_emprestimo(segundo)

        self.assertFalse(resultado)
        self.assertEqual(len(self.sistema.emprestimos), 1)

    def test_rejeitar_codigo_emprestimo_duplicado(self):
        primeiro = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=5)
        )

        self.sistema.cadastrar_emprestimo(primeiro)

        # Devolvendo o equipamento para permitir novo empréstimo
        self.sistema.registrar_devolucao(
            "eqp001",
            date.today()
        )

        segundo = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=3)
        )

        resultado = self.sistema.cadastrar_emprestimo(segundo)

        self.assertFalse(resultado)
        self.assertEqual(len(self.sistema.emprestimos), 1)

    def test_rejeitar_retirada_futura(self):
        emprestimo = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today() + timedelta(days=2),
            date.today() + timedelta(days=5)
        )

        resultado = self.sistema.cadastrar_emprestimo(emprestimo)

        self.assertFalse(resultado)

    def test_rejeitar_devolucao_anterior_retirada(self):
        emprestimo = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() - timedelta(days=1)
        )

        resultado = self.sistema.cadastrar_emprestimo(emprestimo)

        self.assertFalse(resultado)

    # --------------------------------------------------
    # RESERVAS
    # --------------------------------------------------

    def test_cadastrar_reserva_futura(self):
        reserva = Reserva(
            "res001",
            "eqp001",
            "usr001",
            date.today() + timedelta(days=2),
            date.today() + timedelta(days=4)
        )

        resultado = self.sistema.cadastrar_reserva(reserva)

        self.assertTrue(resultado)
        self.assertEqual(len(self.sistema.listar_reservas_ativas()), 1)

    def test_rejeitar_reserva_data_passada(self):
        reserva = Reserva(
            "res001",
            "eqp001",
            "usr001",
            date.today() - timedelta(days=1),
            date.today() + timedelta(days=2)
        )

        resultado = self.sistema.cadastrar_reserva(reserva)

        self.assertFalse(resultado)

    def test_rejeitar_reserva_data_inicio_maior(self):
        reserva = Reserva(
            "res001",
            "eqp001",
            "usr001",
            date.today() + timedelta(days=5),
            date.today() + timedelta(days=2)
        )

        resultado = self.sistema.cadastrar_reserva(reserva)

        self.assertFalse(resultado)

    def test_rejeitar_reserva_equipamento_inexistente(self):
        reserva = Reserva(
            "res001",
            "eqp999",
            "usr001",
            date.today() + timedelta(days=2),
            date.today() + timedelta(days=4)
        )

        resultado = self.sistema.cadastrar_reserva(reserva)

        self.assertFalse(resultado)

    def test_rejeitar_reserva_usuario_inexistente(self):
        reserva = Reserva(
            "res001",
            "eqp001",
            "usr999",
            date.today() + timedelta(days=2),
            date.today() + timedelta(days=4)
        )

        resultado = self.sistema.cadastrar_reserva(reserva)

        self.assertFalse(resultado)

    def test_rejeitar_reservas_conflitantes(self):
        primeira = Reserva(
            "res001",
            "eqp001",
            "usr001",
            date.today() + timedelta(days=2),
            date.today() + timedelta(days=5)
        )

        segunda = Reserva(
            "res002",
            "eqp001",
            "usr001",
            date.today() + timedelta(days=4),
            date.today() + timedelta(days=7)
        )

        self.sistema.cadastrar_reserva(primeira)

        resultado = self.sistema.cadastrar_reserva(segunda)

        self.assertFalse(resultado)
        self.assertEqual(len(self.sistema.reservas), 1)

    def test_cancelar_reserva(self):
        reserva = Reserva(
            "res001",
            "eqp001",
            "usr001",
            date.today() + timedelta(days=2),
            date.today() + timedelta(days=4)
        )

        self.sistema.cadastrar_reserva(reserva)

        resultado = self.sistema.cancelar_reserva("res001")

        self.assertTrue(resultado)
        self.assertEqual(len(self.sistema.listar_reservas_ativas()), 0)

    def test_rejeitar_cancelamento_reserva_inexistente(self):
        resultado = self.sistema.cancelar_reserva("res999")

        self.assertFalse(resultado)

    # --------------------------------------------------
    # DEVOLUÇÕES
    # --------------------------------------------------

    def test_registrar_devolucao_normal(self):
        emprestimo = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=5)
        )

        self.sistema.cadastrar_emprestimo(emprestimo)

        resultado = self.sistema.registrar_devolucao(
            "eqp001",
            date.today()
        )

        self.assertTrue(resultado)

        self.assertEqual(
            self.sistema.buscar_equipamento("eqp001").estado,
            "disponivel"
        )

        self.assertTrue(emprestimo.finalizado)
        self.assertEqual(emprestimo.data_retorno, date.today())

    def test_rejeitar_devolucao_sem_emprestimo_ativo(self):
        resultado = self.sistema.registrar_devolucao(
            "eqp001",
            date.today()
        )

        self.assertFalse(resultado)

    def test_rejeitar_devolucao_equipamento_inexistente(self):
        resultado = self.sistema.registrar_devolucao(
            "eqp999",
            date.today()
        )

        self.assertFalse(resultado)

    # --------------------------------------------------
    # AVARIAS
    # --------------------------------------------------

    def test_devolucao_com_avaria(self):
        emprestimo = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=5)
        )

        self.sistema.cadastrar_emprestimo(emprestimo)

        avaria = Avaria(
            "avr001",
            "eqp001",
            "emp001",
            "Equipamento danificado",
            date.today()
        )

        resultado = self.sistema.registrar_devolucao(
            "eqp001",
            date.today(),
            avaria
        )

        self.assertTrue(resultado)

        self.assertEqual(
            self.sistema.buscar_equipamento("eqp001").estado,
            "danificado"
        )

        self.assertEqual(len(self.sistema.listar_avarias_pendentes()), 1)

    def test_resolver_avaria(self):
        emprestimo = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=5)
        )

        self.sistema.cadastrar_emprestimo(emprestimo)

        avaria = Avaria(
            "avr001",
            "eqp001",
            "emp001",
            "Equipamento danificado",
            date.today()
        )

        self.sistema.registrar_devolucao(
            "eqp001",
            date.today(),
            avaria
        )

        resultado = self.sistema.resolver_avaria(
            "avr001",
            date.today()
        )

        self.assertTrue(resultado)

        self.assertEqual(
            self.sistema.buscar_equipamento("eqp001").estado,
            "disponivel"
        )

        self.assertEqual(len(self.sistema.listar_avarias_pendentes()), 0)

    def test_rejeitar_resolucao_avaria_inexistente(self):
        resultado = self.sistema.resolver_avaria(
            "avr999",
            date.today()
        )

        self.assertFalse(resultado)

    # --------------------------------------------------
    # CONSULTAS
    # --------------------------------------------------

    def test_listar_equipamentos(self):
        resultado = self.sistema.listar_equipamentos()

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].codigo, "eqp001")

    def test_listar_emprestimos_ativos(self):
        emprestimo = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=5)
        )

        self.sistema.cadastrar_emprestimo(emprestimo)

        resultado = self.sistema.listar_emprestimos_ativos()

        self.assertEqual(len(resultado), 1)

    def test_listar_emprestimos_atrasados(self):
        emprestimo = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today() - timedelta(days=5),
            date.today() - timedelta(days=1)
        )

        self.sistema.emprestimos.append(emprestimo)
        self.repositorio.salvar_emprestimos(self.sistema.emprestimos)

        resultado = self.sistema.listar_emprestimos_atrasados()

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].codigo, "emp001")

    # --------------------------------------------------
    # PERSISTÊNCIA
    # --------------------------------------------------

    def test_persistencia_dos_dados(self):
        equipamento = Equipamento(
            "eqp002",
            "Notebook",
            "Notebook de teste",
            "disponivel"
        )

        usuario = Usuario(
            "usr002",
            "Outro Usuario",
            "outro@email.com"
        )

        self.sistema.cadastrar_equipamento(equipamento)
        self.sistema.cadastrar_usuario(usuario)

        # Cria uma nova instância para carregar os JSON
        novo_sistema = SistemaAlmoxarifado(self.repositorio)

        self.assertIsNotNone(
            novo_sistema.buscar_equipamento("eqp002")
        )

        self.assertIsNotNone(
            novo_sistema.buscar_usuario("usr002")
        )

    
    # --------------------------------------------------
    # REGRAS DE CONFLITO ENTRE EMPRÉSTIMOS E RESERVAS
    # --------------------------------------------------

    def test_rejeitar_reserva_equipamento_danificado(self):
        emprestimo = Emprestimo(
            "emp001", "eqp001", "usr001", date.today(), date.today() + timedelta(days=5)
        )
        self.sistema.cadastrar_emprestimo(emprestimo)
        avaria = Avaria("avr001", "eqp001", "emp001", "Dano de teste", date.today())
        self.sistema.registrar_devolucao("eqp001", date.today(), avaria)

        reserva = Reserva(
            "res001",
            "eqp001",
            "usr001",
            date.today() + timedelta(days=2),
            date.today() + timedelta(days=4)
        )

        resultado = self.sistema.cadastrar_reserva(reserva)

        self.assertFalse(resultado)

    def test_rejeitar_emprestimo_com_reserva_de_outro_usuario(self):
        outro_usuario = Usuario(
            "usr002",
            "Outro Usuario",
            "outro@email.com"
        )

        self.sistema.cadastrar_usuario(outro_usuario)

        reserva = Reserva(
            "res001",
            "eqp001",
            "usr002",
            date.today(),
            date.today() + timedelta(days=5)
        )

        self.sistema.cadastrar_reserva(reserva)

        emprestimo = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=3)
        )

        resultado = self.sistema.cadastrar_emprestimo(emprestimo)

        self.assertFalse(resultado)
        self.assertEqual(len(self.sistema.emprestimos), 0)

    def test_emprestimo_atende_reserva_do_mesmo_usuario(self):
        reserva = Reserva(
            "res001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=5)
        )

        self.sistema.cadastrar_reserva(reserva)

        emprestimo = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=3)
        )

        resultado = self.sistema.cadastrar_emprestimo(emprestimo)

        self.assertTrue(resultado)
        self.assertTrue(reserva.atendida)
        self.assertEqual(len(self.sistema.listar_reservas_ativas()), 0)

    def test_rejeitar_reserva_conflitante_com_emprestimo(self):
        emprestimo = Emprestimo(
            "emp001",
            "eqp001",
            "usr001",
            date.today(),
            date.today() + timedelta(days=5)
        )

        self.sistema.cadastrar_emprestimo(emprestimo)

        reserva = Reserva(
            "res001",
            "eqp001",
            "usr001",
            date.today() + timedelta(days=2),
            date.today() + timedelta(days=4)
        )

        resultado = self.sistema.cadastrar_reserva(reserva)

        self.assertFalse(resultado)



if __name__ == "__main__":
    unittest.main(verbosity=2)
