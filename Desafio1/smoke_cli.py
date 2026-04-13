from banco import Banco

def main():
    banco = Banco(table_size=11, hash_strategy="divisao")

    operacoes = [
        banco.incluir_conta("Ana", "11111111111"),
        banco.incluir_conta("Bruno", "22222222222"),
        banco.depositar(1001, 150.0),
        banco.depositar(1002, 90.0),
        banco.sacar(1001, 50.0),
    ]

    # Massa adicional para tornar o comparativo das hashes mais representativo.
    for i in range(3, 103):
        banco.incluir_conta(f"Cliente {i}", f"{i:011d}")

    for ok, msg in operacoes:
        print(f"[{ok}] {msg}")

    ok, msg, conta = banco.consultar_conta(1001)
    print(f"[{ok}] {msg}")
    if conta is not None:
        print(conta)

    print()
    print(banco.gerar_relatorio())
    print()
    print(banco.listar_buckets(mostrar_vazios=True))
    print()
    print(banco.relatorio_metricas_hash())
    print()
    print(banco.relatorio_comparativo_hash(repeticoes_busca=20))


if __name__ == "__main__":
    main()

