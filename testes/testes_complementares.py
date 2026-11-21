import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models.equipamentos import Equipamento
from models.usuarios import Usuario
from models.emprestimos import Emprestimo
from models.reservas import Reserva
from models.avarias import Avaria
from services.repositorio_json import RepositorioJSON
from services.sistema_almoxarifado import SistemaAlmoxarifado


class TestesComplementares(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = RepositorioJSON(self.temp.name)
        self.sistema = SistemaAlmoxarifado(self.repo)
        self.hoje = date.today()
        self.eqp = Equipamento('eqp001', 'Projetor', 'Projetor de teste', 'disponivel')
        self.user = Usuario('usr001', 'Usuário teste', 'teste@email.com')
        self.assertTrue(self.sistema.cadastrar_equipamento(self.eqp))
        self.assertTrue(self.sistema.cadastrar_usuario(self.user))

    def tearDown(self):
        self.temp.cleanup()

    def novo_equipamento(self, codigo='eqp002', estado='disponivel'):
        obj = Equipamento(codigo, 'Equipamento 2', 'Descrição 2', estado)
        self.assertTrue(self.sistema.cadastrar_equipamento(obj))
        return obj

    def novo_usuario(self, codigo='usr002'):
        obj = Usuario(codigo, 'Usuário 2', 'u2@email.com')
        self.assertTrue(self.sistema.cadastrar_usuario(obj))
        return obj

    def emprestimo(self, codigo='emp001', equipamento='eqp001', usuario='usr001', prazo=7):
        return Emprestimo(codigo, equipamento, usuario, self.hoje, self.hoje + timedelta(days=prazo))

    def test_emprestimo_no_limite_de_30_dias_e_aceito(self):
        self.assertTrue(self.sistema.cadastrar_emprestimo(self.emprestimo(prazo=30)))

    def test_emprestimo_com_31_dias_e_rejeitado(self):
        self.assertFalse(self.sistema.cadastrar_emprestimo(self.emprestimo(prazo=31)))

    def test_usuario_pode_ter_emprestimos_simultaneos_de_equipamentos_diferentes(self):
        self.novo_equipamento()
        self.assertTrue(self.sistema.cadastrar_emprestimo(self.emprestimo('emp001', 'eqp001')))
        outro = Emprestimo('emp002', 'eqp002', 'usr001', self.hoje, self.hoje + timedelta(days=5))
        self.assertTrue(self.sistema.cadastrar_emprestimo(outro))

    def test_usuario_com_emprestimo_atrasado_nao_pode_pegar_outro(self):
        self.novo_equipamento()
        atrasado = Emprestimo('emp001', 'eqp001', 'usr001', self.hoje - timedelta(days=10), self.hoje - timedelta(days=1))
        self.sistema.emprestimos.append(atrasado)
        self.eqp.marcar_como_emprestado()
        outro = Emprestimo('emp002', 'eqp002', 'usr001', self.hoje, self.hoje + timedelta(days=5))
        self.assertFalse(self.sistema.cadastrar_emprestimo(outro))

    def test_reserva_no_limite_de_30_dias_e_aceita(self):
        r = Reserva('res001', 'eqp001', 'usr001', self.hoje, self.hoje + timedelta(days=30))
        self.assertTrue(self.sistema.cadastrar_reserva(r))

    def test_reserva_com_31_dias_e_rejeitada(self):
        r = Reserva('res001', 'eqp001', 'usr001', self.hoje, self.hoje + timedelta(days=31))
        self.assertFalse(self.sistema.cadastrar_reserva(r))

    def test_reserva_no_mesmo_dia_de_outra_reserva_conflita(self):
        primeira = Reserva('res001', 'eqp001', 'usr001', self.hoje, self.hoje + timedelta(days=2))
        segunda = Reserva('res002', 'eqp001', 'usr001', self.hoje + timedelta(days=2), self.hoje + timedelta(days=3))
        self.assertTrue(self.sistema.cadastrar_reserva(primeira))
        self.assertFalse(self.sistema.cadastrar_reserva(segunda))

    def test_reserva_cancelada_deixa_de_bloquear_periodo(self):
        primeira = Reserva('res001', 'eqp001', 'usr001', self.hoje + timedelta(days=1), self.hoje + timedelta(days=3))
        self.assertTrue(self.sistema.cadastrar_reserva(primeira))
        self.assertTrue(self.sistema.cancelar_reserva('res001'))
        segunda = Reserva('res002', 'eqp001', 'usr001', self.hoje + timedelta(days=2), self.hoje + timedelta(days=4))
        self.assertTrue(self.sistema.cadastrar_reserva(segunda))

    def test_reserva_em_equipamento_emprestado_pode_comecar_no_dia_seguinte_ao_prazo(self):
        loan = self.emprestimo(prazo=2)
        self.assertTrue(self.sistema.cadastrar_emprestimo(loan))
        reserva = Reserva('res001', 'eqp001', 'usr001', self.hoje + timedelta(days=3), self.hoje + timedelta(days=5))
        self.assertTrue(self.sistema.cadastrar_reserva(reserva))

    def test_reserva_em_equipamento_emprestado_nao_pode_comecar_no_dia_do_prazo(self):
        loan = self.emprestimo(prazo=2)
        self.assertTrue(self.sistema.cadastrar_emprestimo(loan))
        reserva = Reserva('res001', 'eqp001', 'usr001', self.hoje + timedelta(days=2), self.hoje + timedelta(days=4))
        self.assertFalse(self.sistema.cadastrar_reserva(reserva))

    def test_equipamento_indisponivel_nao_recebe_emprestimo_ou_reserva(self):
        eq = self.novo_equipamento(estado='indisponivel')
        loan = Emprestimo('emp001', eq.codigo, 'usr001', self.hoje, self.hoje + timedelta(days=2))
        reserva = Reserva('res001', eq.codigo, 'usr001', self.hoje + timedelta(days=1), self.hoje + timedelta(days=2))
        self.assertFalse(self.sistema.cadastrar_emprestimo(loan))
        self.assertFalse(self.sistema.cadastrar_reserva(reserva))

    def test_indisponibilizar_equipamento_cancela_reservas_ativas(self):
        reserva = Reserva('res001', 'eqp001', 'usr001', self.hoje + timedelta(days=1), self.hoje + timedelta(days=2))
        self.assertTrue(self.sistema.cadastrar_reserva(reserva))
        self.assertTrue(self.sistema.indisponibilizar_equipamento('eqp001'))
        self.assertEqual(self.eqp.estado, 'indisponivel')
        self.assertTrue(reserva.cancelada)
        self.assertEqual(len(self.sistema.listar_reservas_ativas()), 0)

    def test_nao_pode_indisponibilizar_equipamento_emprestado(self):
        self.assertTrue(self.sistema.cadastrar_emprestimo(self.emprestimo()))
        self.assertFalse(self.sistema.indisponibilizar_equipamento('eqp001'))
        self.assertEqual(self.eqp.estado, 'emprestado')

    def test_nao_pode_reativar_equipamento_indisponivel(self):
        self.assertTrue(self.sistema.indisponibilizar_equipamento('eqp001'))
        with self.assertRaises(ValueError):
            self.eqp.marcar_como_disponivel()

    def test_equipamento_danificado_pode_ser_indisponibilizado(self):
        self.eqp._estado = 'danificado'
        self.assertTrue(self.sistema.indisponibilizar_equipamento('eqp001'))
        self.assertEqual(self.eqp.estado, 'indisponivel')

    def test_resolver_avaria_de_equipamento_indisponivel_nao_o_reativa(self):
        self.assertTrue(self.sistema.cadastrar_emprestimo(self.emprestimo()))
        avaria = Avaria('avr001', 'eqp001', 'emp001', 'Lente quebrada', self.hoje)
        self.assertTrue(self.sistema.registrar_devolucao('eqp001', self.hoje, avaria))
        self.assertTrue(self.sistema.indisponibilizar_equipamento('eqp001'))
        self.assertTrue(self.sistema.resolver_avaria('avr001', self.hoje + timedelta(days=1)))
        self.assertEqual(self.eqp.estado, 'indisponivel')

    def test_listagens_historicas_incluem_registros_finalizados_cancelados_e_resolvidos(self):
        self.assertTrue(self.sistema.cadastrar_emprestimo(self.emprestimo()))
        self.assertTrue(self.sistema.registrar_devolucao('eqp001', self.hoje))
        self.assertEqual(len(self.sistema.listar_emprestimos()), 1)
        self.assertEqual(len(self.sistema.listar_emprestimos_ativos()), 0)
        reserva = Reserva('res001', 'eqp001', 'usr001', self.hoje + timedelta(days=1), self.hoje + timedelta(days=2))
        self.assertTrue(self.sistema.cadastrar_reserva(reserva))
        self.assertTrue(self.sistema.cancelar_reserva('res001'))
        self.assertEqual(len(self.sistema.listar_reservas()), 1)
        self.assertEqual(len(self.sistema.listar_reservas_ativas()), 0)

    def test_codigos_sao_normalizados_para_minusculas(self):
        eq = Equipamento('EQP009', 'Maiúsculo', 'Descrição', 'disponivel')
        self.assertTrue(self.sistema.cadastrar_equipamento(eq))
        self.assertEqual(eq.codigo, 'eqp009')
        self.assertIsNotNone(self.sistema.buscar_equipamento('EQP009'))

    def test_codigo_com_prefixo_incorreto_e_rejeitado(self):
        eq = Equipamento('abc001', 'Inválido', 'Descrição', 'disponivel')
        self.assertFalse(self.sistema.cadastrar_equipamento(eq))

    def test_codigo_antigo_nao_pode_ser_reutilizado_apos_cancelamento(self):
        reserva = Reserva('res001', 'eqp001', 'usr001', self.hoje + timedelta(days=1), self.hoje + timedelta(days=2))
        self.assertTrue(self.sistema.cadastrar_reserva(reserva))
        self.assertTrue(self.sistema.cancelar_reserva('res001'))
        repetida = Reserva('res001', 'eqp001', 'usr001', self.hoje + timedelta(days=3), self.hoje + timedelta(days=4))
        self.assertFalse(self.sistema.cadastrar_reserva(repetida))

    def test_falha_de_persistencia_reverte_cadastro_em_memoria(self):
        novo = Equipamento('eqp002', 'Outro', 'Descrição', 'disponivel')
        with patch.object(self.repo, 'salvar_estado', side_effect=OSError('falha simulada')):
            self.assertFalse(self.sistema.cadastrar_equipamento(novo))
        self.assertIsNone(self.sistema.buscar_equipamento('eqp002'))


    def test_reserva_e_rejeitada_quando_emprestimo_do_equipamento_esta_atrasado(self):
        loan = Emprestimo('emp001', 'eqp001', 'usr001', self.hoje - timedelta(days=5), self.hoje - timedelta(days=1))
        self.sistema.emprestimos.append(loan)
        self.eqp.marcar_como_emprestado()
        reserva = Reserva('res001', 'eqp001', 'usr001', self.hoje + timedelta(days=1), self.hoje + timedelta(days=2))
        self.assertFalse(self.sistema.cadastrar_reserva(reserva))

    def test_resolucao_de_avaria_nao_pode_ser_anterior_ao_registro(self):
        self.assertTrue(self.sistema.cadastrar_emprestimo(self.emprestimo()))
        avaria = Avaria('avr001', 'eqp001', 'emp001', 'Defeito', self.hoje)
        self.assertTrue(self.sistema.registrar_devolucao('eqp001', self.hoje, avaria))
        self.assertFalse(self.sistema.resolver_avaria('avr001', self.hoje - timedelta(days=1)))
        self.assertTrue(avaria.esta_ativa())

    def test_devolucao_rejeita_avaria_com_codigo_invalido(self):
        self.assertTrue(self.sistema.cadastrar_emprestimo(self.emprestimo()))
        avaria = Avaria('bad001', 'eqp001', 'emp001', 'Defeito', self.hoje)
        self.assertFalse(self.sistema.registrar_devolucao('eqp001', self.hoje, avaria))
        self.assertTrue(self.emprestimo_ativo())

    def test_devolucao_rejeita_avaria_vinculada_a_outro_emprestimo(self):
        self.assertTrue(self.sistema.cadastrar_emprestimo(self.emprestimo()))
        avaria = Avaria('avr001', 'eqp001', 'emp999', 'Defeito', self.hoje)
        self.assertFalse(self.sistema.registrar_devolucao('eqp001', self.hoje, avaria))
        self.assertTrue(self.emprestimo_ativo())

    def test_devolucao_rejeita_data_de_registro_da_avaria_diferente_do_retorno(self):
        self.assertTrue(self.sistema.cadastrar_emprestimo(self.emprestimo()))
        avaria = Avaria('avr001', 'eqp001', 'emp001', 'Defeito', self.hoje - timedelta(days=1))
        self.assertFalse(self.sistema.registrar_devolucao('eqp001', self.hoje, avaria))
        self.assertTrue(self.emprestimo_ativo())

    def test_falha_ao_salvar_emprestimo_reverte_estado_do_equipamento(self):
        loan = self.emprestimo()
        with patch.object(self.repo, 'salvar_estado', side_effect=OSError('falha simulada')):
            self.assertFalse(self.sistema.cadastrar_emprestimo(loan))
        self.assertEqual(self.eqp.estado, 'disponivel')
        self.assertEqual(len(self.sistema.emprestimos), 0)

    def test_falha_ao_salvar_devolucao_com_avaria_reverte_todos_os_estados(self):
        loan = self.emprestimo()
        self.assertTrue(self.sistema.cadastrar_emprestimo(loan))
        avaria = Avaria('avr001', 'eqp001', 'emp001', 'Defeito', self.hoje)
        with patch.object(self.repo, 'salvar_estado', side_effect=OSError('falha simulada')):
            self.assertFalse(self.sistema.registrar_devolucao('eqp001', self.hoje, avaria))
        self.assertFalse(loan.finalizado)
        self.assertEqual(self.eqp.estado, 'emprestado')
        self.assertEqual(len(self.sistema.avarias), 0)

    def test_arquivo_json_corrompido_gera_erro_claro(self):
        caminho = Path(self.temp.name) / 'equipamentos.json'
        caminho.write_text('{json inválido', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'JSON inválido'):
            RepositorioJSON(self.temp.name).carregar('equipamentos.json')

    def emprestimo_ativo(self):
        return any(e.esta_ativo() for e in self.sistema.emprestimos)

    def test_arquivos_json_ausentes_sao_criados_automaticamente(self):
        with tempfile.TemporaryDirectory() as pasta:
            repo = RepositorioJSON(pasta)
            sistema = SistemaAlmoxarifado(repo)
            for nome in ('equipamentos.json', 'usuarios.json', 'emprestimos.json', 'reservas.json', 'avarias.json'):
                self.assertTrue((Path(pasta) / nome).exists(), nome)


if __name__ == '__main__':
    unittest.main()
