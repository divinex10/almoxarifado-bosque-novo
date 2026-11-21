from datetime import date, datetime
from textwrap import dedent

from models.equipamentos import Equipamento
from models.usuarios import Usuario
from models.emprestimos import Emprestimo
from models.reservas import Reserva
from models.avarias import Avaria


class OperacaoCancelada(Exception):
    """Sinaliza que o usuário decidiu interromper o preenchimento atual."""


def ler_entrada(rotulo):
    valor = input(f"{rotulo} [digite !cancelar para voltar]: ").strip()
    if valor.casefold() == "!cancelar":
        raise OperacaoCancelada
    return valor


def ler_texto(rotulo, obrigatorio=True):
    while True:
        valor = ler_entrada(rotulo)
        if valor or not obrigatorio:
            return valor
        print("Campo obrigatório. Informe um valor.")


def ler_data(rotulo, permitir_vazio=False):
    while True:
        valor = ler_entrada(rotulo)
        if permitir_vazio and not valor:
            return None
        try:
            return date.fromisoformat(valor) if "-" in valor else datetime.strptime(valor, "%d/%m/%Y").date()
        except (ValueError, TypeError):
            print("Data inválida. Use DD/MM/AAAA (ex.: 25/11/2026).")


def confirmar(rotulo):
    while True:
        resposta = ler_entrada(f"{rotulo} (s/n)").lower()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao", "não"):
            return False
        print("Responda com 's' ou 'n'.")


def pausar():
    input("\nPressione ENTER para continuar...")


def mostrar_equipamentos(sistema):
    itens = sistema.listar_equipamentos()
    print("\n=== EQUIPAMENTOS ===")
    if not itens:
        print("Nenhum equipamento cadastrado.")
    for item in itens:
        print(f"{item.codigo} | {item.nome} | {item.estado} | {item.descricao}")


def mostrar_usuarios(sistema):
    itens = sistema.listar_usuarios()
    print("\n=== USUÁRIOS ===")
    if not itens:
        print("Nenhum usuário cadastrado.")
    for item in itens:
        print(f"{item.codigo} | {item.nome} | {item.contato}")


def mostrar_emprestimos(sistema, itens, titulo):
    print(f"\n=== {titulo} ===")
    if not itens:
        print("Nenhum empréstimo encontrado.")
    for e in itens:
        situacao = "finalizado" if e.finalizado else ("atrasado" if e.esta_em_atraso() else "ativo")
        retorno = e.data_retorno.strftime("%d/%m/%Y") if e.data_retorno else "—"
        print(f"{e.codigo} | equipamento: {e.codigo_equipamento} | usuário: {e.codigo_usuario} | retirada: {e.data_retirada:%d/%m/%Y} | prazo: {e.data_devolucao:%d/%m/%Y} | retorno: {retorno} | {situacao}")


def mostrar_reservas(sistema, itens, titulo):
    print(f"\n=== {titulo} ===")
    if not itens:
        print("Nenhuma reserva encontrada.")
    for r in itens:
        situacao = "cancelada" if r.cancelada else ("atendida" if r.atendida else "ativa")
        print(f"{r.codigo} | equipamento: {r.codigo_equipamento} | usuário: {r.codigo_usuario} | {r.data_inicio:%d/%m/%Y} a {r.data_fim:%d/%m/%Y} | {situacao}")


def mostrar_avarias(sistema, itens, titulo):
    print(f"\n=== {titulo} ===")
    if not itens:
        print("Nenhuma avaria encontrada.")
    for a in itens:
        situacao = "resolvida" if a.resolvida else "pendente"
        print(f"{a.codigo} | equipamento: {a.codigo_equipamento} | empréstimo: {a.codigo_emprestimo} | registro: {a.data_registro:%d/%m/%Y} | {situacao} | {a.descricao}")


def informar_resultado(sistema, sucesso, mensagem_sucesso):
    print(mensagem_sucesso if sucesso else f"Operação não realizada: {sistema.ultimo_erro}")


def menu_cadastros(sistema):
    while True:
        try:
            print(dedent("""
    ========== CADASTROS ==========
    [1] Cadastrar equipamento
    [2] Listar equipamentos
    [3] Cadastrar usuário
    [4] Listar usuários
    [0] Voltar
    """))
            opcao = input("Escolha: ").strip()
            if opcao == "0":
                return
            elif opcao == "1":
                try:
                    codigo = ler_texto("Código (eqp + números): ").lower()
                    nome = ler_texto("Nome: ")
                    descricao = ler_texto("Descrição: ")
                    print("Estados: disponivel | emprestado | danificado | indisponivel")
                    estado = ler_texto("Estado inicial: ").lower()
                    sucesso = sistema.cadastrar_equipamento(Equipamento(codigo, nome, descricao, estado))
                    informar_resultado(sistema, sucesso, "Equipamento cadastrado.")
                except ValueError as erro:
                    print(f"Dados inválidos: {erro}")
                pausar()
            elif opcao == "2":
                mostrar_equipamentos(sistema); pausar()
            elif opcao == "3":
                try:
                    usuario = Usuario(ler_texto("Código (usr + números): ").lower(), ler_texto("Nome: "), ler_texto("Contato: "))
                    sucesso = sistema.cadastrar_usuario(usuario)
                    informar_resultado(sistema, sucesso, "Usuário cadastrado.")
                except ValueError as erro:
                    print(f"Dados inválidos: {erro}")
                pausar()
            elif opcao == "4":
                mostrar_usuarios(sistema); pausar()
            else:
                print("Opção inválida.")


        except OperacaoCancelada:
            print("Operação cancelada. Nenhuma alteração foi realizada.")
            continue

def menu_emprestimos(sistema):
    while True:
        try:
            print(dedent("""
    ========== EMPRÉSTIMOS ==========
    [1] Registrar empréstimo
    [2] Registrar devolução
    [3] Listar empréstimos ativos
    [4] Listar empréstimos atrasados
    [5] Histórico completo de empréstimos
    [0] Voltar
    """))
            opcao = input("Escolha: ").strip()
            if opcao == "0":
                return
            elif opcao == "1":
                try:
                    codigo = ler_texto("Código do empréstimo (emp + números): ").lower()
                    codigo_eqp = ler_texto("Código do equipamento: ").lower()
                    codigo_usr = ler_texto("Código do usuário: ").lower()
                    retirada = date.today()
                    print(f"Data de retirada: {retirada:%d/%m/%Y}")
                    devolucao = ler_data("Data prevista de devolução (DD/MM/AAAA): ")
                    emprestimo = Emprestimo(codigo, codigo_eqp, codigo_usr, retirada, devolucao)
                    sucesso = sistema.cadastrar_emprestimo(emprestimo)
                    informar_resultado(sistema, sucesso, "Empréstimo registrado.")
                except ValueError as erro:
                    print(f"Dados inválidos: {erro}")
                pausar()
            elif opcao == "2":
                codigo_eqp = ler_texto("Código do equipamento: ").lower()
                emprestimo = next((e for e in sistema.listar_emprestimos_ativos() if e.codigo_equipamento == codigo_eqp), None)
                if emprestimo is None:
                    print("Não há empréstimo ativo para esse equipamento.")
                else:
                    retorno = ler_data("Data real de retorno (DD/MM/AAAA): ")
                    if confirmar("O equipamento apresentou avaria na avaliação?"):
                        try:
                            avaria = Avaria(ler_texto("Código da avaria (avr + números): ").lower(), codigo_eqp,
                                            emprestimo.codigo, ler_texto("Descrição da avaria: "), retorno)
                            sucesso = sistema.registrar_devolucao(codigo_eqp, retorno, avaria)
                        except ValueError as erro:
                            print(f"Dados inválidos: {erro}"); sucesso = False
                            sistema.ultimo_erro = str(erro)
                    else:
                        sucesso = sistema.registrar_devolucao(codigo_eqp, retorno)
                    informar_resultado(sistema, sucesso, "Devolução registrada.")
                pausar()
            elif opcao == "3":
                mostrar_emprestimos(sistema, sistema.listar_emprestimos_ativos(), "EMPRÉSTIMOS ATIVOS"); pausar()
            elif opcao == "4":
                mostrar_emprestimos(sistema, sistema.listar_emprestimos_atrasados(), "EMPRÉSTIMOS ATRASADOS"); pausar()
            elif opcao == "5":
                mostrar_emprestimos(sistema, sistema.listar_emprestimos(), "HISTÓRICO COMPLETO"); pausar()
            else:
                print("Opção inválida.")


        except OperacaoCancelada:
            print("Operação cancelada. Nenhuma alteração foi realizada.")
            continue

def menu_reservas(sistema):
    while True:
        try:
            print(dedent("""
    ========== RESERVAS ==========
    [1] Registrar reserva
    [2] Listar reservas ativas
    [3] Histórico completo de reservas
    [4] Cancelar reserva
    [0] Voltar
    """))
            opcao = input("Escolha: ").strip()
            if opcao == "0":
                return
            elif opcao == "1":
                try:
                    reserva = Reserva(
                        ler_texto("Código (res + números): ").lower(),
                        ler_texto("Código do equipamento: ").lower(),
                        ler_texto("Código do usuário: ").lower(),
                        ler_data("Data inicial (DD/MM/AAAA): "),
                        ler_data("Data final (DD/MM/AAAA): "),
                    )
                    sucesso = sistema.cadastrar_reserva(reserva)
                    informar_resultado(sistema, sucesso, "Reserva registrada.")
                except ValueError as erro:
                    print(f"Dados inválidos: {erro}")
                pausar()
            elif opcao == "2":
                mostrar_reservas(sistema, sistema.listar_reservas_ativas(), "RESERVAS ATIVAS"); pausar()
            elif opcao == "3":
                mostrar_reservas(sistema, sistema.listar_reservas(), "HISTÓRICO COMPLETO"); pausar()
            elif opcao == "4":
                codigo = ler_texto("Código da reserva: ").lower()
                sucesso = sistema.cancelar_reserva(codigo)
                informar_resultado(sistema, sucesso, "Reserva cancelada.")
                pausar()
            else:
                print("Opção inválida.")


        except OperacaoCancelada:
            print("Operação cancelada. Nenhuma alteração foi realizada.")
            continue

def menu_avarias(sistema):
    while True:
        try:
            print(dedent("""
    ========== AVARIAS ==========
    [1] Listar avarias pendentes
    [2] Histórico completo de avarias
    [3] Resolver avaria
    [0] Voltar
    """))
            opcao = input("Escolha: ").strip()
            if opcao == "0":
                return
            elif opcao == "1":
                mostrar_avarias(sistema, sistema.listar_avarias_pendentes(), "AVARIAS PENDENTES"); pausar()
            elif opcao == "2":
                mostrar_avarias(sistema, sistema.listar_avarias(), "HISTÓRICO DE AVARIAS"); pausar()
            elif opcao == "3":
                codigo = ler_texto("Código da avaria: ").lower()
                data = ler_data("Data da resolução (DD/MM/AAAA): ")
                sucesso = sistema.resolver_avaria(codigo, data)
                informar_resultado(sistema, sucesso, "Avaria resolvida.")
                pausar()
            else:
                print("Opção inválida.")


        except OperacaoCancelada:
            print("Operação cancelada. Nenhuma alteração foi realizada.")
            continue

def resumo_mensal(sistema):
    hoje = date.today()
    emprestimos_mes = [e for e in sistema.listar_emprestimos() if e.data_retirada.year == hoje.year and e.data_retirada.month == hoje.month]
    devolucoes_mes = [e for e in sistema.listar_emprestimos() if e.data_retorno and e.data_retorno.year == hoje.year and e.data_retorno.month == hoje.month]
    contagem = {estado: sum(1 for eq in sistema.equipamentos if eq.estado == estado)
                for estado in ("disponivel", "emprestado", "danificado", "indisponivel")}
    print(f"\n=== RESUMO DE {hoje:%m/%Y} ===")
    print(f"Empréstimos iniciados no mês: {len(emprestimos_mes)}")
    print(f"Devoluções registradas no mês: {len(devolucoes_mes)}")
    print(f"Empréstimos ativos atualmente: {len(sistema.listar_emprestimos_ativos())}")
    print("Equipamentos por estado:")
    for estado, quantidade in contagem.items():
        print(f"  {estado}: {quantidade}")
    pausar()


def menu_principal(sistema):
    while True:
        try:
            print(dedent("""
    ====================================
           ALMOXARIFADO BOSQUE NOVO
    ====================================
    [1] Empréstimos e devoluções
    [2] Consultar equipamentos
    [3] Reservas
    [4] Cadastros
    [5] Avarias
    [6] Indisponibilizar equipamento
    [7] Resumo mensal
    [0] Sair
    """))
            opcao = input("Escolha uma opção: ").strip()
            if opcao == "0":
                print("Sistema encerrado.")
                return
            elif opcao == "1":
                menu_emprestimos(sistema)
            elif opcao == "2":
                mostrar_equipamentos(sistema); pausar()
            elif opcao == "3":
                menu_reservas(sistema)
            elif opcao == "4":
                menu_cadastros(sistema)
            elif opcao == "5":
                menu_avarias(sistema)
            elif opcao == "6":
                codigo = ler_texto("Código do equipamento: ").lower()
                equipamento = sistema.buscar_equipamento(codigo)
                if equipamento is None:
                    print("Equipamento não encontrado.")
                else:
                    print(f"{equipamento.codigo} | {equipamento.nome} | estado atual: {equipamento.estado}")
                    if confirmar("Confirma a indisponibilização permanente? As reservas ativas serão canceladas"):
                        sucesso = sistema.indisponibilizar_equipamento(codigo)
                        informar_resultado(sistema, sucesso, "Equipamento marcado como indisponível.")
                    else:
                        print("Operação cancelada.")
                pausar()
            elif opcao == "7":
                resumo_mensal(sistema)
            else:
                print("Opção inválida. Escolha uma opção exibida no menu.")
        except OperacaoCancelada:
            print("Operação cancelada. Nenhuma alteração foi realizada.")
            continue

