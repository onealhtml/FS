from banco import Banco


def main():
    banco = Banco()

    operacoes = [
        banco.incluir_conta("Ana", "11111111111"),
        banco.incluir_conta("Bruno", "22222222222"),
        banco.depositar(1001, 150.0),
        banco.depositar(1002, 90.0),
        banco.sacar(1001, 50.0),
    ]

    for ok, msg in operacoes:
        print(f"[{ok}] {msg}")

    ok, msg, conta = banco.consultar_conta(1001)
    print(f"[{ok}] {msg}")
    if conta is not None:
        print(conta)

    print()
    print(banco.gerar_relatorio())


if __name__ == "__main__":
    main()

