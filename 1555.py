"""
    Nome: 1555 - Funções
    Autor: Lorenzo Farias
    FS - UNISC
"""

def main():
    N = int(input())    # Lê a quantidade de casos de teste
    entrada(N)          # Chama a função de entrada com N casos

def entrada(n):
    for _ in range(n):                          # Repete n vezes
        x, y = map(int, input().split())        # Lê dois inteiros x e y
        calculo(x, y)                           # Chama a função de cálculo com x e y

def calculo(x, y):
    rafael = (3 * x) ** 2 + y ** 2             # Fórmula do Rafael
    beto = 2 * x ** 2 + (5 * y) ** 2           # Fórmula do Beto
    carlos = -100 * x + y ** 3                 # Fórmula do Carlos

    if rafael > beto and rafael > carlos:       # Rafael tem o maior valor
        print(f"Rafael ganhou")
    elif beto > rafael and beto > carlos:       # Beto tem o maior valor
        print(f"Beto ganhou")
    elif carlos > rafael and carlos > beto:     # Carlos tem o maior valor
        print(f"Carlos ganhou")

main()  # Ponto de entrada do programa