# Módulo de entrada de dados, cria, inclui na lista e converte valores para float (números reais).
def entradaDados():
  #lista = [float(item) for item in lista]                                      # Converte os valores para float utilizando list comprehension.
  lista = list(map(float, input().split()))                                     # Converte os valores para float usando "map()", aplica uma mesma ação em todos os itens de entrada, sendo um item por vez (portanto, evita a cópia).
  return lista

# Módulo verifica posição par e apresenta valores.
def verificaPosicaoPar(lista):
  #for i in range(0, len(lista), 2):                                            # Itera apenas sobre índices pares (evita usar o for e if juntos, portanto evita verificações desnecessárias dos ímpares).
  for i, valor in enumerate(lista):                                             # Percorre a lista utilizando enumerate para obter tanto o índice quanto o valor da lista.
    if i % 2 == 0:                                                              # Verifica se a posição (i) é par, caso sim, mostra o valores armazenado na posição.
      print("Valor na posição {}: {}".format(i, valor))

# Módulo principal: valoresPosicoesPares.
def main():
  lista = entradaDados()
  verificaPosicaoPar(lista)

# Chamada da função.
if __name__ == "__main__":
  main()