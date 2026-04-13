import argparse # Importa módulo para processar argumentos de linha de comando
from pathlib import Path # Importa módulo para trabalhar com caminhos de arquivo

from banco import Banco # Importa a classe Banco para gerenciar o banco


def _mensagem_resumida(msg: str, max_erros: int) -> str: # Função para resumir mensagens com muitos erros
    linhas = msg.splitlines() # Divide a mensagem em linhas
    if len(linhas) <= 1 or max_erros < 0: # Se tem 1 linha ou max_erros é -1 (mostrar tudo)
        return msg # Retorna a mensagem completa

    resumo = linhas[0] # Primeira linha é o resumo
    detalhes = linhas[1:] # Linhas restantes são detalhes de erros

    if len(detalhes) <= max_erros: # Se erros cabem no limite
        return msg # Retorna mensagem completa

    exibidas = detalhes[:max_erros] # Pega apenas os primeiros max_erros detalhes
    restante = len(detalhes) - max_erros # Calcula quantos erros foram omitidos
    return "\n".join([resumo, *exibidas, f"... ({restante} erro(s) omitido(s))"])  # Retorna resumida com contagem


def main() -> int: # Função principal que retorna código de saída
    parser = argparse.ArgumentParser( # Cria parser de argumentos
        description="Smoke test: importa CSV e mostra estatísticas/buckets da tabela hash dinâmica." # Descrição
    )
    parser.add_argument( # Define argumento para caminho do CSV
        "--csv",
        default=str(Path(__file__).with_name("clientes_banco.csv")), # Padrão: clientes_banco.csv na mesma pasta
        help="Caminho do CSV (padrão: Desafio1/clientes_banco.csv).",
    )
    parser.add_argument( # Define argumento para tamanho da tabela
        "--table-size",
        type=int,
        default=101, # Padrão: 101
        help="Tamanho inicial da tabela hash (padrão: 101).",
    )
    parser.add_argument( # Define argumento para fator de carga máximo
        "--max-load-factor",
        type=float,
        default=0.75, # Padrão: 0.75
        help="Fator de carga máximo antes de redimensionar (padrão: 0.75).",
    )
    parser.add_argument( # Define argumento para delimitador do CSV
        "--delimitador",
        default=",", # Padrão: vírgula
        help="Delimitador do CSV (padrão: ',').",
    )
    parser.add_argument( # Define flag para mostrar buckets vazios
        "--mostrar-vazios",
        action="store_true", # True se argumento está presente
        help="Mostra buckets vazios no debug da hash.",
    )
    parser.add_argument( # Define argumento para quantidade máxima de erros a exibir
        "--max-erros",
        type=int,
        default=20, # Padrão: 20 erros
        help="Quantidade máxima de erros detalhados no print (padrão: 20, -1 mostra todos).",
    )
    parser.add_argument( # Define flag para mostrar apenas resumo
        "--somente-resumo",
        action="store_true", # True se argumento está presente
        help="Mostra apenas resumo e estatísticas da hash, sem listar buckets.",
    )

    args = parser.parse_args() # Processa os argumentos passados

    banco = Banco(table_size=args.table_size, max_load_factor=args.max_load_factor) # Cria banco com argumentos
    ok, msg = banco.importar_contas_csv(args.csv, delimitador=args.delimitador) # Importa contas do CSV
    stats = banco.estatisticas_hash() # Obtém estatísticas da hash

    print(f"[{ok}] Importação de '{args.csv}'") # Exibe resultado da importação
    print(_mensagem_resumida(msg, args.max_erros)) # Exibe mensagem resumida se muitos erros

    print("\nEstatísticas da hash:") # Cabeçalho das estatísticas
    print( # Exibe estatísticas em uma única linha
        " | ".join(
            [
                f"table_size={stats['table_size']}", # Tamanho da tabela
                f"total_contas={stats['total_contas']}", # Total de contas
                f"buckets_usados={stats['buckets_usados']}", # Buckets com contas
                f"buckets_vazios={stats['buckets_vazios']}", # Buckets vazios
                f"fator_carga={stats['fator_carga']:.4f}", # Fator de carga com 4 casas decimais
                f"media_cadeia={stats['media_cadeia_bucket_usado']:.4f}", # Média de contas por bucket ocupado
                f"maior_cadeia={stats['maior_cadeia']}", # Tamanho da maior cadeia
                f"max_load_factor={stats['max_load_factor']}", # Fator de carga máximo configurado
            ]
        )
    )

    if not args.somente_resumo: # Se não está apenas para resumo
        print("\nDistribuição dos buckets:") # Cabeçalho
        print(banco.debug_buckets()) # Exibe buckets (vazios ou não)

    return 0 if ok else 1 # Retorna 0 se sucesso, 1 se erro


if __name__ == "__main__": # Verifica se script está sendo executado diretamente
    try: # Tenta executar
        raise SystemExit(main()) # Executa main e encerra com código de saída
    except BrokenPipeError: # Se houver erro de pipe quebrado (ex: output interrompido)
        pass # Ignora o erro

