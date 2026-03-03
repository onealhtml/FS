"""
    Nome: 1113 - Crescente e Decrescente
    Autor: Lorenzo Farias
    FS - UNISC
"""

def main():
    saida = 1           # Variável para controlar a saída do loop
    while saida == 1:   # Loop principal para ler os casos de teste
        x, y = entrada()
        saida = logica(x, y)

def entrada():
    x, y = map(int, input().split())
    return x, y

def logica(x, y):
    if x < y:                           # Verifica se é crescente
        print("Crescente")
        return 1
    elif x > y:                         # Verifica se é decrescente
        print("Decrescente")
        return 1
    elif x == y:                        # Caso x e y sejam iguais, sai do loop
        return 0
    return None


main()  # Ponto de entrada do programa