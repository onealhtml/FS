import time

def f(v, n):
    s = 0
    for valor in v:                         # Itera sobre os elementos do vetor
        if valor > 0:                       # Se o elemento atual for positivo, adiciona à soma
            s += valor
    return s

def main():
    inicio = time.time()                 # Armazena tempo inicial
    print(f([2, -4, 7, 0, -1, 4], 6))    # Chamada da função recursiva, argumentos: vetor de entrada e tamanho do vetor
    print("Tempo de execução: {:.6f} segundos".format(time.time() - inicio))  # Mostra o tempo de execução

main()                                   # Chamada da função