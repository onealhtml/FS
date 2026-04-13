class ListaEncadeada: # Classe para implementar uma lista encadeada com operações de inserção, exclusão e busca
    def __init__(self): # Inicializa a lista vazia com o primeiro nó apontando para None
        self._primeiro = None # Variável que aponta para o primeiro nó da lista

    def get_primeiro(self): # Método que retorna o primeiro nó da lista
        return self._primeiro # Retorna o nó inicial

    def lista_vazia(self): # Método que verifica se a lista está vazia
        return self._primeiro is None # Retorna True se a lista está vazia, False caso contrário

    def mostrar_lista(self): # Método que exibe todos os elementos da lista
        if self.lista_vazia(): # Verifica se a lista está vazia
            print("Lista Vazia") # Exibe mensagem se vazia
            return # Encerra a função

        atual = self._primeiro # Inicializa o ponteiro atual no primeiro nó
        while atual is not None: # Percorre todos os nós da lista
            print(atual) # Exibe o nó atual
            atual = atual.get_prox() # Avança para o próximo nó

    def inserir_inicio(self, novo): # Método para inserir um novo nó no início da lista
        novo.set_prox(self._primeiro) # O novo nó aponta para o que era o primeiro
        self._primeiro = novo # O novo nó passa a ser o primeiro da lista

    def inserir_fim(self, novo): # Método para inserir um novo nó no final da lista
        novo.set_prox(None) # O novo nó não aponta para ninguém (será o último)

        if self.lista_vazia(): # Caso 1: verifica se a lista está vazia
            self._primeiro = novo # Se vazia, o novo nó passa a ser o primeiro
            return # Encerra a função

        atual = self._primeiro # Caso 2: inicializa o ponteiro no primeiro nó
        while atual.get_prox() is not None: # Percorre até encontrar o último nó
            atual = atual.get_prox() # Avança para o próximo nó

        atual.set_prox(novo) # Liga o último nó ao novo nó

    def excluir(self, valor): # Método para excluir um nó específico da lista
        if self.lista_vazia(): # Verifica se a lista está vazia
            return False # Retorna False se não há nada para excluir

        if self._primeiro is valor: # Verifica se o nó a excluir é o primeiro
            self._primeiro = self._primeiro.get_prox() # O primeiro passa a ser o segundo nó
            return True # Retorna True indicando sucesso

        anterior = self._primeiro # Inicializa o ponteiro anterior no primeiro nó
        atual = self._primeiro.get_prox() # Inicializa o ponteiro atual no segundo nó

        while atual is not None and atual is not valor: # Percorre a lista procurando o nó
            anterior = atual # Avança o ponteiro anterior
            atual = atual.get_prox() # Avança o ponteiro atual

        if atual is None: # Se não encontrou o nó na lista
            print("Valor não encontrado") # Exibe mensagem de erro
            return False # Retorna False

        anterior.set_prox(atual.get_prox()) # Liga o nó anterior ao próximo do nó a excluir
        print("Valor excluido com sucesso") # Exibe mensagem de sucesso
        return True # Retorna True indicando sucesso

    def iterar_valores(self): # Método gerador para iterar sobre todos os nós da lista
        atual = self._primeiro # Inicializa o ponteiro no primeiro nó
        while atual is not None: # Percorre todos os nós
            yield atual # Retorna o nó atual
            atual = atual.get_prox() # Avança para o próximo nó

    def pesquisar(self, valor): # Método para buscar um nó específico na lista
        if self.lista_vazia(): # Verifica se a lista está vazia
            print("Lista vazia") # Exibe mensagem
            return False # Retorna False

        atual = self._primeiro # Inicializa o ponteiro no primeiro nó

        while atual is not None and atual is not valor: # Percorre a lista procurando o nó
            atual = atual.get_prox() # Avança para o próximo nó

        if atual is None: # Se não encontrou o nó
            print("Valor nao encontrado") # Exibe mensagem de não encontrado
            return False # Retorna False

        print("Valor encontrado") # Exibe mensagem de encontrado
        return True # Retorna True indicando sucesso

    def ordenar(self): # Método para ordenar a lista em ordem crescente usando Bubble Sort
        if self.lista_vazia(): # Verifica se a lista está vazia
            return "Lista vazia" # Retorna mensagem se vazia

        houve_troca = True # Flag para controlar se houve troca na iteração
        while houve_troca: # Continua até não haver mais trocas
            houve_troca = False # Reinicia a flag assumindo que não há trocas
            atual = self._primeiro # Inicializa o ponteiro no primeiro nó

            while atual is not None and atual.get_prox() is not None: # Percorre até o penúltimo nó
                proximo = atual.get_prox() # Pega o próximo nó para comparação
                if atual.get_numero() > proximo.get_numero(): # Compara os números das contas
                    # Armazena os dados do nó atual
                    numero_atual = atual.get_numero()
                    titular_atual = atual.get_titular()
                    cpf_atual = atual.get_cpf()
                    saldo_atual = atual.get_saldo()

                    # Copia os dados do próximo nó para o nó atual
                    atual.set_numero(proximo.get_numero())
                    atual.set_titular(proximo.get_titular())
                    atual.set_cpf(proximo.get_cpf())
                    atual.set_saldo(proximo.get_saldo())

                    # Copia os dados salvos (do nó atual) para o próximo nó
                    proximo.set_numero(numero_atual)
                    proximo.set_titular(titular_atual)
                    proximo.set_cpf(cpf_atual)
                    proximo.set_saldo(saldo_atual)
                    houve_troca = True # Marca que houve uma troca
                atual = atual.get_prox() # Avança para o próximo nó

        return "Lista ordenada com sucesso" # Retorna mensagem de sucesso

    # ...existing code...

    # Aliases para manter compatibilidade com nomes antigos usados no projeto (padrão snake_case vs camelCase)
    def listaVazia(self): # Alias para lista_vazia()
        return self.lista_vazia() # Retorna o resultado de lista_vazia()

    def mostrarLista(self): # Alias para mostrar_lista()
        self.mostrar_lista() # Chama o método mostrar_lista()

    def inserirInicio(self, novo): # Alias para inserir_inicio()
        self.inserir_inicio(novo) # Chama o método inserir_inicio() com o novo nó

    def inserirFim(self, novo): # Alias para inserir_fim()
        self.inserir_fim(novo) # Chama o método inserir_fim() com o novo nó

    def iterarValores(self): # Alias para iterar_valores() com yield
        yield from self.iterar_valores() # Delega para iterar_valores() retornando todos os valores

