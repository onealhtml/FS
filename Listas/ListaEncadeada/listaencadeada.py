class No:
    def __init__(self, valor, prox=None):
        self.valor = valor
        self.prox = prox

    def mostrarNo(self):
        print(self.valor)

class ListaEncadeada:
    def __init__(self):
        self.primeiro = None

    def listaVazia(self):
        return self.primeiro is None
    def mostrarLista(self):
        if self.listaVazia():
            print("Lista Vazia")
            return

        atual = self.primeiro
        while atual is not None:
            atual.mostrarNo()
            atual = atual.prox

    def inserirInicio(self, valor):
        novo = No(valor)
        novo.prox = self.primeiro
        self.primeiro = novo

    def inserirFim(self, valor):
        novo = No(valor)

        # caso 1: lista vazia
        if self.listaVazia():
            self.primeiro = novo
            return

        # caso 2: andar até o último nó
        atual = self.primeiro
        while atual.prox is not None:
            atual = atual.prox

        # liga o último ao novo nó
        atual.prox = novo

    def excluir(self, valor):
        if self.listaVazia():
            return

        if self.primeiro.valor == valor:
            self.primeiro = self.primeiro.prox
            print("Valor excluído com sucesso")
            return

        anterior = self.primeiro
        atual = self.primeiro.prox

        while atual is not None and atual.valor != valor:
            anterior = atual
            atual = atual.prox

        if atual is None:
            print("Valor não encontrado")

        anterior.prox = atual.prox
        print("Valor excluído com sucesso")

    def pesquisar(self, valor):
        if self.listaVazia():
            print("Lista vazia")
            return False

        atual = self.primeiro

        while atual is not None and atual.valor != valor:
            atual = atual.prox

        if atual is None:
            print("Valor não encontrado")
            return False

        print("Valor encontrado")
        return True

    def ordenar(self):
        return