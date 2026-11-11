def menu_principal():
#FUNÇÃO DO MENU PRINCIPAL COM LOOP E SWITCH CASE
    while True:
        print("""
        ==============================
        Almoxarifado - Bosque Novo
        ==============================

        [1] Registrar empréstimo
        [2] Registrar devolução
        [3] Consultar disponibilidade
        [4] Reservas
        [5] Cadastros
        [6] Liberar equipamento danificado
        [7] Resumo mensal
        [0] Sair
    
        """)

        escolha = int(input("Escolha uma opção: "))

        match escolha:
            case 0:
                print("Programa finalizado!")
                break

            case 1:
                break

            case 2:
                break

            case 3:
                break

            case 4:
                submenu_reservas()
                break

            case 5:
                menu_cadastros()

            case 6:
                break

            case 7:
                break

            case _:
                print("Opção inválida! Tente novamente!")
    return

def menu_cadastros():
#FUNÇÃO DO MENU DE CADASTROS(OPÇÃO 5) COM LOOP E SWITCH CASE
    while True: 
        print("""
    ==========CADASTROS=========

    [1] Cadastrar equipamento
    [2] Listar equipamentos
    [3] Cadastrar usuário
    [0] Voltar ao menu principal
    """)
        escolha = int(input("Escolha uma opção: "))

        match escolha:
            case 0:
                return

            case 1:
                break

            case 2:
                break

            case 3:
                break

            case _:
                print("Opção inválida! Tente Novamente")
    return

def registrar_emprestimo():
    return

def submenu_reservas():
    reservas = int(input( "Para checar os itens reservados, digite 1:"))
    match reservas:
        case 1: 
            print ( f"Os itens reservados são: {reservados} " )
        case _:
            print ( " Opção inválida! Tente novamente")
	
		
					


