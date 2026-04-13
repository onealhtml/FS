import csv
import math
import time
from typing import Optional

from listaencadeada import ListaEncadeada

class Conta: # Classe que representa uma conta bancária
    def __init__(self, numero: int, titular: str, cpf: str, saldo: float = 0.0, ativa: bool = True):
        self._numero = 0
        self._titular = ""
        self._cpf = ""
        self._saldo = 0.0
        self._ativa = True
        self._prox: Optional["Conta"] = None # Próximo nó para encadeamento na hash
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

    def depositar(self, valor): # Adiciona saldo à conta
        valor_float = float(valor)
        if valor_float <= 0:
            return False, "Valor do depósito deve ser maior que zero."
        self._saldo += valor_float
        return True, "Depósito realizado com sucesso."

    def sacar(self, valor): # Remove saldo da conta se houver saldo suficiente
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

class Banco: # Implementa banco com tabela hash dinâmica para armazenar contas
    HASH_ESTRATEGIAS = ("divisao", "fnv1a", "mod31")
    MOD31_BASE = 31

    def __init__(self, table_size: int = 101, hash_strategy: str = "divisao", max_load_factor: float = 0.75):
        if int(table_size) <= 0:
            raise ValueError("table_size deve ser maior que zero.")
        if float(max_load_factor) <= 0:
            raise ValueError("max_load_factor deve ser maior que zero.")
        self._table_size = int(table_size)
        estrategia = str(hash_strategy).strip().lower()
        if estrategia not in self.HASH_ESTRATEGIAS:
            raise ValueError("hash_strategy deve ser 'divisao', 'fnv1a' ou 'mod31'.")
        self._hash_strategy = estrategia
        self._max_load_factor = float(max_load_factor)
        self._buckets = [ListaEncadeada() for _ in range(self._table_size)]
        self._cpf_index = {} # Índice para busca rápida por CPF
        self._qtd_contas = 0
        self._ultimo_numero = 1000

    def _gerar_numero_conta(self): # Gera próximo número de conta sequencial
        self._ultimo_numero += 1
        return self._ultimo_numero

    @staticmethod
    def fnv1a(key: str, table_size: int) -> int: # Algoritmo FNV-1a para hash
        FNV_OFFSET = 2166136261
        FNV_PRIME = 16777619

        hash_value = FNV_OFFSET
        for char in key.encode("utf-8"):
            hash_value ^= char
            hash_value *= FNV_PRIME
            hash_value &= 0xFFFFFFFF

        return hash_value % table_size

    def _indice_bucket(self, numero: int) -> int: # Calcula índice do bucket usando estratégia configurada
        if self._hash_strategy == "divisao":
            return int(numero) % self._table_size
        if self._hash_strategy == "mod31":
            # Estrategia proposital para testes de colisao com base fixa.
            return (int(numero) % self.MOD31_BASE)
        return self.fnv1a(str(numero), self._table_size)

    def _iterar_contas(self): # Itera sobre todas as contas em todos buckets
        for bucket in self._buckets:
            for conta in bucket.iterar_valores():
                yield conta

    def _fator_carga(self) -> float: # Calcula razão entre contas e tamanho da tabela
        return self._qtd_contas / self._table_size

    def _precisa_redimensionar(self) -> bool: # Verifica se fator de carga ultrapassou máximo
        return self._fator_carga() > self._max_load_factor

    def _proximo_tamanho_tabela(self) -> int: # Calcula novo tamanho (dobro + 1)
        return (self._table_size * 2) + 1

    def _redimensionar_tabela(self, novo_tamanho: int): # Redimensiona tabela reinsertando contas
        contas = list(self._iterar_contas())
        self._table_size = int(novo_tamanho)
        self._buckets = [ListaEncadeada() for _ in range(self._table_size)]
        self._cpf_index = {}
        self._qtd_contas = 0
        for conta in contas:
            self._inserir_conta_obj(conta, verificar_redimensionamento=False)

    def _inserir_conta_obj(self, conta: Conta, verificar_redimensionamento: bool = True): # Insere conta na hash
        indice = self._indice_bucket(conta.get_numero())
        self._buckets[indice].inserir_inicio(conta)
        self._cpf_index[conta.get_cpf()] = conta
        self._qtd_contas += 1
        if conta.get_numero() > self._ultimo_numero:
            self._ultimo_numero = conta.get_numero()
        if verificar_redimensionamento and self._precisa_redimensionar():
            self._redimensionar_tabela(self._proximo_tamanho_tabela())

    def _buscar_conta(self, numero): # Busca conta pelo número
        numero_int = int(numero)
        indice = self._indice_bucket(numero_int)
        for conta in self._buckets[indice].iterar_valores():
            if conta.get_numero() == numero_int:
                return conta
        return None

    def _verificacao_conta_por_cpf(self, cpf): # Busca conta pelo CPF (O(1))
        cpf_limpo = "".join(ch for ch in str(cpf) if ch.isdigit())
        return self._cpf_index.get(cpf_limpo)

    def incluir_conta(self, titular, cpf): # Cria nova conta e a insere
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

    def excluir_conta(self, numero): # Remove conta se saldo for zero
        conta = self._buscar_conta(numero)
        if conta is None:
            return False, "Conta não encontrada."

        if conta.get_saldo() != 0:
            return False, "Não é possível excluir conta com saldo diferente de zero."

        indice = self._indice_bucket(conta.get_numero())
        removida = self._buckets[indice].excluir(conta)
        if not removida:
            return False, "Falha ao excluir conta."

        self._qtd_contas -= 1
        self._cpf_index.pop(conta.get_cpf(), None)
        return True, "Conta excluída com sucesso."

    def consultar_conta(self, numero): # Retorna dados da conta
        conta = self._buscar_conta(numero)
        if conta is None:
            return False, "Conta não encontrada.", None
        return True, "Conta encontrada.", conta

    def depositar(self, numero, valor): # Realiza depósito em conta
        conta = self._buscar_conta(numero)
        if conta is None:
            return False, "Conta não encontrada."
        if not conta.get_ativa():
            return False, "Conta inativa."

        return conta.depositar(valor)

    def sacar(self, numero, valor): # Realiza saque de conta
        conta = self._buscar_conta(numero)
        if conta is None:
            return False, "Conta não encontrada."
        if not conta.get_ativa():
            return False, "Conta inativa."

        return conta.sacar(valor)

    def gerar_relatorio(self): # Gera relatório com todas as contas e saldos
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

    def debug_buckets(self, mostrar_vazios: bool = False): # Alias para listar_buckets
        return self.listar_buckets(mostrar_vazios=mostrar_vazios)

    def listar_buckets(self, mostrar_vazios: bool = False): # Exibe distribuição de contas nos buckets
        linhas = []

        for indice, bucket in enumerate(self._buckets):
            numeros = [str(conta.get_numero()) for conta in bucket.iterar_valores()]

            if not numeros and not mostrar_vazios:
                continue

            if numeros:
                linhas.append(
                    f"Bucket {indice:03d} ({len(numeros)}): " + " -> ".join(numeros) + " -> None"
                )
            else:
                linhas.append(f"Bucket {indice:03d}: vazio")

        if not linhas:
            return "Nenhuma conta cadastrada na tabela hash."

        return "\n".join(linhas)

    def obter_metricas_hash(self): # Calcula métricas estatísticas da hash
        tamanhos_buckets = [sum(1 for _ in bucket.iterar_valores()) for bucket in self._buckets]

        total_contas = self._qtd_contas
        buckets_ocupados = sum(1 for tamanho in tamanhos_buckets if tamanho > 0)
        buckets_vazios = self._table_size - buckets_ocupados
        colisoes = sum(max(0, tamanho - 1) for tamanho in tamanhos_buckets)
        maior_cadeia = max(tamanhos_buckets, default=0)
        fator_carga = self._fator_carga()
        media_por_bucket = total_contas / self._table_size
        media_bucket_ocupado = (total_contas / buckets_ocupados) if buckets_ocupados else 0.0
        variancia = sum((tamanho - media_por_bucket) ** 2 for tamanho in tamanhos_buckets) / self._table_size
        desvio_padrao = math.sqrt(variancia)

        return {
            "estrategia": self._hash_strategy,
            "table_size": self._table_size,
            "total_contas": total_contas,
            "buckets_ocupados": buckets_ocupados,
            "buckets_vazios": buckets_vazios,
            "fator_carga": fator_carga,
            "colisoes": colisoes,
            "maior_cadeia": maior_cadeia,
            "media_bucket_ocupado": media_bucket_ocupado,
            "desvio_padrao_tamanho_bucket": desvio_padrao,
            "max_load_factor": self._max_load_factor,
        }

    def estatisticas_hash(self): # Retorna estatísticas simplificadas
        m = self.obter_metricas_hash()
        return {
            "table_size": m["table_size"],
            "total_contas": m["total_contas"],
            "buckets_usados": m["buckets_ocupados"],
            "buckets_vazios": m["buckets_vazios"],
            "fator_carga": m["fator_carga"],
            "media_cadeia_bucket_usado": m["media_bucket_ocupado"],
            "maior_cadeia": m["maior_cadeia"],
            "max_load_factor": m["max_load_factor"],
        }

    def relatorio_metricas_hash(self): # Exibe relatório formatado das métricas
        m = self.obter_metricas_hash()
        return "\n".join(
            [
                "Métricas da Tabela Hash",
                "-" * 23,
                f"Estratégia de hash: {m['estrategia']}",
                f"Tamanho da tabela: {m['table_size']}",
                f"Total de contas: {m['total_contas']}",
                f"Buckets ocupados: {m['buckets_ocupados']} | Buckets vazios: {m['buckets_vazios']}",
                f"Fator de carga: {m['fator_carga']:.4f}",
                f"Colisões (inserções em bucket já ocupado): {m['colisoes']}",
                f"Maior cadeia: {m['maior_cadeia']}",
                f"Média por bucket ocupado: {m['media_bucket_ocupado']:.4f}",
                f"Desvio padrão do tamanho dos buckets: {m['desvio_padrao_tamanho_bucket']:.4f}",
            ]
        )

    def comparar_estrategias_hash(self, repeticoes_busca: int = 5): # Testa performance das 3 estratégias
        repeticoes = max(1, int(repeticoes_busca))
        snapshot = [
            (
                conta.get_numero(),
                conta.get_titular(),
                conta.get_cpf(),
                conta.get_saldo(),
                conta.get_ativa(),
            )
            for conta in self._iterar_contas()
        ]
        numeros_existentes = [dados[0] for dados in snapshot]
        numeros_inexistentes = [numero + 10_000_000 for numero in numeros_existentes] or [9_999_999]

        comparativo = {}
        for estrategia in self.HASH_ESTRATEGIAS:
            banco_teste = Banco(table_size=self._table_size, hash_strategy=estrategia, max_load_factor=self._max_load_factor)

            inicio = time.perf_counter_ns()
            for numero, titular, cpf, saldo, ativa in snapshot:
                conta = Conta(numero=numero, titular=titular, cpf=cpf, saldo=saldo, ativa=ativa)
                banco_teste._inserir_conta_obj(conta)
            tempo_insercao_ms = (time.perf_counter_ns() - inicio) / 1_000_000

            inicio = time.perf_counter_ns()
            for _ in range(repeticoes):
                for numero in numeros_existentes:
                    banco_teste._buscar_conta(numero)
            tempo_busca_existente_ms = (time.perf_counter_ns() - inicio) / 1_000_000

            inicio = time.perf_counter_ns()
            for _ in range(repeticoes):
                for numero in numeros_inexistentes:
                    banco_teste._buscar_conta(numero)
            tempo_busca_inexistente_ms = (time.perf_counter_ns() - inicio) / 1_000_000

            total_buscas_existentes = max(1, repeticoes * len(numeros_existentes))
            total_buscas_inexistentes = max(1, repeticoes * len(numeros_inexistentes))

            metricas = banco_teste.obter_metricas_hash()
            metricas.update(
                {
                    "tempo_insercao_ms": tempo_insercao_ms,
                    "tempo_total_busca_existente_ms": tempo_busca_existente_ms,
                    "tempo_total_busca_inexistente_ms": tempo_busca_inexistente_ms,
                    "media_busca_existente_us": (tempo_busca_existente_ms * 1000) / total_buscas_existentes,
                    "media_busca_inexistente_us": (tempo_busca_inexistente_ms * 1000) / total_buscas_inexistentes,
                    "throughput_busca_existente_ops_s": total_buscas_existentes / max(0.000001, tempo_busca_existente_ms / 1000),
                    "throughput_busca_inexistente_ops_s": total_buscas_inexistentes
                    / max(0.000001, tempo_busca_inexistente_ms / 1000),
                }
            )
            comparativo[estrategia] = metricas

        return {
            "table_size": self._table_size,
            "total_contas": len(snapshot),
            "repeticoes_busca": repeticoes,
            "resultados": comparativo,
        }

    def relatorio_comparativo_hash(self, repeticoes_busca: int = 5): # Exibe comparativo formatado
        dados = self.comparar_estrategias_hash(repeticoes_busca=repeticoes_busca)
        estrategias = list(self.HASH_ESTRATEGIAS)
        resultados = dados["resultados"]

        def _linha_metricas(rotulo: str, chave: str, formato: str):
            partes = [f"{estrategia}={format(resultados[estrategia][chave], formato)}" for estrategia in estrategias]
            return f"- {rotulo}: " + " | ".join(partes)

        linhas = [
            "Comparativo de Hash",
            "-" * 19,
            f"Total de contas avaliadas: {dados['total_contas']} | Tamanho tabela: {dados['table_size']} | Repetições de busca: {dados['repeticoes_busca']}",
            "Estratégias: " + ", ".join(estrategias),
            "",
            "Distribuição",
            _linha_metricas("Fator de carga", "fator_carga", ".4f"),
            _linha_metricas("Buckets ocupados", "buckets_ocupados", "d"),
            _linha_metricas("Buckets vazios", "buckets_vazios", "d"),
            _linha_metricas("Colisões", "colisoes", "d"),
            _linha_metricas("Maior cadeia", "maior_cadeia", "d"),
            _linha_metricas("Média bucket ocupado", "media_bucket_ocupado", ".4f"),
            _linha_metricas("Desvio padrão tamanhos", "desvio_padrao_tamanho_bucket", ".4f"),
            "",
            "Tempo",
            _linha_metricas("Inserção total (ms)", "tempo_insercao_ms", ".4f"),
            _linha_metricas("Busca existente média (us)", "media_busca_existente_us", ".4f"),
            _linha_metricas("Busca inexistente média (us)", "media_busca_inexistente_us", ".4f"),
            _linha_metricas("Throughput busca existente (ops/s)", "throughput_busca_existente_ops_s", ".2f"),
            _linha_metricas("Throughput busca inexistente (ops/s)", "throughput_busca_inexistente_ops_s", ".2f"),
        ]
        return "\n".join(linhas)

    @staticmethod
    def _parse_bool_ativa(valor): # Converte string para booleano (ativo/inativo)
        texto = str(valor).strip().lower()
        if texto in {"true", "1", "sim", "s", "ativo", "ativa"}:
            return True
        if texto in {"false", "0", "nao", "não", "n", "inativo", "inativa"}:
            return False
        raise ValueError("Campo 'ativa' deve ser True/False (ou equivalente).")

    def importar_contas_csv(self, caminho_csv: str, delimitador: str = ","): # Lê contas de arquivo CSV
        inseridas = 0
        erros = []

        # Evita busca linear por linha do CSV: valida duplicidade em O(1) com set.
        numeros_existentes = set()
        cpfs_existentes = set(self._cpf_index.keys())
        for conta_existente in self._iterar_contas():
            numeros_existentes.add(conta_existente.get_numero())

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

