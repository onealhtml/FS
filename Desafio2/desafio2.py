# Desafio 2 - Fábrica de Software
# Lorenzo Farias
# Bernardo Soares Nunes
# Pedro Cabral Buchaim

import copy
import random
import sys
import time
import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate

sys.setrecursionlimit(200000)

BIG_O = {
    "Insertion Sort": {"melhor": "O(n)", "medio": "O(n²)", "pior": "O(n²)"},
    "Quick Sort":     {"melhor": "O(n log n)", "medio": "O(n log n)", "pior": "O(n²)"},
    "Merge Sort":     {"melhor": "O(n log n)", "medio": "O(n log n)", "pior": "O(n log n)"},
    "Shell Sort":     {"melhor": "O(n log n)", "medio": "O(n^1.5)", "pior": "O(n²)"},
    "Selection Sort": {"melhor": "O(n²)", "medio": "O(n²)", "pior": "O(n²)"},
    "Radix Sort":     {"melhor": "O(nk)", "medio": "O(nk)", "pior": "O(nk)"},
}

# =====================================================================
# ALGORITMOS DE ORDENAÇÃO
# =====================================================================

def insertion_sort(arr):
    """
    Insertion Sort
    Lógica: Constrói a ordenação deslocando elementos maiores para a direita e inserindo
            o elemento atual na posição correta da parte ordenada.
    Big-O: Melhor O(n), Médio O(n²), Pior O(n²)
    """
    comp = 0
    trocas = 0
    n = len(arr)
    start = time.perf_counter()
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comp += 1          # conta TODA comparação, inclusive a que falha e encerra o while
            if arr[j] > key:
                arr[j + 1] = arr[j]
                trocas += 1
                j -= 1
            else:
                break
        arr[j + 1] = key
        trocas += 1  # Conta a inserção final como movimentação
    end = time.perf_counter()
    return arr, comp, trocas, end - start

def quick_sort_main(arr):
    """
    Quick Sort com pivô Mediana de Três (Median-of-Three)
    Lógica: Escolhe o pivô como a mediana entre o primeiro, meio e último elemento.
            Isso evita o pior caso O(n²) em vetores já ordenados (crescente/decrescente),
            que ocorre com pivô fixo no início ou fim.
    Big-O: Melhor O(n log n), Médio O(n log n), Pior O(n²) (raro com median-of-three)
    """
    comp = [0]
    trocas = [0]

    def median_of_three(a, low, high):
        """
        Ordena a[low], a[mid], a[high] e coloca o pivô (mediana) em a[high-1].
        Garante que a[low] <= pivô <= a[high], melhorando a escolha do pivô.
        """
        mid = (low + high) // 2
        # 3 comparações para ordenar os 3 candidatos
        comp[0] += 3
        if a[low] > a[mid]:
            a[low], a[mid] = a[mid], a[low]
            trocas[0] += 1
        if a[low] > a[high]:
            a[low], a[high] = a[high], a[low]
            trocas[0] += 1
        if a[mid] > a[high]:
            a[mid], a[high] = a[high], a[mid]
            trocas[0] += 1
        # Move o pivô para penúltima posição
        a[mid], a[high - 1] = a[high - 1], a[mid]
        trocas[0] += 1
        return a[high - 1]

    def _quick_sort(a, low, high):
        if high - low < 2:
            return
        pivot = median_of_three(a, low, high)
        i = low
        j = high - 1
        while True:
            i += 1
            while a[i] < pivot:
                comp[0] += 1
                i += 1
            comp[0] += 1
            j -= 1
            while a[j] > pivot:
                comp[0] += 1
                j -= 1
            comp[0] += 1
            if i >= j:
                break
            a[i], a[j] = a[j], a[i]
            trocas[0] += 1
        # Restaura o pivô na posição correta
        a[i], a[high - 1] = a[high - 1], a[i]
        trocas[0] += 1
        _quick_sort(a, low, i - 1)
        _quick_sort(a, i + 1, high)

    start = time.perf_counter()
    if len(arr) > 1:
        _quick_sort(arr, 0, len(arr) - 1)
    end = time.perf_counter()
    return arr, comp[0], trocas[0], end - start

def merge_sort_main(arr):
    """
    Merge Sort
    Lógica: Divide o array na metade até chegar em 1 elemento (que está ordenado),
            depois intercala/une essas partes ordenando os elementos.
    Big-O: Melhor O(n log n), Médio O(n log n), Pior O(n log n)
    """
    comp = [0]
    trocas = [0]

    def _merge_sort(a):
        if len(a) > 1:
            mid = len(a) // 2
            L = a[:mid]
            R = a[mid:]

            _merge_sort(L)
            _merge_sort(R)

            i = j = k = 0

            # Intercalando os elementos
            while i < len(L) and j < len(R):
                comp[0] += 1
                if L[i] < R[j]:
                    a[k] = L[i]
                    i += 1
                else:
                    a[k] = R[j]
                    j += 1
                trocas[0] += 1
                k += 1

            # Copiando o resto de L e R
            while i < len(L):
                a[k] = L[i]
                trocas[0] += 1
                i += 1
                k += 1

            while j < len(R):
                a[k] = R[j]
                trocas[0] += 1
                j += 1
                k += 1

    start = time.perf_counter()
    _merge_sort(arr)
    end = time.perf_counter()
    return arr, comp[0], trocas[0], end - start

def shell_sort(arr):
    """
    Shell Sort
    Lógica: Versão otimizada do Insertion Sort que compara e troca elementos distantes.
            O intervalo de distância (gap) é reduzido gradualmente até ser 1.
    Big-O: Melhor O(n log n), Médio O(n^1.5), Pior O(n²)
    """
    comp = 0
    trocas = 0
    n = len(arr)
    gap = n // 2
    start = time.perf_counter()
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap:
                comp += 1      # conta TODA comparação, inclusive a que encerra o while
                if arr[j - gap] > temp:
                    arr[j] = arr[j - gap]
                    trocas += 1
                    j -= gap
                else:
                    break
            arr[j] = temp
            trocas += 1
        gap //= 2
    end = time.perf_counter()
    return arr, comp, trocas, end - start

def selection_sort(arr):
    """
    Selection Sort
    Lógica: Procura repetidamente pelo menor elemento da parte não ordenada e o move
            para o final da parte ordenada.
    Big-O: Melhor O(n²), Médio O(n²), Pior O(n²)
    """
    comp = 0
    trocas = 0
    n = len(arr)
    start = time.perf_counter()
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comp += 1
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            trocas += 1
    end = time.perf_counter()
    return arr, comp, trocas, end - start

def radix_sort(arr):
    """
    Radix Sort
    Lógica: Ordena cada dígito do número de forma estável começando pelo menos significativo.
    Big-O: Melhor O(nk), Médio O(nk), Pior O(nk)
    Obs: Não conta comparações diretas, foca em acesso ao array.
    """
    comp = 0
    trocas = 0
    start = time.perf_counter()

    if len(arr) == 0:
        return arr, comp, trocas, time.perf_counter() - start

    if len(arr) == 1:
        return arr, comp, trocas, time.perf_counter() - start

    # Adaptação para suportar negativos - encontra mínimo geral
    min_val = min(arr)
    temp_arr = [x - min_val for x in arr] if min_val < 0 else arr

    max1 = max(temp_arr) if len(temp_arr) > 0 else 0
    exp = 1

    def counting_sort(a, e):
        nonlocal trocas
        n = len(a)
        output = [0] * n
        count = [0] * 10
        for i in range(n):
            index = (a[i] // e) % 10
            count[index] += 1
        for i in range(1, 10):
            count[i] += count[i - 1]
        i = n - 1
        while i >= 0:
            index = (a[i] // e) % 10
            output[count[index] - 1] = a[i]
            count[index] -= 1
            trocas += 1
            i -= 1
        for i in range(len(a)):
            a[i] = output[i]
            trocas += 1

    while max1 // exp > 0:
        counting_sort(temp_arr, exp)
        exp *= 10

    if min_val < 0:
        temp_arr = [x + min_val for x in temp_arr]

    end = time.perf_counter()
    return temp_arr, comp, trocas, end - start

# =====================================================================
# GERAÇÃO DE DADOS POR CENÁRIO
# =====================================================================

def gera_vetor(tamanho, cenario):
    """
    Gera as diferentes massas de dados baseadas no tamanho e no cenário esperado.
    Atende aos 8 cenários obrigatórios.
    """
    # Cenários 5 e 6 ignoram o tamanho recebido na hora da geração final se aplicável
    if cenario == "vazia":
        return []
    if cenario == "um_item":
        return [42]

    if cenario == "aleatoria_pequena":
        return [random.randint(-1000, 1000) for _ in range(tamanho)]
    elif cenario == "crescente":
        return list(range(tamanho))
    elif cenario == "decrescente":
        return list(range(tamanho, 0, -1))
    elif cenario == "repetido":
        base = 77
        arr = [base] * int(tamanho * 0.9) # 90% do vetor tem valores iguais
        arr += [random.randint(-1000, 1000) for _ in range(tamanho - len(arr))]
        random.shuffle(arr)
        return arr
    elif cenario == "muitos_repetidos":
        # Apenas 3 valores distintos (conforme exemplo sugerido)
        return [random.choice([10, 20, 30]) for _ in range(tamanho)]
    elif cenario == "longa":
        return [random.randint(-50000, 50000) for _ in range(tamanho)]
    else:
        return [random.randint(-1000, 1000) for _ in range(tamanho)]

# =====================================================================
# MOTOR DE BENCHMARK (GENÉRICO)
# =====================================================================

def testar_algoritmo(func_algo, base_array, nome_algo, repeticoes, cenario=None, tamanho=None):
    runs_comp = []
    runs_troca = []
    runs_tempo = []

    # Cenários aleatórios geram vetor novo a cada repetição → 3 casos estatisticamente distintos
    # Cenários determinísticos (crescente, decrescente etc.) são sempre iguais por natureza
    CENARIOS_ALEATORIOS = {"aleatoria_pequena", "longa", "repetido", "muitos_repetidos"}

    for r in range(repeticoes):
        if cenario in CENARIOS_ALEATORIOS and tamanho is not None:
            arr_copy = gera_vetor(tamanho, cenario)   # novo vetor a cada repetição
        else:
            arr_copy = copy.deepcopy(base_array)       # determinístico: cópia idêntica
        try:
            _, comp, trocas, tempo = func_algo(arr_copy)
            runs_comp.append(comp)
            runs_troca.append(trocas)
            runs_tempo.append(tempo)
        except RecursionError:
            runs_comp.append(0)
            runs_troca.append(0)
            runs_tempo.append(0.0)

    media_comp = sum(runs_comp) // repeticoes if runs_comp else 0
    media_troca = sum(runs_troca) // repeticoes if runs_troca else 0
    media_tempo = sum(runs_tempo) / repeticoes if runs_tempo else 0.0

    return runs_comp, runs_troca, runs_tempo, media_comp, media_troca, media_tempo

def executar_benchmark(tamanho_maximo_otimizacao=False):
    # Fixar a seed para manter a reprodutibilidade
    random.seed(42)

    # As 4 massas de dados
    tamanhos = [1000, 10000, 50000, 100000]

    if tamanho_maximo_otimizacao:
        # Se True na execução interativa para evitar horas de espera, limpa lista
        tamanhos = [100, 500, 1000]

    cenarios = [
        "aleatoria_pequena",
        "crescente",
        "decrescente",
        "repetido",
        "vazia",
        "um_item",
        "muitos_repetidos",
        "longa"
    ]

    algoritmos = {
        "Insertion Sort": insertion_sort,
        "Quick Sort": quick_sort_main,
        "Merge Sort": merge_sort_main,
        "Shell Sort": shell_sort,
        "Selection Sort": selection_sort,
        "Radix Sort": radix_sort
    }

    resultados = []
    repeticoes = 3

    print("Iniciando Benchmark...")
    print("Aviso: Testes N=100.000 para Selection/Insertion Sort podem demorar vários minutos.")

    for cenario in cenarios:
        for tamanho in tamanhos:

            # Arrays vazios ou de 1 item não precisam variar tamanho pra N de verdade,
            # rodam 1 vez.
            if cenario in ["vazia", "um_item"] and tamanho != tamanhos[0]:
                continue

            print(f"- Processando Cenário: {cenario} | Massa: {tamanho}")
            # Gera o vetor 1 unica vez para a massa/cenario
            base_array = gera_vetor(tamanho, cenario)
            massa_real = len(base_array)

            for nome_algo, func_algo in algoritmos.items():
                r_comp, r_trc, r_tmp, m_comp, m_trc, m_tmp = testar_algoritmo(
                    func_algo, base_array, nome_algo, repeticoes,
                    cenario=cenario, tamanho=tamanho
                )

                res = {
                    "Algoritmo": nome_algo,
                    "Cenário": cenario,
                    "Massa": massa_real,
                    "Caso1_comp": r_comp[0],
                    "Caso2_comp": r_comp[1],
                    "Caso3_comp": r_comp[2],
                    "Media_comp": m_comp,
                    "Caso1_trocas": r_trc[0],
                    "Caso2_trocas": r_trc[1],
                    "Caso3_trocas": r_trc[2],
                    "Media_trocas": m_trc,
                    "Caso1_tempo": r_tmp[0],
                    "Caso2_tempo": r_tmp[1],
                    "Caso3_tempo": r_tmp[2],
                    "Media_tempo": m_tmp
                }
                resultados.append(res)

    return resultados

# =====================================================================
# SAÍDAS DO SISTEMA (CSV, GRÁFICOS, TERMINAL)
# =====================================================================

def exportar_csv(resultados):
    """
    Exporta os resultados para um CSV nos moldes requisitados.
    """
    df = pd.DataFrame(resultados)
    df.to_csv("resultados_ordenacao.csv", index=False)
    print("\n[OK] CSV gerado: resultados_ordenacao.csv")
    return df

def gerar_graficos(df):
    """
    Gera:
    - Gráfico de linhas: Tempo de execução por algoritmo x massa
    - Gráfico de barras: Comparações médias por algoritmo x massa
    - Gráfico de barras: Trocas/Movimentações médias por algoritmo x massa
      (Radix Sort anotado como 'Movimentações' por ser não-comparativo)
    """
    import warnings
    warnings.filterwarnings("ignore")
    plt.style.use('ggplot')

    # Paleta de cores fixa por algoritmo — consistente nos 3 gráficos
    CORES = {
        "Insertion Sort": "#E24B4A",  # vermelho
        "Quick Sort":     "#378ADD",  # azul
        "Merge Sort":     "#7F77DD",  # roxo
        "Shell Sort":     "#639922",  # verde
        "Selection Sort": "#EF9F27",  # laranja
        "Radix Sort":     "#888780",  # cinza
    }

    # Remove cenários de 0 ou 1 item para não poluir os eixos
    df_graf = df[df["Massa"] > 1].copy()

    # ── 1. Gráfico de Linhas: Tempo de Execução ──────────────────────────────
    plt.figure(figsize=(10, 6))
    for algo in CORES:
        if algo not in df_graf["Algoritmo"].values:
            continue
        subset = df_graf[df_graf["Algoritmo"] == algo].groupby("Massa")["Media_tempo"].mean().reset_index()
        plt.plot(subset["Massa"], subset["Media_tempo"], marker="o", label=algo, color=CORES[algo])

    plt.title("Tempo de Execução Geral (Crescimento) x Tamanho da Massa")
    plt.xlabel("Massa de Dados (N)")
    plt.ylabel("Tempo (s)")
    plt.yscale("log")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("grafico_tempo_execucao.png", dpi=150)
    plt.close()

    # ── 2. Gráfico de Barras: Comparações ────────────────────────────────────
    pivot_comp = df_graf.pivot_table(
        index="Massa", columns="Algoritmo", values="Media_comp", aggfunc="mean"
    ).reset_index()

    colunas_ord = ["Massa"] + [a for a in CORES if a in pivot_comp.columns]
    pivot_comp = pivot_comp[colunas_ord]
    cores_comp = [CORES[a] for a in colunas_ord if a != "Massa"]

    ax = pivot_comp.plot(x="Massa", kind="bar", figsize=(13, 6), width=0.8, color=cores_comp)
    plt.title("Comparações Média - Agrupada por Algoritmo x Massa")
    plt.xlabel("Tamanho da Massa de Dados (N)")
    plt.ylabel("Qtd (Comparações) - Log Scale")
    plt.yscale("symlog")
    plt.xticks(rotation=0)
    plt.grid(True, axis="y")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0, title="Algoritmo")

    if "Radix Sort" in pivot_comp.columns:
        ax.annotate(
            "* Radix Sort: algoritmo\nnão-comparativo (comp=0)",
            xy=(0.01, 0.97), xycoords="axes fraction",
            fontsize=8, color="gray", va="top",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7)
        )

    plt.tight_layout()
    plt.savefig("grafico_barras_comparacoes.png", dpi=150)
    plt.close()

    # ── 3. Gráfico de Barras: Trocas / Movimentações ─────────────────────────
    pivot_trc = df_graf.pivot_table(
        index="Massa", columns="Algoritmo", values="Media_trocas", aggfunc="mean"
    ).reset_index()

    colunas_ord = ["Massa"] + [a for a in CORES if a in pivot_trc.columns]
    pivot_trc = pivot_trc[colunas_ord]
    cores_trc = [CORES[a] for a in colunas_ord if a != "Massa"]

    ax = pivot_trc.plot(x="Massa", kind="bar", figsize=(13, 6), width=0.8, color=cores_trc)
    plt.title("Trocas/Movimentações Média - Agrupada por Algoritmo x Massa")
    plt.xlabel("Tamanho da Massa de Dados (N)")
    plt.ylabel("Qtd (Trocas/Movimentações) - Log Scale")
    plt.yscale("symlog")
    plt.xticks(rotation=0)
    plt.grid(True, axis="y")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0, title="Algoritmo")

    ax.annotate(
        "* Radix Sort: métrica representa\nmovimentações (2×N×k), não trocas",
        xy=(0.01, 0.97), xycoords="axes fraction",
        fontsize=8, color="gray", va="top",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.7)
    )

    plt.tight_layout()
    plt.savefig("grafico_barras_trocas.png", dpi=150)
    plt.close()

    print("[OK] Gráficos exportados (.png)")

def exibir_relatorio_terminal(df):
    """
    Imprime estrutura formatada na tela usando tabulate ou pandas.
    """
    print("\n" + "="*80)
    print("RELATÓRIO DE RESULTADOS MÉDIOS GERAIS (Agrupamento por Algoritmo e Massa)")
    print("="*80)

    # Faz uma media total ignorando se é ordem crescente/decrescente etc. p/ relatorio
    resumo = df.groupby(["Algoritmo", "Massa"]).agg({
        "Media_comp": "mean",
        "Media_trocas": "mean",
        "Media_tempo": "mean"
    }).reset_index()

    print(tabulate(resumo, headers="keys", tablefmt="pretty", floatfmt=".5f"))

    print("\n" + "="*80)
    print("CLASSIFICAÇÃO BIG O")
    print("="*80)
    for algo, b in BIG_O.items():
        print(f"[{algo}] Melhor: {b['melhor']:<10} | Médio: {b['medio']:<10} | Pior: {b['pior']:<10}")

# =====================================================================
# EXECUÇÃO DO SCRIPT
# =====================================================================

if __name__ == "__main__":
    resultados_finais = executar_benchmark(tamanho_maximo_otimizacao=False) # Usando True para simulação rápida
    # Para o desafio completo N=100.000: mude para "executar_benchmark(tamanho_maximo_otimizacao=False)"

    df_result = exportar_csv(resultados_finais)
    gerar_graficos(df_result)
    exibir_relatorio_terminal(df_result)
    print("\n[!] PROCESSO FINALIZADO. Arquivos criados na raiz da pasta.")