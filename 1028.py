"""
    Nome: 1028 - Figurinhas
    Autor: Lorenzo Farias
    FS - UNISC
"""

def main():
    n = int(input())    # Lê a quantidade de casos de teste
    entrada(n)          # Chama a função de entrada com n casos

def entrada(n):
    for _ in range(n):                          # Repete n vezes
        f1, f2 = map(int, input().split())      # Lê dois inteiros f1 e f2
        mdc = calculoMDC(f1, f2)                # Chama a função de cálculo do MDC com f1 e f2
        print(mdc)                              # Imprime o resultado do MDC

def calculoMDC(f1, f2):
    if f2 == 0:                                 # Caso base: se f2 for 0, o MDC é f1
        return f1                               # Retorna f1 como resultado final
    else:
        return calculoMDC(f2, f1 % f2)          # Chamada recursiva: MDC(f2, resto de f1 dividido por f2)

if __name__ == '__main__':
    main()  # Ponto de entrada do programa