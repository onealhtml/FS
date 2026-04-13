import argparse
from pathlib import Path

from banco import Banco


def _mensagem_resumida(msg: str, max_erros: int) -> str:
    linhas = msg.splitlines()
    if len(linhas) <= 1 or max_erros < 0:
        return msg

    resumo = linhas[0]
    detalhes = linhas[1:]

    if len(detalhes) <= max_erros:
        return msg

    exibidas = detalhes[:max_erros]
    restante = len(detalhes) - max_erros
    return "\n".join([resumo, *exibidas, f"... ({restante} erro(s) omitido(s))"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Smoke test: importa CSV e mostra estatísticas/buckets da tabela hash dinâmica."
    )
    parser.add_argument(
        "--csv",
        default=str(Path(__file__).with_name("clientes_banco.csv")),
        help="Caminho do CSV (padrão: Desafio1/clientes_banco.csv).",
    )
    parser.add_argument(
        "--table-size",
        type=int,
        default=101,
        help="Tamanho inicial da tabela hash (padrão: 101).",
    )
    parser.add_argument(
        "--max-load-factor",
        type=float,
        default=0.75,
        help="Fator de carga máximo antes de redimensionar (padrão: 0.75).",
    )
    parser.add_argument(
        "--delimitador",
        default=",",
        help="Delimitador do CSV (padrão: ',').",
    )
    parser.add_argument(
        "--mostrar-vazios",
        action="store_true",
        help="Mostra buckets vazios no debug da hash.",
    )
    parser.add_argument(
        "--max-erros",
        type=int,
        default=20,
        help="Quantidade máxima de erros detalhados no print (padrão: 20, -1 mostra todos).",
    )
    parser.add_argument(
        "--somente-resumo",
        action="store_true",
        help="Mostra apenas resumo e estatísticas da hash, sem listar buckets.",
    )

    args = parser.parse_args()

    banco = Banco(table_size=args.table_size, max_load_factor=args.max_load_factor)
    ok, msg = banco.importar_contas_csv(args.csv, delimitador=args.delimitador)
    stats = banco.estatisticas_hash()

    print(f"[{ok}] Importação de '{args.csv}'")
    print(_mensagem_resumida(msg, args.max_erros))

    print("\nEstatísticas da hash:")
    print(
        " | ".join(
            [
                f"table_size={stats['table_size']}",
                f"total_contas={stats['total_contas']}",
                f"buckets_usados={stats['buckets_usados']}",
                f"buckets_vazios={stats['buckets_vazios']}",
                f"fator_carga={stats['fator_carga']:.4f}",
                f"media_cadeia={stats['media_cadeia_bucket_usado']:.4f}",
                f"maior_cadeia={stats['maior_cadeia']}",
                f"max_load_factor={stats['max_load_factor']}",
            ]
        )
    )

    if not args.somente_resumo:
        print("\nDistribuição dos buckets:")
        print(banco.debug_buckets())

    return 0 if ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        pass

