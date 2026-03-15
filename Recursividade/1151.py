"""
    Nome: 1151 - Fibonacci Fácil
    Autor: Lorenzo Farias
    FS - UNISC
"""

def fibonacci(n):                   # Função que imprime os termos de Fibonacci menores que n
    a, b = 0, 1                     # Inicializa os dois primeiros termos: a=0, b=1
    termos = []                     # Lista para armazenar os termos de Fibonacci como strings para impressão
    for _ in range(n):                      # Repete n vezes para gerar n termos
        termos.append(str(a))               # Adiciona o termo atual como string na lista
        a, b = b, a + b                     # Avança: a recebe b, e b recebe a soma de ambos
    print(' '.join(termos))                 # Imprime todos os termos separados por espaço, sem espaço no final

def main():
    n = int(input())                # Lê o limite n da sequência de Fibonacci
    fibonacci(n)                    # Chama a função passando o limite n

main()                              # Ponto de entrada do programa