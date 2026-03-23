# Módulo de entrada de dados, cria, inclui na lista e converte valores para float (números reais).
def entradaDados():
  lista = input(float).split()                                                       # split para quebrar uma linha única de valores em itens de uma lista.
  return lista

# Módulo verifica posição par e apresenta valores.
def verificaPosicaoPar(lista):
  for i in range(len(lista)):                                                   # Percorre a lista até o final.
    if i % 2 == 0:                                                              # Verifica se a posição (i) é par, caso sim, mostra o valores armazenado na posição.
      print("Valor na posição {}: {}".format(i, lista[i]))

# Módulo principal: valoresPosicoesPares.
def main():
  lista = entradaDados()
  verificaPosicaoPar(lista)

# Chamada da função.
if __name__ == "__main__":
  main()