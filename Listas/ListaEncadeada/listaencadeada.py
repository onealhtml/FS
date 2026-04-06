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
            print("Lista vazia\n")
            return

        atual = self.primeiro
        while atual is not None:
            atual.mostrarNo()
            atual = atual.prox

        print("")

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
            print("Lista vazia\n")
            return

        if self.primeiro.valor == valor:
            self.primeiro = self.primeiro.prox
            print("Valor excluído com sucesso\n")
            return

        anterior = self.primeiro
        atual = self.primeiro.prox

        while atual is not None and atual.valor != valor:
            anterior = atual
            atual = atual.prox

        if atual is None:
            print("Valor não encontrado\n")
            return

        anterior.prox = atual.prox
        print("Valor excluído com sucesso\n")

    def pesquisar(self, valor):
        if self.listaVazia():
            print("Lista vazia\n")
            return False

        atual = self.primeiro

        while atual is not None and atual.valor != valor:
            atual = atual.prox

        if atual is None:
            print("Valor não encontrado\n")
            return False

        print("Valor encontrado\n")
        return True

    def ordenar(self):
        if self.listaVazia():
            print("Lista vazia\n")
            return
        
        houve_troca = True
        
        while houve_troca:
            houve_troca = False
            atual = self.primeiro
            while atual.prox is not None:
                if atual.valor > atual.prox.valor:
                    temp = atual.valor
                    atual.valor = atual.prox.valor
                    atual.prox.valor = temp
                    houve_troca = True

                atual = atual.prox
        print("Lista ordenada!\n")
        return