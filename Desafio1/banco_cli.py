from banco import Banco
import os


def ler_int(mensagem):
    while True:
        try:
            return int(input(mensagem).strip())
        except ValueError:
            print("Entrada inválida. Digite um número inteiro.")


def ler_float(mensagem):
    while True:
        try:
            return float(input(mensagem).strip().replace(",", "."))
        except ValueError:
            print("Entrada inválida. Digite um número válido.")


def limpar_tela():
    # 'nt' é o caso para Windows
    if os.name == 'nt':
        os.system('cls')
    # Para Linux e macOS
    else:
        os.system('clear')


def mostrar_menu():
    print("=== Banco Grêmio ===")
    print("1 - Inclusão de conta")
    print("2 - Exclusão de conta")
    print("3 - Consulta de conta")
    print("4 - Relatório")
    print("5 - Depósito")
    print("6 - Saque")
    print("7 - Importar contas via CSV")
    print("0 - Sair\n")


def executar_cli():
    banco = Banco()
    executando = True

    while executando:
        limpar_tela()
        mostrar_menu()
        opcao = input("Escolha uma opção: ").strip()
        limpar_tela()

        if opcao == "1":
            titular = input("Titular da conta: ").strip()
            cpf = input("CPF do titular (11 digitos): ").strip()
            ok, msg = banco.incluir_conta(titular, cpf)
            print(msg)

        elif opcao == "2":
            numero = ler_int("Número da conta para excluir: ")
            ok, msg = banco.excluir_conta(numero)
            print(msg)

        elif opcao == "3":
            numero = ler_int("Número da conta para consulta: ")
            ok, msg, conta = banco.consultar_conta(numero)
            print(msg)
            if ok:
                print(conta)

        elif opcao == "4":
            print(banco.gerar_relatorio())

        elif opcao == "5":
            numero = ler_int("Número da conta para depósito: ")
            valor = ler_float("Valor do depósito: ")
            ok, msg = banco.depositar(numero, valor)
            print(msg)

        elif opcao == "6":
            numero = ler_int("Número da conta para saque: ")
            valor = ler_float("Valor do saque: ")
            ok, msg = banco.sacar(numero, valor)
            print(msg)

        elif opcao == "7":
            caminho = input("Caminho do CSV: ").strip()
            delimitador = input("Delimitador (Enter para ','): ").strip() or ","
            ok, msg = banco.importar_contas_csv(caminho, delimitador)
            print(msg)

        elif opcao == "0":
            print("Encerrando sistema...")
            executando = False

        else:
            print("Opção inválida.")

        if executando:
            input("\nPressione Enter para voltar ao menu...")

executar_cli()