"""
    Nome: 1113 - Crescente e Decrescente
    Autor: Lorenzo Farias
    FS - UNISC
"""

def main():
    saida = 1          # Variável para controlar a saída do loop
    while saida == 1:   # Loop principal para ler os casos de teste
        x, y = entrada()
        logica(x, y)

def entrada():
    x, y = map(int, input().split())
    return x, y

def logica(x, y):
    if x < y:                           # Verifica se é crescente
        print("Crescente")
    elif x > y:                         # Verifica se é decrescente
        print("Decrescente")
    else:                               # Caso x e y sejam iguais, sai do loop
        saida = 0

main()  # Ponto de entrada do programa