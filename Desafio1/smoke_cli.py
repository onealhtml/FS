from banco import Banco # Importa a classe Banco para criar e gerenciar o banco

def main(): # Função principal que executa testes de smoke no sistema
    banco = Banco(table_size=11, hash_strategy="divisao") # Cria banco com tamanho 11 e estratégia divisão

    operacoes = [ # Lista com as primeiras operações de teste
        banco.incluir_conta("Ana", "11111111111"), # Inclui conta de Ana
        banco.incluir_conta("Bruno", "22222222222"), # Inclui conta de Bruno
        banco.depositar(1001, 150.0), # Deposita R$ 150 na conta de Ana
        banco.depositar(1002, 90.0), # Deposita R$ 90 na conta de Bruno
        banco.sacar(1001, 50.0), # Saca R$ 50 da conta de Ana
    ]

    # Massa adicional para tornar o comparativo das hashes mais representativo.
    # Insere mais 100 contas (clientes 3 a 102) para ter dados suficientes para testes
    for i in range(3, 103): # Loop de 3 a 102
        banco.incluir_conta(f"Cliente {i}", f"{i:011d}") # Inclui cliente i com CPF formatado em 11 dígitos

    for ok, msg in operacoes: # Itera sobre os resultados das operações iniciais
        print(f"[{ok}] {msg}") # Exibe sucesso e mensagem de cada operação

    ok, msg, conta = banco.consultar_conta(1001) # Consulta a conta 1001 (Ana)
    print(f"[{ok}] {msg}") # Exibe resultado da consulta
    if conta is not None: # Se encontrou a conta
        print(conta) # Exibe os dados da conta

    print() # Exibe linha vazia
    print(banco.gerar_relatorio()) # Exibe relatório completo de todas as contas
    print() # Exibe linha vazia
    print(banco.listar_buckets(mostrar_vazios=True)) # Exibe todos os buckets, inclusive vazios
    print() # Exibe linha vazia
    print(banco.relatorio_metricas_hash()) # Exibe métricas da tabela hash
    print() # Exibe linha vazia
    print(banco.relatorio_comparativo_hash(repeticoes_busca=20)) # Exibe comparativo das 3 estratégias com 20 repetições


if __name__ == "__main__": # Verifica se o script está sendo executado diretamente (não importado)
    main() # Executa a função principal

