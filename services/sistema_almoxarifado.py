import copy
import re
from datetime import date, timedelta


class SistemaAlmoxarifado:
    PREFIXOS = {
        "equipamento": "eqp",
        "usuario": "usr",
        "emprestimo": "emp",
        "avaria": "avr",
        "reserva": "res",
    }

    def __init__(self, repositorio):
        self.repositorio = repositorio
        self.equipamentos = repositorio.carregar_equipamentos()
        self.usuarios = repositorio.carregar_usuarios()
        self.emprestimos = repositorio.carregar_emprestimos()
        self.reservas = repositorio.carregar_reservas()
        self.avarias = repositorio.carregar_avarias()
        self.ultimo_erro = ""

    def _falhar(self, mensagem):
        self.ultimo_erro = mensagem
        return False

    def _codigo_valido(self, codigo, tipo):
        prefixo = self.PREFIXOS[tipo]
        return bool(re.fullmatch(rf"{prefixo}\d+", str(codigo).strip().lower()))

    def _normalizar_codigo(self, codigo):
        return str(codigo).strip().lower()

    def _codigo_duplicado(self, lista, codigo):
        codigo = self._normalizar_codigo(codigo)
        return any(obj.codigo == codigo for obj in lista)

    def _transacao(self, chaves, operacao):
        listas_originais = {chave: getattr(self, chave) for chave in chaves}
        itens_originais = {chave: list(getattr(self, chave)) for chave in chaves}
        estados_originais = {}
        for itens in itens_originais.values():
            for item in itens:
                estados_originais[id(item)] = (item, copy.deepcopy(item.__dict__))
        try:
            operacao()
            self.repositorio.salvar_estado(self, chaves)
            self.ultimo_erro = ""
            return True
        except Exception as erro:
            for item, estado in estados_originais.values():
                item.__dict__.clear()
                item.__dict__.update(estado)
            for chave in chaves:
                lista_original = listas_originais[chave]
                lista_original[:] = itens_originais[chave]
                setattr(self, chave, lista_original)
            return self._falhar(f"Não foi possível salvar a operação. Nenhuma alteração foi mantida. Detalhe: {erro}")

    # CONSULTAS
    def listar_equipamentos(self): return list(self.equipamentos)
    def listar_usuarios(self): return list(self.usuarios)
    def listar_emprestimos(self): return list(self.emprestimos)
    def listar_emprestimos_ativos(self): return [e for e in self.emprestimos if e.esta_ativo()]
    def listar_emprestimos_atrasados(self): return [e for e in self.emprestimos if e.esta_em_atraso()]
    def listar_reservas(self): return list(self.reservas)
    def listar_reservas_ativas(self): return [r for r in self.reservas if r.esta_ativa()]
    def listar_avarias(self): return list(self.avarias)
    def listar_avarias_pendentes(self): return [a for a in self.avarias if a.esta_ativa()]

    def buscar_equipamento(self, codigo):
        codigo = self._normalizar_codigo(codigo)
        return next((e for e in self.equipamentos if e.codigo == codigo), None)

    def buscar_usuario(self, codigo):
        codigo = self._normalizar_codigo(codigo)
        return next((u for u in self.usuarios if u.codigo == codigo), None)

    # CADASTROS
    def cadastrar_equipamento(self, equipamento):
        if not self._codigo_valido(equipamento.codigo, "equipamento"):
            return self._falhar("O código do equipamento deve começar com 'eqp' seguido de um ou mais números.")
        if not equipamento.nome.strip() or not equipamento.descricao.strip():
            return self._falhar("Nome e descrição do equipamento são obrigatórios.")
        if self._codigo_duplicado(self.equipamentos, equipamento.codigo):
            return self._falhar("Já existe um equipamento com esse código. Códigos antigos não podem ser reutilizados.")
        return self._transacao(["equipamentos"], lambda: self.equipamentos.append(equipamento))

    def cadastrar_usuario(self, usuario):
        if not self._codigo_valido(usuario.codigo, "usuario"):
            return self._falhar("O código do usuário deve começar com 'usr' seguido de um ou mais números.")
        if not usuario.nome.strip() or not usuario.contato.strip():
            return self._falhar("Nome e contato do usuário são obrigatórios.")
        if self._codigo_duplicado(self.usuarios, usuario.codigo):
            return self._falhar("Já existe um usuário com esse código. Códigos antigos não podem ser reutilizados.")
        return self._transacao(["usuarios"], lambda: self.usuarios.append(usuario))

    # EMPRÉSTIMOS
    def cadastrar_emprestimo(self, emprestimo):
        emprestimo.codigo = self._normalizar_codigo(emprestimo.codigo)
        emprestimo.codigo_equipamento = self._normalizar_codigo(emprestimo.codigo_equipamento)
        emprestimo.codigo_usuario = self._normalizar_codigo(emprestimo.codigo_usuario)
        if not self._codigo_valido(emprestimo.codigo, "emprestimo"):
            return self._falhar("O código do empréstimo deve começar com 'emp' seguido de um ou mais números.")
        if self._codigo_duplicado(self.emprestimos, emprestimo.codigo):
            return self._falhar("Já existe um empréstimo com esse código. Códigos não podem ser reutilizados.")
        equipamento = self.buscar_equipamento(emprestimo.codigo_equipamento)
        usuario = self.buscar_usuario(emprestimo.codigo_usuario)
        if equipamento is None:
            return self._falhar("Equipamento não encontrado.")
        if usuario is None:
            return self._falhar("Usuário não encontrado.")
        if equipamento.estado != "disponivel":
            return self._falhar(f"O equipamento não pode ser emprestado: estado atual '{equipamento.estado}'.")
        if emprestimo.data_retirada != date.today():
            return self._falhar("A data de retirada deve ser hoje.")
        if emprestimo.data_devolucao < emprestimo.data_retirada:
            return self._falhar("A data prevista de devolução não pode ser anterior à retirada.")
        if (emprestimo.data_devolucao - emprestimo.data_retirada).days > 30:
            return self._falhar("O prazo máximo de um empréstimo é de 30 dias.")
        if any(e.codigo_usuario == usuario.codigo and e.esta_em_atraso() for e in self.emprestimos):
            return self._falhar("O usuário possui empréstimo atrasado e não pode retirar outro equipamento.")
        reserva_a_atender = None
        for reserva in self.reservas:
            if reserva.codigo_equipamento != equipamento.codigo or not reserva.esta_ativa():
                continue
            conflito = emprestimo.data_retirada <= reserva.data_fim and reserva.data_inicio <= emprestimo.data_devolucao
            if not conflito:
                continue
            if (reserva.codigo_usuario == usuario.codigo
                    and reserva.data_inicio == emprestimo.data_retirada
                    and reserva.data_fim >= emprestimo.data_devolucao
                    and reserva_a_atender is None):
                reserva_a_atender = reserva
            else:
                return self._falhar(f"O período do empréstimo conflita com a reserva {reserva.codigo}.")

        chaves = ["emprestimos", "equipamentos"]
        if reserva_a_atender:
            chaves.append("reservas")

        def operacao():
            self.emprestimos.append(emprestimo)
            equipamento.marcar_como_emprestado()
            if reserva_a_atender:
                reserva_a_atender.marcar_como_atendida()
        return self._transacao(chaves, operacao)

    # RESERVAS
    def cadastrar_reserva(self, reserva):
        reserva.codigo = self._normalizar_codigo(reserva.codigo)
        reserva.codigo_equipamento = self._normalizar_codigo(reserva.codigo_equipamento)
        reserva.codigo_usuario = self._normalizar_codigo(reserva.codigo_usuario)
        if not self._codigo_valido(reserva.codigo, "reserva"):
            return self._falhar("O código da reserva deve começar com 'res' seguido de um ou mais números.")
        if self._codigo_duplicado(self.reservas, reserva.codigo):
            return self._falhar("Já existe uma reserva com esse código. Códigos não podem ser reutilizados.")
        equipamento = self.buscar_equipamento(reserva.codigo_equipamento)
        usuario = self.buscar_usuario(reserva.codigo_usuario)
        if equipamento is None:
            return self._falhar("Equipamento não encontrado.")
        if usuario is None:
            return self._falhar("Usuário não encontrado.")
        if equipamento.estado in ("danificado", "indisponivel"):
            return self._falhar(f"Equipamentos no estado '{equipamento.estado}' não podem receber reservas.")
        if reserva.data_inicio < date.today():
            return self._falhar("A data de início da reserva não pode estar no passado.")
        if reserva.data_inicio > reserva.data_fim:
            return self._falhar("A data inicial não pode ser posterior à data final.")
        if (reserva.data_fim - reserva.data_inicio).days > 30:
            return self._falhar("O prazo máximo de uma reserva é de 30 dias.")
        for existente in self.reservas:
            if existente.codigo_equipamento == equipamento.codigo and existente.esta_ativa():
                if reserva.data_inicio <= existente.data_fim and reserva.data_fim >= existente.data_inicio:
                    return self._falhar(f"O período conflita com a reserva ativa {existente.codigo}.")
        emprestimo_ativo = next((e for e in self.emprestimos if e.codigo_equipamento == equipamento.codigo and e.esta_ativo()), None)
        if emprestimo_ativo:
            if emprestimo_ativo.esta_em_atraso():
                return self._falhar("Não é possível reservar enquanto o empréstimo atual estiver atrasado.")
            if reserva.data_inicio <= emprestimo_ativo.data_devolucao:
                return self._falhar("A reserva deve começar somente no dia seguinte à devolução prevista do empréstimo atual.")
        return self._transacao(["reservas"], lambda: self.reservas.append(reserva))

    def cancelar_reserva(self, codigo):
        codigo = self._normalizar_codigo(codigo)
        reserva = next((r for r in self.reservas if r.codigo == codigo and r.esta_ativa()), None)
        if reserva is None:
            return self._falhar("Reserva ativa não encontrada.")
        return self._transacao(["reservas"], reserva.cancelar)

    # DEVOLUÇÃO E AVARIAS
    def registrar_devolucao(self, codigo_equipamento, data_retorno, avaria=None):
        equipamento = self.buscar_equipamento(codigo_equipamento)
        if equipamento is None:
            return self._falhar("Equipamento não encontrado.")
        emprestimo = next((e for e in self.emprestimos if e.codigo_equipamento == equipamento.codigo and e.esta_ativo()), None)
        if emprestimo is None:
            return self._falhar("Não existe empréstimo ativo para esse equipamento.")
        if data_retorno < emprestimo.data_retirada:
            return self._falhar("A data de retorno não pode ser anterior à retirada.")
        chaves = ["emprestimos", "equipamentos"]
        if avaria is not None:
            avaria.codigo = self._normalizar_codigo(avaria.codigo)
            avaria.codigo_equipamento = self._normalizar_codigo(avaria.codigo_equipamento)
            avaria.codigo_emprestimo = self._normalizar_codigo(avaria.codigo_emprestimo)
            if not self._codigo_valido(avaria.codigo, "avaria"):
                return self._falhar("O código da avaria deve começar com 'avr' seguido de um ou mais números.")
            if self._codigo_duplicado(self.avarias, avaria.codigo):
                return self._falhar("Já existe uma avaria com esse código. Códigos não podem ser reutilizados.")
            if avaria.codigo_equipamento != equipamento.codigo or avaria.codigo_emprestimo != emprestimo.codigo:
                return self._falhar("A avaria deve referenciar o equipamento e o empréstimo que estão sendo devolvidos.")
            if avaria.data_registro != data_retorno:
                return self._falhar("A data de registro da avaria deve corresponder à data da devolução.")
            if any(a.codigo_equipamento == equipamento.codigo and a.esta_ativa() for a in self.avarias):
                return self._falhar("O equipamento já possui uma avaria pendente.")
            chaves.append("avarias")

        def operacao():
            emprestimo.finalizar(data_retorno)
            if avaria is None:
                equipamento.marcar_como_disponivel()
            else:
                equipamento.marcar_como_danificado()
                self.avarias.append(avaria)
        return self._transacao(chaves, operacao)

    def resolver_avaria(self, codigo, data):
        codigo = self._normalizar_codigo(codigo)
        avaria = next((a for a in self.avarias if a.codigo == codigo and a.esta_ativa()), None)
        if avaria is None:
            return self._falhar("Avaria pendente não encontrada.")
        equipamento = self.buscar_equipamento(avaria.codigo_equipamento)
        if equipamento is None:
            return self._falhar("O equipamento vinculado à avaria não foi encontrado.")
        if data < avaria.data_registro:
            return self._falhar("A data de resolução não pode ser anterior ao registro da avaria.")
        if equipamento.estado not in ("danificado", "indisponivel"):
            return self._falhar("O estado atual do equipamento não é compatível com essa avaria pendente.")

        def operacao():
            avaria.resolver(data)
            if equipamento.estado == "danificado":
                equipamento.marcar_como_disponivel()
            # Se foi baixado como indisponível, permanece indisponível.
        return self._transacao(["avarias", "equipamentos"], operacao)

    def indisponibilizar_equipamento(self, codigo):
        equipamento = self.buscar_equipamento(codigo)
        if equipamento is None:
            return self._falhar("Equipamento não encontrado.")
        if equipamento.estado == "emprestado":
            return self._falhar("Finalize o empréstimo antes de indisponibilizar o equipamento.")
        if equipamento.estado == "indisponivel":
            return self._falhar("O equipamento já está indisponível.")
        reservas_afetadas = [r for r in self.reservas if r.codigo_equipamento == equipamento.codigo and r.esta_ativa()]
        chaves = ["equipamentos"] + (["reservas"] if reservas_afetadas else [])

        def operacao():
            equipamento.indisponibilizar()
            for reserva in reservas_afetadas:
                reserva.cancelar()
        return self._transacao(chaves, operacao)
