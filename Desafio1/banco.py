from typing import Optional

from listaencadeada import ListaEncadeada

class Conta:
    def __init__(self, numero: int, titular: str, cpf: str, saldo: float = 0.0):
        self._numero = 0
        self._titular = ""
        self._cpf = ""
        self._saldo = 0.0
        self._prox: Optional["Conta"] = None
        self.set_numero(numero)
        self.set_titular(titular)
        self.set_cpf(cpf)
        self.set_saldo(saldo)

    def get_numero(self):
        return self._numero

    def set_numero(self, valor):
        if int(valor) <= 0:
            raise ValueError("Numero da conta deve ser maior que zero.")
        self._numero = int(valor)

    def get_titular(self):
        return self._titular

    def set_titular(self, valor):
        nome = str(valor).strip()
        if not nome:
            raise ValueError("Titular da conta nao pode ser vazio.")
        self._titular = nome

    def get_cpf(self):
        return self._cpf

    def set_cpf(self, valor):
        cpf = str(valor).strip()
        if not cpf:
            raise ValueError("CPF nao pode ser vazio.")
        if not cpf.isdigit():
            raise ValueError("CPF deve conter apenas digitos.")
        if len(cpf) != 11:
            raise ValueError("CPF deve ter exatamente 11 digitos.")
        if self._verificacao_conta_por_cpf(cpf) is not None:
            raise ValueError("Já existe uma conta com este CPF.")
        self._cpf = cpf

    def get_saldo(self):
        return self._saldo

    def set_saldo(self, valor):
        saldo = float(valor)
        if saldo < 0:
            raise ValueError("Saldo nao pode ser negativo.")
        self._saldo = saldo

    def get_prox(self):
        return self._prox

    def set_prox(self, proxima_conta):
        self._prox = proxima_conta

    def depositar(self, valor):
        valor_float = float(valor)
        if valor_float <= 0:
            return False, "Valor do deposito deve ser maior que zero."
        self._saldo += valor_float
        return True, "Deposito realizado com sucesso."

    def sacar(self, valor):
        valor_float = float(valor)
        if valor_float <= 0:
            return False, "Valor do saque deve ser maior que zero."
        if valor_float > self._saldo:
            return False, "Saldo insuficiente."
        self._saldo -= valor_float
        return True, "Saque realizado com sucesso."

    def __str__(self):
        return (
            f"Conta {self.get_numero()} | Titular: {self.get_titular()} "
            f"| CPF: {self.get_cpf()} | Saldo: R$ {self.get_saldo():.2f}"
        )

class Banco:
    def __init__(self):
        self._contas = ListaEncadeada()
        self._proximo_numero = 1001


    def _gerar_numero_conta(self):
        max_numero = 1000
        for conta in self._contas.iterar_valores():
            if conta.get_numero() > max_numero:
                max_numero = conta.get_numero()
        return max_numero + 1

    def _buscar_conta(self, numero):
        for conta in self._contas.iterar_valores():
            if conta.get_numero() == numero:
                return conta
        return None

    def _verificacao_conta_por_cpf(self, cpf):
        for conta in self._contas.iterar_valores():
            if conta.get_cpf() == cpf:
                return conta
        return None


    def incluir_conta(self, titular, cpf):
        numero_gerado = self._gerar_numero_conta()
        try:
            # Regra da atividade: toda conta sempre inicia com saldo zero.
            nova_conta = Conta(numero=numero_gerado, titular=titular, cpf=cpf, saldo=0.0)
        except (TypeError, ValueError) as erro:
            return False, str(erro)

        self._contas.inserir_fim(nova_conta)
        return True, f"Conta incluida com sucesso. Numero: {numero_gerado}."

    def excluir_conta(self, numero):
        conta = self._buscar_conta(numero)
        if conta is None:
            return False, "Conta nao encontrada."

        if conta.get_saldo() != 0:
            return False, "Nao e possivel excluir conta com saldo diferente de zero."

        self._contas.excluir(conta)

        return True, "Conta excluida com sucesso."

    def consultar_conta(self, numero):
        conta = self._buscar_conta(numero)
        if conta is None:
            return False, "Conta nao encontrada.", None
        return True, "Conta encontrada.", conta

    def depositar(self, numero, valor):
        conta = self._buscar_conta(numero)
        if conta is None:
            return False, "Conta nao encontrada."

        return conta.depositar(valor)

    def sacar(self, numero, valor):
        conta = self._buscar_conta(numero)
        if conta is None:
            return False, "Conta nao encontrada."

        return conta.sacar(valor)

    def gerar_relatorio(self):
        linhas = []
        total_contas = 0
        saldo_total = 0.0

        for conta in self._contas.iterar_valores():
            total_contas += 1
            saldo_total += conta.get_saldo()
            linhas.append(str(conta))

        if total_contas == 0:
            return "Relatorio: nenhuma conta cadastrada."

        cabecalho = "Relatorio de Contas"
        resumo = f"Total de contas: {total_contas} | Saldo total no banco: R$ {saldo_total:.2f}"
        return "\n".join([cabecalho, "-" * len(cabecalho), *linhas, "", resumo])
