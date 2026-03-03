"""
    Nome: 1168 - LED
    Autor: Lorenzo Farias
    FS - UNISC
"""

def processar(N, nLeds):                # Função com loop principal para percorrer os casos de teste
    for i in range(int(N)):
        numero = input().strip()        # Lê o número como string diretamente
        leds = calcLeds(numero, nLeds)  # Calcula a quantidade de leds do número lido
        print(f"{leds} leds")           # Exibe o resultado

def calcLeds(numero, nLeds):            # Função para calcular a quantidade de leds de um número
    totalLeds = 0                       # Acumulador do total de leds

    for j in range(len(numero)):                        # Percorre caractere por caractere do número
        if not numero[j].isdigit():                     # Verifica se o caractere é um dígito válido
            print(f"Caractere invalido: {numero[j]}")   # Avisa caso encontre caractere inválido
            continue

        totalLeds += nLeds[int(numero[j])]  # Soma os leds do dígito atual ao total

    return totalLeds                    # Retorna o total de leds calculado

def main():
    nLeds = [6, 2, 5, 5, 4, 5, 6, 3, 7, 6]    # Quantidade de leds de cada dígito (0 a 9)

    N = int(input())                    # Lê a quantidade de casos de teste

    processar(N, nLeds)                 # Processa todos os casos de teste

if __name__ == '__main__':
    main()                              # Ponto de entrada do programa
