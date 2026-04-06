class ListaEncadeada:
    def __init__(self):
        self._primeiro = None

    def get_primeiro(self):
        return self._primeiro

    def lista_vazia(self):
        return self._primeiro is None

    def mostrar_lista(self):
        if self.lista_vazia():
            print("Lista Vazia")
            return

        atual = self._primeiro
        while atual is not None:
            print(atual)
            atual = atual.get_prox()

    def inserir_inicio(self, novo):
        novo.set_prox(self._primeiro)
        self._primeiro = novo

    def inserir_fim(self, novo):
        novo.set_prox(None)

        # caso 1: lista vazia
        if self.lista_vazia():
            self._primeiro = novo
            return

        # caso 2: andar ate o ultimo no
        atual = self._primeiro
        while atual.get_prox() is not None:
            atual = atual.get_prox()

        # liga o ultimo ao novo no
        atual.set_prox(novo)

    def excluir(self, valor):
        if self.lista_vazia():
            return False

        if self._primeiro is valor:
            self._primeiro = self._primeiro.get_prox()
           # print("Valor excluido com sucesso")
            return True

        anterior = self._primeiro
        atual = self._primeiro.get_prox()

        while atual is not None and atual is not valor:
            anterior = atual
            atual = atual.get_prox()

        if atual is None:
            print("Valor não encontrado")
            return False

        anterior.set_prox(atual.get_prox())
        print("Valor excluido com sucesso")
        return True

    def iterar_valores(self):
        atual = self._primeiro
        while atual is not None:
            yield atual
            atual = atual.get_prox()

    def pesquisar(self, valor):
        if self.lista_vazia():
            print("Lista vazia")
            return False

        atual = self._primeiro

        while atual is not None and atual is not valor:
            atual = atual.get_prox()

        if atual is None:
            print("Valor nao encontrado")
            return False

        print("Valor encontrado")
        return True

    def ordenar(self):
        if self.lista_vazia():
            return "Lista vazia"

        houve_troca = True
        while houve_troca:
            houve_troca = False
            atual = self._primeiro

            while atual is not None and atual.get_prox() is not None:
                proximo = atual.get_prox()
                if atual.get_numero() > proximo.get_numero():
                    numero_atual = atual.get_numero()
                    titular_atual = atual.get_titular()
                    cpf_atual = atual.get_cpf()
                    saldo_atual = atual.get_saldo()

                    atual.set_numero(proximo.get_numero())
                    atual.set_titular(proximo.get_titular())
                    atual.set_cpf(proximo.get_cpf())
                    atual.set_saldo(proximo.get_saldo())

                    proximo.set_numero(numero_atual)
                    proximo.set_titular(titular_atual)
                    proximo.set_cpf(cpf_atual)
                    proximo.set_saldo(saldo_atual)
                    houve_troca = True
                atual = atual.get_prox()

        return "Lista ordenada com sucesso"

    # Aliases para manter compatibilidade com nomes antigos usados no projeto.
    def listaVazia(self):
        return self.lista_vazia()

    def mostrarLista(self):
        self.mostrar_lista()

    def inserirInicio(self, novo):
        self.inserir_inicio(novo)

    def inserirFim(self, novo):
        self.inserir_fim(novo)

    def iterarValores(self):
        yield from self.iterar_valores()

