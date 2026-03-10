import time

def f(v, n):
    if n == 0:
        return v[0]
    else:
        s = f(v, n-1)
        if v[n-1] > 0:
            s += v[n-1]
        return s

def main():
    inicio = time.time()                 # Armazena tempo inicial
    print(f([2, -4, 7, 0, -1, 4], 6))    # Chamada da função recursiva, argumentos: vetor de entrada e tamanho do vetor
    print("Tempo de execução: {:.6f} segundos".format(time.time() - inicio))  # Mostra o tempo de execução

main()                                   # Chamada da função