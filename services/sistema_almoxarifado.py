from datetime import date 

class SistemaAlmoxarifado:
    def __init__(self, repositorio):
        self.repositorio = repositorio
        self.equipamentos = self.repositorio.carregar_equipamentos()
        self.usuarios = self.repositorio.carregar_usuarios()
        self.emprestimos = self.repositorio.carregar_emprestimos()
        self.reservas = self.repositorio.carregar_reservas()
        self.avarias = self.repositorio.carregar_avarias()

    def cadastrar_equipamento(self, equipamento):
        for objeto in self.equipamentos:
            if objeto.codigo == equipamento.codigo:
                return False

        else:
            self.equipamentos.append(equipamento)
            self.repositorio.salvar_equipamentos(self.equipamentos)
            return True

    def cadastrar_usuario(self, usuario):
        for objeto in self.usuarios:
            if objeto.codigo == usuario.codigo:
                return False

        else:
            self.usuarios.append(usuario)
            self.repositorio.salvar_usuarios(self.usuarios)
            return True

    def buscar_equipamento(self, codigo):
        for equipamento in self.equipamentos:
            if equipamento.codigo == codigo:
                return equipamento
        return None

    def buscar_usuario(self, codigo):
        for usuario in self.usuarios:
            if usuario.codigo == codigo:
                return usuario
        return None

    def cadastrar_emprestimo(self, emprestimo):
        equipamento = self.buscar_equipamento(emprestimo.codigo_equipamento)
        usuario = self.buscar_usuario(emprestimo.codigo_usuario)

        if equipamento is None or usuario is None:
            return False

        if not equipamento.esta_disponivel():
            return False

        if emprestimo.data_retirada != date.today() or emprestimo.data_retirada > emprestimo.data_devolucao:
            return False

        for objeto in self.emprestimos:
            if objeto.codigo == emprestimo.codigo:
                return False

        for reserva in self.reservas:
            if reserva.codigo_equipamento == emprestimo.codigo_equipamento and reserva.esta_ativa() and emprestimo.data_retirada <= reserva.data_fim and reserva.data_inicio <= emprestimo.data_devolucao:
                return False
            

        self.emprestimos.append(emprestimo)
        equipamento.alterar_estado("emprestado")

        self.repositorio.salvar_emprestimos(self.emprestimos)
        self.repositorio.salvar_equipamentos(self.equipamentos)

        return True

    def registrar_devolucao(self, codigo_equipamento, data_retorno, avaria = None):
        equipamento = self.buscar_equipamento(codigo_equipamento)

        if equipamento is None:
            return False

        for emprestimo in self.emprestimos:
            if emprestimo.codigo_equipamento == codigo_equipamento and not emprestimo.finalizado :
                emprestimo.finalizar(data_retorno)

                if avaria is not None:
                    self.avarias.append(avaria)
                    equipamento.alterar_estado("danificado")
                    self.repositorio.salvar_avarias(self.avarias)
                else:
                    equipamento.alterar_estado("disponivel")

                self.repositorio.salvar_emprestimos(self.emprestimos)
                self.repositorio.salvar_equipamentos(self.equipamentos)

                return True

        return False

    def cadastrar_reserva(self, reserva):
        equipamento = self.buscar_equipamento(reserva.codigo_equipamento)
        usuario = self.buscar_usuario(reserva.codigo_usuario)

        if reserva.data_inicio > reserva.data_fim and reserva.data_inicio < date.today():
             return False

        if equipamento is None or usuario is None:
            return False

        for objeto in self.reservas:
            if objeto.codigo == reserva.codigo:
                return False     

            if objeto.codigo_equipamento == reserva.codigo_equipamento and objeto.esta_ativa():
                if reserva.data_inicio <= objeto.data_fim and reserva.data_fim >= objeto.data_inicio:
                    return False

        if equipamento.estado != "danificado":
            if equipamento.estado == "emprestado":
                for emprestimo in self.emprestimos:
                    if emprestimo.codigo_equipamento == reserva.codigo_equipamento and not emprestimo.finalizado:
                        if emprestimo.esta_em_atraso():
                            return False
                        
                        elif reserva.data_inicio <= emprestimo.data_devolucao and reserva.data_fim >= emprestimo.data_retirada:
                            return False

        else:
            return False

        self.reservas.append(reserva)
        self.repositorio.salvar_reservas(self.reservas)
        return True
   