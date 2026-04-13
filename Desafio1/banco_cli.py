from banco import Banco # Importa a classe Banco para gerenciar contas
import os # Importa módulo do sistema operacional para limpeza de tela


def ler_int(mensagem): # Função para ler um número inteiro com validação
    while True: # Loop infinito até entrada válida
        try: # Tenta converter entrada para inteiro
            return int(input(mensagem).strip()) # Retorna o inteiro se sucesso
        except ValueError: # Se conversão falhar
            print("Entrada inválida. Digite um número inteiro.") # Exibe erro


def ler_float(mensagem): # Função para ler um número decimal com validação
    while True: # Loop infinito até entrada válida
        try: # Tenta converter entrada para float
            return float(input(mensagem).strip().replace(",", ".")) # Retorna float, convertendo vírgula em ponto
        except ValueError: # Se conversão falhar
            print("Entrada inválida. Digite um número válido.") # Exibe erro


def limpar_tela(): # Função para limpar a tela do console
    if os.name == 'nt': # Verifica se o SO é Windows ('nt' = Windows)
        os.system('cls') # Executa comando 'cls' para limpar tela no Windows
    else: # Para Linux e macOS
        os.system('clear') # Executa comando 'clear' para limpar tela


def mostrar_menu(): # Função para exibir o menu principal do banco
    print("=== Banco Grêmio ===") # Cabeçalho do menu
    print("1 - Inclusão de conta") # Opção 1
    print("2 - Exclusão de conta") # Opção 2
    print("3 - Consulta de conta") # Opção 3
    print("4 - Relatório") # Opção 4
    print("5 - Depósito") # Opção 5
    print("6 - Saque") # Opção 6
    print("7 - Importar contas via CSV") # Opção 7
    print("8 - Mostrar lista por bucket") # Opção 8
    print("9 - Mostrar métricas da hash") # Opção 9
    print("10 - Comparar divisão x fnv1a") # Opção 10
    print("0 - Sair\n") # Opção para sair


def executar_cli(): # Função principal que executa a interface de linha de comando
    banco = Banco() # Cria uma instância do banco com configurações padrão
    executando = True # Flag para controlar o loop principal

    while executando: # Loop principal da CLI
        limpar_tela() # Limpa a tela antes de exibir menu
        mostrar_menu() # Exibe o menu de opções
        opcao = input("Escolha uma opção: ").strip() # Lê a opção do usuário
        limpar_tela() # Limpa tela novamente

        if opcao == "1": # Se opção é incluir conta
            titular = input("Titular da conta: ").strip() # Lê o nome do titular
            cpf = input("CPF do titular (11 digitos): ").strip() # Lê o CPF
            ok, msg = banco.incluir_conta(titular, cpf) # Inclui a conta no banco
            print(msg) # Exibe resultado da operação

        elif opcao == "2": # Se opção é excluir conta
            numero = ler_int("Número da conta para excluir: ") # Lê número da conta
            ok, msg = banco.excluir_conta(numero) # Exclui a conta
            print(msg) # Exibe resultado

        elif opcao == "3": # Se opção é consultar conta
            numero = ler_int("Número da conta para consulta: ") # Lê número da conta
            ok, msg, conta = banco.consultar_conta(numero) # Consulta a conta
            print(msg) # Exibe resultado
            if ok: # Se encontrou a conta
                print(conta) # Exibe dados da conta

        elif opcao == "4": # Se opção é gerar relatório
            print(banco.gerar_relatorio()) # Exibe relatório completo

        elif opcao == "5": # Se opção é fazer depósito
            numero = ler_int("Número da conta para depósito: ") # Lê número da conta
            valor = ler_float("Valor do depósito: ") # Lê valor do depósito
            ok, msg = banco.depositar(numero, valor) # Realiza o depósito
            print(msg) # Exibe resultado

        elif opcao == "6": # Se opção é fazer saque
            numero = ler_int("Número da conta para saque: ") # Lê número da conta
            valor = ler_float("Valor do saque: ") # Lê valor do saque
            ok, msg = banco.sacar(numero, valor) # Realiza o saque
            print(msg) # Exibe resultado

        elif opcao == "7": # Se opção é importar CSV
            caminho = input("Caminho do CSV: ").strip() # Lê caminho do arquivo
            delimitador = input("Delimitador (Enter para ','): ").strip() or "," # Lê delimitador ou usa ','
            ok, msg = banco.importar_contas_csv(caminho, delimitador) # Importa contas do CSV
            print(msg) # Exibe resultado

        elif opcao == "8": # Se opção é listar buckets
            mostrar_vazios = input("Mostrar buckets vazios? [s/N]: ").strip().lower() == "s" # Pergunta se mostra vazios
            print(banco.listar_buckets(mostrar_vazios=mostrar_vazios)) # Exibe buckets

        elif opcao == "9": # Se opção é mostrar métricas
            print(banco.relatorio_metricas_hash()) # Exibe métricas da tabela hash

        elif opcao == "10": # Se opção é comparar estratégias
            repeticoes_txt = input("Repetições para benchmark de busca (Enter para 5): ").strip() # Lê repetições
            try: # Tenta converter para inteiro
                repeticoes = int(repeticoes_txt) if repeticoes_txt else 5 # Usa valor ou padrão 5
            except ValueError: # Se conversão falhar
                print("Valor inválido. Usando 5 repetições.") # Exibe erro
                repeticoes = 5 # Define padrão
            print(banco.relatorio_comparativo_hash(repeticoes_busca=repeticoes)) # Exibe comparativo

        elif opcao == "0": # Se opção é sair
            print("Encerrando sistema...") # Exibe mensagem de encerramento
            executando = False # Define flag para sair do loop

        else: # Se opção inválida
            print("Opção inválida.") # Exibe erro

        if executando: # Se ainda está executando
            input("\nPressione Enter para voltar ao menu...") # Aguarda Enter para continuar

executar_cli() # Executa a interface de linha de comando
