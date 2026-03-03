"""
    Nome: 1180 - Menor e Posição
    Autor: Lorenzo Farias
    FS - UNISC
"""

def main():
    n = int(input())                    # Lê a quantidade de elementos do vetor
    vetor = entradaVal(n)               # Preenche o vetor com os valores fornecidos pelo usuário
    menor, posicao = calcValor(vetor)   # Calcula o menor valor e sua posição no vetor
    print(f"Menor valor: {menor}")      # Exibe o menor valor encontrado
    print(f"Posicao: {posicao + 1}")    # Exibe a posição (base 1) do menor valor

def entradaVal(n):
    valores = list(map(int, input().split()))  # Lê uma linha e converte cada elemento para inteiro
    return valores[:n]                         # Retorna apenas os primeiros n elementos

def calcValor(vetor):
    menor = vetor[0]    # Inicializa o menor valor com o primeiro elemento do vetor
    posicao = 0         # Inicializa a posição do menor valor como 0 (índice base 0)
    for i, num in enumerate(vetor):            # Percorre o vetor comparando cada elemento
        if num < menor:
            menor = num     # Atualiza o menor valor
            posicao = i     # Atualiza a posição do menor valor
    return menor, posicao

main()  # Ponto de entrada do programa
