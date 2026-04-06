import csv
from typing import Optional

from listaencadeada import ListaEncadeada

class Conta:
    def __init__(self, numero: int, titular: str, cpf: str, saldo: float = 0.0, ativa: bool = True):
        self._numero = 0
        self._titular = ""
        self._cpf = ""
        self._saldo = 0.0
        self._ativa = True
        self._prox: Optional["Conta"] = None
        self.set_numero(numero)
        self.set_titular(titular)
        self.set_cpf(cpf)
        self.set_saldo(saldo)
        self.set_ativa(ativa)

    def get_numero(self):
        return self._numero

    def set_numero(self, valor):
        if int(valor) <= 0:
            raise ValueError("Número da conta deve ser maior que zero.")
        self._numero = int(valor)

    def get_titular(self):
        return self._titular

    def set_titular(self, valor):
        nome = str(valor).strip()
        if not nome:
            raise ValueError("Titular da conta não pode ser vazio.")
        self._titular = nome

    def get_cpf(self):
        return self._cpf

    def set_cpf(self, valor):
        cpf = "".join(ch for ch in str(valor) if ch.isdigit())
        if not cpf:
            raise ValueError("CPF não pode ser vazio.")
        if len(cpf) != 11:
            raise ValueError("CPF deve ter exatamente 11 digitos.")
        self._cpf = cpf

    def get_saldo(self):
        return self._saldo

    def set_saldo(self, valor):
        saldo = float(valor)
        if saldo < 0:
            raise ValueError("Saldo não pode ser negativo.")
        self._saldo = saldo

    def get_ativa(self):
        return self._ativa

    def set_ativa(self, valor):
        self._ativa = bool(valor)

    def get_prox(self):
        return self._prox

    def set_prox(self, proxima_conta):
        self._prox = proxima_conta

    def depositar(self, valor):
        valor_float = float(valor)
        if valor_float <= 0:
            return False, "Valor do depósito deve ser maior que zero."
        self._saldo += valor_float
        return True, "Depósito realizado com sucesso."

    def sacar(self, valor):
        valor_float = float(valor)
        if valor_float <= 0:
            return False, "Valor do saque deve ser maior que zero."
        if valor_float > self._saldo:
            return False, "Saldo insuficiente."
        self._saldo -= valor_float
        return True, "Saque realizado com sucesso."

    def __str__(self):
        status = "Ativa" if self.get_ativa() else "Inativa"
        return (
            f"Conta {self.get_numero()} | Titular: {self.get_titular()} "
            f"| CPF: {self.get_cpf()} | Saldo: R$ {self.get_saldo():.2f} | Status: {status}"
        )

class Banco:
    def __init__(self, table_size: int = 101):
        if int(table_size) <= 0:
            raise ValueError("table_size deve ser maior que zero.")
        self._table_size = int(table_size)
        self._buckets = [ListaEncadeada() for _ in range(self._table_size)]
        self._ultimo_numero = 1000

    def _gerar_numero_conta(self):
        self._ultimo_numero += 1
        return self._ultimo_numero

    @staticmethod
    def fnv1a(key: str, table_size: int) -> int:
        FNV_OFFSET = 2166136261
        FNV_PRIME = 16777619

        hash_value = FNV_OFFSET
        for char in key.encode("utf-8"):
            hash_value ^= char
            hash_value *= FNV_PRIME
            hash_value &= 0xFFFFFFFF

        return hash_value % table_size

    def _indice_bucket(self, numero: int) -> int:
        return self.fnv1a(str(numero), self._table_size)

    def _iterar_contas(self):
        for bucket in self._buckets:
            for conta in bucket.iterar_valores():
                yield conta

    def _inserir_conta_obj(self, conta: Conta):
        indice = self._indice_bucket(conta.get_numero())
        self._buckets[indice].inserir_fim(conta)
        if conta.get_numero() > self._ultimo_numero:
            self._ultimo_numero = conta.get_numero()

    def _buscar_conta(self, numero):
        numero_int = int(numero)
        indice = self._indice_bucket(numero_int)
        for conta in self._buckets[indice].iterar_valores():
            if conta.get_numero() == numero_int:
                return conta
        return None

    def _verificacao_conta_por_cpf(self, cpf):
        cpf_limpo = "".join(ch for ch in str(cpf) if ch.isdigit())
        for conta in self._iterar_contas():
            if conta.get_cpf() == cpf_limpo:
                return conta
        return None


    def incluir_conta(self, titular, cpf):
        if self._verificacao_conta_por_cpf(cpf) is not None:
            return False, "Já existe uma conta com este CPF."

        numero_gerado = self._gerar_numero_conta()
        try:
            # Regra da atividade: toda conta sempre inicia com saldo zero.
            nova_conta = Conta(numero=numero_gerado, titular=titular, cpf=cpf, saldo=0.0, ativa=True)
        except (TypeError, ValueError) as erro:
            return False, str(erro)

        self._inserir_conta_obj(nova_conta)
        return True, f"Conta incluída com sucesso. Número: {numero_gerado}."

    def excluir_conta(self, numero):
        conta = self._buscar_conta(numero)
        if conta is None:
            return False, "Conta não encontrada."

        if conta.get_saldo() != 0:
            return False, "Não é possível excluir conta com saldo diferente de zero."

        indice = self._indice_bucket(conta.get_numero())
        self._buckets[indice].excluir(conta)

        return True, "Conta excluída com sucesso."

    def consultar_conta(self, numero):
        conta = self._buscar_conta(numero)
        if conta is None:
            return False, "Conta não encontrada.", None
        return True, "Conta encontrada.", conta

    def depositar(self, numero, valor):
        conta = self._buscar_conta(numero)
        if conta is None:
            return False, "Conta não encontrada."
        if not conta.get_ativa():
            return False, "Conta inativa."

        return conta.depositar(valor)

    def sacar(self, numero, valor):
        conta = self._buscar_conta(numero)
        if conta is None:
            return False, "Conta não encontrada."
        if not conta.get_ativa():
            return False, "Conta inativa."

        return conta.sacar(valor)

    def gerar_relatorio(self):
        linhas = []
        total_contas = 0
        saldo_total = 0.0

        for conta in self._iterar_contas():
            total_contas += 1
            saldo_total += conta.get_saldo()
            linhas.append(str(conta))

        if total_contas == 0:
            return "Relatório: nenhuma conta cadastrada."

        cabecalho = "Relatório de Contas"
        resumo = f"Total de contas: {total_contas} | Saldo total no banco: R$ {saldo_total:.2f}"
        return "\n".join([cabecalho, "-" * len(cabecalho), *linhas, "", resumo])

    def debug_buckets(self, mostrar_vazios: bool = False):
        linhas = []

        for indice, bucket in enumerate(self._buckets):
            numeros = [str(conta.get_numero()) for conta in bucket.iterar_valores()]

            if not numeros and not mostrar_vazios:
                continue

            if numeros:
                linhas.append(f"Bucket {indice:03d}: " + " -> ".join(numeros) + " -> None")
            else:
                linhas.append(f"Bucket {indice:03d}: vazio")

        if not linhas:
            return "Nenhuma conta cadastrada na tabela hash."

        return "\n".join(linhas)

    @staticmethod
    def _parse_bool_ativa(valor):
        texto = str(valor).strip().lower()
        if texto in {"true", "1", "sim", "s", "ativo", "ativa"}:
            return True
        if texto in {"false", "0", "nao", "não", "n", "inativo", "inativa"}:
            return False
        raise ValueError("Campo 'ativa' deve ser True/False (ou equivalente).")

    def importar_contas_csv(self, caminho_csv: str, delimitador: str = ","):
        inseridas = 0
        erros = []

        # Evita busca linear por linha do CSV: valida duplicidade em O(1) com set.
        numeros_existentes = set()
        cpfs_existentes = set()
        for conta_existente in self._iterar_contas():
            numeros_existentes.add(conta_existente.get_numero())
            cpfs_existentes.add(conta_existente.get_cpf())

        try:
            with open(caminho_csv, newline="", encoding="utf-8") as arquivo:
                leitor = csv.reader(arquivo, delimiter=delimitador)
                for indice_linha, linha in enumerate(leitor, start=1):
                    if not linha or not any(campo.strip() for campo in linha):
                        continue

                    if len(linha) != 5:
                        erros.append(f"Linha {indice_linha}: esperado 5 campos.")
                        continue

                    numero_txt, titular, cpf, saldo_txt, ativa_txt = [campo.strip() for campo in linha]

                    try:
                        numero = int(numero_txt)
                        if numero <= 0:
                            raise ValueError("numero inválido")
                        saldo = float(saldo_txt)
                        ativa = self._parse_bool_ativa(ativa_txt)

                        cpf_limpo = "".join(ch for ch in str(cpf) if ch.isdigit())
                        if not cpf_limpo:
                            raise ValueError("CPF não pode ser vazio.")
                        if len(cpf_limpo) != 11:
                            raise ValueError("CPF deve ter exatamente 11 digitos.")
                    except (TypeError, ValueError) as erro:
                        erros.append(f"Linha {indice_linha}: {erro}")
                        continue

                    if numero in numeros_existentes:
                        erros.append(f"Linha {indice_linha}: número de conta duplicado ({numero}).")
                        continue

                    if cpf_limpo in cpfs_existentes:
                        erros.append(f"Linha {indice_linha}: CPF duplicado ({cpf_limpo}).")
                        continue

                    try:
                        conta = Conta(numero=numero, titular=titular, cpf=cpf_limpo, saldo=saldo, ativa=ativa)
                    except (TypeError, ValueError) as erro:
                        erros.append(f"Linha {indice_linha}: {erro}")
                        continue

                    self._inserir_conta_obj(conta)
                    numeros_existentes.add(conta.get_numero())
                    cpfs_existentes.add(conta.get_cpf())
                    inseridas += 1
        except FileNotFoundError:
            return False, "Arquivo CSV não encontrado."
        except OSError as erro:
            return False, f"Erro ao ler arquivo CSV: {erro}"

        if erros:
            return False, (
                f"Importação concluída com {inseridas} conta(s) inserida(s) e {len(erros)} erro(s). "
                + "\n"
                + "\n".join(erros)
            )

        return True, f"Importação concluída com sucesso. {inseridas} conta(s) inserida(s)."

