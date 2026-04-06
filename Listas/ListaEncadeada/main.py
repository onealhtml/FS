
import listaencadeada

def main():
    lista = listaencadeada.ListaEncadeada()  # Cria uma instância da classe ListaEncadeada
    lista.inserirInicio(10)                          # Insere o valor 10 na lista
    lista.inserirInicio(20)                          # Insere o valor 20 na lista
    lista.inserirInicio(30)                          # Insere o valor 30 na lista
    lista.inserirFim(40)

    lista.mostrarLista()

    lista.ordenar()  # Ordena a lista

    lista.mostrarLista()

if __name__ == "__main__":
  main()