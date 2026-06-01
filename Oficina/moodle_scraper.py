"""
Moodle Scraper — coleta de atividades pendentes no Moodle da UNISC.
Web scraping do painel com Playwright (Edge).

Login: o script detecta sozinho quando você entra (sem apertar Enter).
  • Perfil real (USAR_PERFIL_REAL=True): usa seu Edge logado. Precisa fechar o Edge antes.
  • Perfil dedicado (USAR_PERFIL_REAL=False): guarda cookies em sessao_moodle.json (loga 1x).

Setup:
    pip install -r requirements.txt

Run:
    python moodle_scraper.py
"""

from __future__ import annotations

import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import (
    Locator,
    Page,
    TimeoutError as PlaywrightTimeout,
    sync_playwright,
)

# Configuração geral
MOODLE_URL = "https://portalvirtual.unisc.br/moodle"

# Usar seu perfil real do Edge ou um perfil dedicado do script?
USAR_PERFIL_REAL: bool = True

# Se True, faz uma cópia do seu perfil (contorna bloqueio do Chromium 136+)
COPIAR_PERFIL_REAL: bool = False

# Debug: salva itens crus pra ver o que tá vindo do Moodle
SALVAR_BRUTO: bool = False

# Pega dados do calendário ou da timeline?
USAR_CALENDARIO: bool = False

# Sinal de que o usuário tá logado
SINAL_LOGADO = "a[href*='login/logout.php'], body.userloggedin, [data-region='timeline']"


ARQUIVO_CSV = "atividades_moodle.csv"
ARQUIVO_JSON = "atividades_moodle.json"
ARQUIVO_BRUTO = "atividades_moodle_bruto.json"
PASTA_PERFIS = Path(__file__).resolve().parent
SESSAO_FILE = PASTA_PERFIS / "sessao_moodle.json"

TIMEOUT_PADRAO = 10_000  # Operações normais
TIMEOUT_LOGIN = 300_000  # 5 minutos pra usuário logar

# Nomes genéricos que não são atividades
NOMES_GENERICOS = {
    "hoje", "amanhã", "ontem",
    "segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo",
}


# Detectar onde o Edge está instalado
def navegador_edge() -> dict:
    """Descreve o Microsoft Edge no SO atual (e o diretório do seu perfil real)."""
    home = Path.home()
    if sys.platform.startswith("win"):
        user_data = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local")) / "Microsoft/Edge/User Data"
        processo = "msedge.exe"
    elif sys.platform == "darwin":
        user_data = home / "Library/Application Support/Microsoft Edge"
        processo = "Microsoft Edge"
    else:  # Linux
        user_data = home / ".config/microsoft-edge"
        processo = "msedge"

    if not user_data.exists():
        sys.exit(
            f"❌ Não encontrei o perfil do Edge em {user_data}.\n"
            f"   O Microsoft Edge está instalado e foi aberto ao menos uma vez?"
        )
    return {"canal": "msedge", "nome": "Edge", "motor": "chromium", "processo": processo, "dir": user_data}


def listar_perfis_chromium(user_data_dir: Path) -> list[dict]:
    """Lista os perfis do Edge lendo 'Local State'."""
    try:
        estado = json.loads((user_data_dir / "Local State").read_text(encoding="utf-8"))
    except Exception:
        return [{"id": "Default", "nome": "Default", "email": "", "ultimo": True}]

    perfil_cfg = estado.get("profile", {})
    info = perfil_cfg.get("info_cache", {})
    ultimo = perfil_cfg.get("last_used") or "Default"

    perfis = [
        {
            "id": pid,
            "nome": dados.get("name") or pid,
            "email": dados.get("user_name", ""),
            "ultimo": pid == ultimo,
        }
        for pid, dados in info.items()
        if (user_data_dir / pid).exists()
    ]
    if not perfis:
        return [{"id": "Default", "nome": "Default", "email": "", "ultimo": True}]
    # Último usado primeiro, depois ordem alfabética
    perfis.sort(key=lambda x: (not x["ultimo"], x["nome"].lower()))
    return perfis


def escolher_perfil(nav: dict) -> str:
    """Detecta os perfis do navegador e deixa o usuário escolher."""
    perfis = listar_perfis_chromium(nav["dir"])
    if len(perfis) == 1:
        return perfis[0]["id"]

    print(f"\n👤 Perfis encontrados no {nav['nome']}:\n")
    for i, pf in enumerate(perfis, 1):
        email = f" — {pf['email']}" if pf["email"] else ""
        marca = "  (último usado)" if pf["ultimo"] else ""
        print(f"   {i}. {pf['nome']}{email}  [{pf['id']}]{marca}")
    print()

    padrao = next(i for i, pf in enumerate(perfis, 1) if pf["ultimo"])
    while True:
        escolha = input(f"Escolha o perfil [1-{len(perfis)}] (ENTER = {padrao}): ").strip()
        if escolha == "":
            return perfis[padrao - 1]["id"]
        if escolha.isdigit() and 1 <= int(escolha) <= len(perfis):
            return perfis[int(escolha) - 1]["id"]
        print("   ⚠️  Opção inválida, tente de novo.")


def navegador_aberto(processo: str) -> bool:
    """Verifica se o navegador tá rodando."""
    try:
        if sys.platform.startswith("win"):
            saida = subprocess.run(
                ["tasklist", "/FI", f"IMAGENAME eq {processo}"],
                capture_output=True, text=True, check=False,
            )
            return processo.lower() in saida.stdout.lower()
        saida = subprocess.run(
            ["pgrep", "-f", processo], capture_output=True, text=True, check=False,
        )
        return bool(saida.stdout.strip())
    except FileNotFoundError:
        return False


def fechar_navegador(processo: str, nome: str) -> None:
    """Fecha o navegador automaticamente se estiver aberto."""
    if not navegador_aberto(processo):
        return
    print(f"⚠️  O {nome} está aberto — fechando automaticamente para liberar o perfil...")
    try:
        if sys.platform.startswith("win"):
            subprocess.run(["taskkill", "/F", "/IM", processo], capture_output=True, check=False)
        else:
            subprocess.run(["pkill", "-f", processo], capture_output=True, check=False)
    except FileNotFoundError:
        print(f"   ⚠️  Não consegui fechar o {nome} automaticamente. Feche manualmente e rode de novo.")
        sys.exit(1)

    # Aguarda o processo realmente encerrar (até 10 s)
    for _ in range(20):
        time.sleep(0.5)
        if not navegador_aberto(processo):
            print(f"   ✅ {nome} fechado.\n")
            return
    print(f"   ⚠️  O {nome} ainda parece aberto. Feche manualmente e rode de novo.")
    sys.exit(1)


# Pastas que não precisamos copiar (são caches e temporários)
_IGNORAR_NA_COPIA = shutil.ignore_patterns(
    "Cache", "Code Cache", "GPUCache", "ShaderCache", "GraphiteDawnCache",
    "DawnGraphiteCache", "DawnWebGPUCache", "Service Worker", "component_crx_cache",
    "Crashpad", "*.log", "*.tmp",
)


def preparar_copia_perfil(nav: dict, perfil: str) -> Path:
    """Faz uma cópia do perfil pra contornar bloqueio do Chrome (Chromium 136+)."""
    origem = nav["dir"]
    sufixo = perfil.replace(" ", "_")
    destino = PASTA_PERFIS / f".perfil_copia_{nav['canal']}_{sufixo}"

    # Já copiou antes? Reaproveita
    if (destino / perfil).exists():
        print(f"♻️  Reaproveitando o perfil já copiado ({destino.name}/).")
        print("   (apague essa pasta se quiser recopiar do seu perfil real)")
        return destino

    print(f"📁 Copiando seu perfil '{perfil}' pra uma pasta de trabalho (só desta vez)...")
    origem_perfil = origem / perfil
    if not origem_perfil.exists():
        sys.exit(
            f"❌ Não achei a pasta do perfil '{perfil}' em {origem}.\n"
            f"   Abra o {nav['nome']}, confirme em qual perfil você usa o Moodle e tente de novo."
        )
    destino.mkdir(parents=True, exist_ok=True)

    # Copia 'Local State' (tem a chave de cripto e registro de perfis)
    local_state = origem / "Local State"
    if local_state.exists():
        shutil.copy2(local_state, destino / "Local State")

    shutil.copytree(origem_perfil, destino / perfil, ignore=_IGNORAR_NA_COPIA, dirs_exist_ok=True)
    return destino


def abrir_contexto(p, nav: dict):
    """Abre o Edge com seu perfil real ou um perfil dedicado do script."""
    if USAR_PERFIL_REAL:
        perfil = escolher_perfil(nav)
        print(f"🧭 {nav['nome']} — SEU perfil real (perfil: {perfil})")
        fechar_navegador(nav["processo"], nav["nome"])
        # Direto = abre o perfil real; cópia = contorna bloqueio do Chrome 136+
        user_data_dir = preparar_copia_perfil(nav, perfil) if COPIAR_PERFIL_REAL else nav["dir"]
        try:
            return p.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                channel=nav["canal"],
                headless=False,
                args=[f"--profile-directory={perfil}"],
                no_viewport=True,
            )
        except Exception as erro:
            dica = "" if COPIAR_PERFIL_REAL else (
                "\n   Se o Edge recusar a automação no perfil padrão (Chromium 136+),\n"
                "   ligue COPIAR_PERFIL_REAL = True no topo do script."
            )
            sys.exit(
                f"❌ Não consegui abrir o {nav['nome']} com o seu perfil real.\n"
                f"   Confira se ele está TOTALMENTE fechado e tente de novo.{dica}\n"
                f"   Detalhe: {erro}"
            )

    # Perfil dedicado — não precisa fechar o Edge
    perfil_dir = PASTA_PERFIS / f".perfil_moodle_{nav['canal']}"
    print(f"🧭 {nav['nome']} — perfil dedicado ({perfil_dir.name}/)")
    try:
        return p.chromium.launch_persistent_context(
            user_data_dir=str(perfil_dir),
            channel=nav["canal"],
            headless=False,
            no_viewport=True,
        )
    except Exception as erro:
        sys.exit(f"❌ Não consegui abrir o {nav['nome']}.\n   Detalhe: {erro}")


def restaurar_sessao(context) -> None:
    """Reinjeta os cookies salvos pra manter logado entre execuções."""
    if not SESSAO_FILE.exists():
        return
    try:
        dados = json.loads(SESSAO_FILE.read_text(encoding="utf-8"))
        cookies = dados.get("cookies", [])
        if cookies:
            context.add_cookies(cookies)
    except Exception:
        pass


def salvar_sessao(context) -> None:
    """Salva os cookies atuais pra próxima vez."""
    try:
        context.storage_state(path=str(SESSAO_FILE))
    except Exception:
        pass


def clicar_entrar_sala(page: Page) -> None:
    """Na tela de login do EAD, clica em 'Entrar na Sala Virtual' (login unificado)."""
    botao = page.locator("#logar, form[action*='auth/oauth2/login'] button").first
    try:
        botao.wait_for(state="visible", timeout=8_000)
    except PlaywrightTimeout:
        return  # Já logado ou layout diferente
    print("   ↪️  Clicando em 'Entrar na Sala Virtual' (login unificado)...")
    botao.click()


def garantir_login(page: Page) -> None:
    """Espera até o painel logado aparecer (o usuário loga na janela)."""
    print("⏳ Abrindo o painel...")
    print("   Se aparecer a tela de login, faça o login na janela que abriu —")
    print("   eu detecto sozinho quando você entrar (não precisa apertar nada).")
    print("   💡 Marque 'Continuar conectado' / 'Confiar neste dispositivo' pra")
    print("      não repetir o 2FA nas próximas execuções.")

    clicar_entrar_sala(page)

    inicio = time.monotonic()
    try:
        page.wait_for_selector(SINAL_LOGADO, state="attached", timeout=TIMEOUT_LOGIN)
    except PlaywrightTimeout:
        sys.exit("❌ Não detectei o login em 5 minutos. Rode de novo e faça o login.")

    if time.monotonic() - inicio < 8:
        print("✅ Sessão reaproveitada — sem digitar nada.\n")
    else:
        print("✅ Login detectado! Vamos coletar...\n")


# Coleta de dados do Moodle
def coletar_timeline(page: Page) -> list[dict]:
    """Coleta atividades da timeline do painel; cai pro calendário se vazia."""
    print("📋 Buscando atividades na timeline...")
    page.goto(f"{MOODLE_URL}/my/", timeout=15_000)
    page.wait_for_timeout(3_000)

    # Tenta expandir a lista ("ver mais eventos").
    try:
        botao = page.locator("a[data-limit='0'], [data-action='more-events']").first
        if botao.is_visible(timeout=2_000):
            botao.click()
            page.wait_for_timeout(2_000)
    except Exception:
        pass

    for seletor in (
        "[data-region='event-list-item']",
        ".event-list-item",
        "[data-region='timeline'] .list-group-item",
    ):
        itens = page.locator(seletor)
        if itens.count() > 0:
            print(f"   ✅ {itens.count()} itens na timeline")
            return extrair_itens(itens, "timeline")

    print("   ⚠️  Timeline vazia, tentando o calendário...")
    return coletar_calendario(page)


def coletar_calendario(page: Page) -> list[dict]:
    """Coleta os próximos eventos do calendário."""
    print("📅 Buscando no calendário...")
    page.goto(f"{MOODLE_URL}/calendar/view.php?view=upcoming", timeout=15_000)
    page.wait_for_timeout(3_000)

    # Pega os cards de eventos do calendário
    eventos = page.locator("div[data-event-id]")
    if eventos.count() == 0:
        eventos = page.locator(".event")

    print(f"   → {eventos.count()} eventos encontrados")
    return extrair_itens_calendario(eventos)


def extrair_itens(itens: Locator, origem: str = "") -> list[dict]:
    """Extrai nome, prazo, link e tipo de cada item da lista (e deduplica)."""
    coletados: list[dict] = []

    for i in range(itens.count()):
        item = itens.nth(i)
        try:
            nome = _primeiro_texto(item, ["a[href*='mod/']", ".event-name-container a", "h6 a"])
            if not nome:
                nome = item.inner_text(timeout=1_000).split("\n")[0].strip()

            prazo = _primeiro_texto(item, ["small", ".text-muted", "time", ".event-time"]) or "Sem prazo"

            link = ""
            try:
                link = item.locator("a[href*='mod/']").first.get_attribute("href", timeout=500) or ""
            except Exception:
                pass

            if nome and len(nome) > 2:
                coletados.append({
                    "nome": nome,
                    "prazo": prazo,
                    "link": link,
                    "tipo": identificar_tipo(link, nome),
                })
        except Exception:
            continue

    if SALVAR_BRUTO:
        _despejar_bruto(origem, coletados)
    return deduplicar(coletados)


def extrair_itens_calendario(itens: Locator) -> list[dict]:
    """Extrai dados dos cards do calendário."""
    coletados: list[dict] = []

    for i in range(itens.count()):
        item = itens.nth(i)
        try:
            # Nome a partir do data-event-title (mais confiável)
            nome = (item.get_attribute("data-event-title") or "").strip()
            if not nome:
                try:
                    nome = item.locator("h3.name").first.inner_text(timeout=500).strip()
                except Exception:
                    nome = item.inner_text(timeout=1_000).split("\n")[0].strip()

            # Tipo de evento (open, close, due, etc)
            eventtype = (item.get_attribute("data-event-eventtype") or "").strip()

            # Data (segunda linha do texto)
            prazo = "Sem prazo"
            try:
                linhas = item.inner_text(timeout=1_000).split("\n")
                _ignorar = {"Evento da disciplina", "Evento do usuário", "Evento do curso"}
                for linha in linhas[1:]:
                    linha = linha.strip()
                    if linha and linha not in _ignorar:
                        prazo = linha
                        break
            except Exception:
                pass

            # Link (botão no rodapé do card)
            link = ""
            try:
                link = item.locator("a.card-link[href*='mod/']").first.get_attribute("href", timeout=500) or ""
            except Exception:
                pass

            if nome and len(nome) > 2:
                coletados.append({
                    "nome": nome,
                    "prazo": prazo,
                    "link": link,
                    "eventtype": eventtype,
                    "tipo": identificar_tipo(link, nome),
                })
        except Exception:
            continue

    if SALVAR_BRUTO:
        _despejar_bruto("calendario", coletados)
    return deduplicar(coletados)


def _despejar_bruto(origem: str, itens: list[dict]) -> None:
    """Salva os itens crus pra depuração."""
    arquivo = Path(ARQUIVO_BRUTO)
    dados: dict = {}
    if arquivo.exists():
        try:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
        except Exception:
            dados = {}
    dados[origem or "itens"] = itens
    arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   🐛 {len(itens)} itens crus salvos em {ARQUIVO_BRUTO} (origem: {origem or 'itens'})")


def _primeiro_texto(item: Locator, seletores: list[str]) -> str:
    """Retorna o texto do primeiro seletor visível encontrado (ou "")."""
    for sel in seletores:
        try:
            el = item.locator(sel).first
            if el.is_visible(timeout=500):
                return el.inner_text(timeout=1_000).strip()
        except Exception:
            continue
    return ""


def eh_nome_generico(nome: str) -> bool:
    return nome.lower().strip().rstrip(",") in NOMES_GENERICOS


def chave_dedupe(item: dict) -> str:
    """Cria uma chave única para cada evento (ignora variações de URL)."""
    link = item.get("link", "") or ""
    m = re.search(r"/mod/([^/]+)/view\.php\?(?:[^#]*&)?id=(\d+)", link)
    if m:
        return f"mod:{m.group(1).lower()}:{m.group(2)}"
    nome = re.sub(r"\s+", " ", item.get("nome", "")).strip().lower().rstrip(",")
    return f"nome:{nome}"


def _mais_descritivo(atual: dict, novo: dict) -> dict:
    """Escolhe qual dos dois registros é mais útil (funde as informações)."""
    # Prioridade: prazos finais > prazos intermediários > eventos iniciais
    _PRIO = {"due": 0, "close": 1, "expectcompletionon": 2, "open": 99}
    prio_atual = _PRIO.get(atual.get("eventtype", ""), 50)
    prio_novo = _PRIO.get(novo.get("eventtype", ""), 50)

    if prio_novo < prio_atual:
        venc, outro = novo, atual
    elif prio_atual < prio_novo:
        venc, outro = atual, novo
    else:
        # Mesmo nível: prefere nome mais descritivo (não genérico, mais longo)
        venc, outro = atual, novo
        if eh_nome_generico(atual["nome"]) and not eh_nome_generico(novo["nome"]):
            venc, outro = novo, atual
        elif not eh_nome_generico(novo["nome"]) and len(novo["nome"]) > len(atual["nome"]):
            venc, outro = novo, atual

    fundido = dict(venc)
    # Completa com info do outro se tiver faltando
    if fundido["prazo"] in ("Sem prazo", "Ver no Moodle") and outro["prazo"] not in ("Sem prazo", "Ver no Moodle"):
        fundido["prazo"] = outro["prazo"]
    if not fundido.get("link") and outro.get("link"):
        fundido["link"] = outro["link"]
        fundido["tipo"] = outro["tipo"]
    return fundido


def deduplicar(itens: list[dict]) -> list[dict]:
    """Remove duplicatas e cabeçalhos de data."""
    por_chave: dict[str, dict[str, str]] = {}
    for item in itens:
        chave = chave_dedupe(item)
        por_chave[chave] = (
            _mais_descritivo(por_chave[chave], item) if chave in por_chave else item
        )

    # Cabeçalhos soltos de data ("Hoje", "Amanhã"...) não são atividades
    resultado = []
    for it in por_chave.values():
        if not eh_nome_generico(it["nome"]):
            it.pop("eventtype", None)
            resultado.append(it)
    return resultado


def identificar_tipo(link: str, nome: str) -> str:
    """Classifica a atividade pelo padrão da URL do módulo ou pelo nome."""
    link, nome = (link or "").lower(), (nome or "").lower()
    if "assign" in link or "tarefa" in nome or "trabalho" in nome:
        return "📝 Trabalho"
    if "quiz" in link or "prova" in nome or "questionário" in nome:
        return "📝 Questionário"
    if "forum" in link or "fórum" in nome:
        return "💬 Fórum"
    if "glossary" in link or "glossário" in nome:
        return "📖 Glossário"
    if "mod/data" in link:
        return "🗃️ Base de dados"
    if "workshop" in link:
        return "🔧 Workshop"
    if "choice" in link:
        return "✅ Escolha"
    return "📄 Atividade"


# Saída e armazenamento de dados
def mostrar(atividades: list[dict]) -> None:
    print("=" * 60)
    print(f"📊 RESULTADO: {len(atividades)} atividades encontradas!")
    print("=" * 60 + "\n")

    if not atividades:
        print("Nenhuma atividade encontrada.")
        print("💡 Use F12 no Moodle pra conferir os seletores CSS.")
        return

    for i, a in enumerate(atividades, 1):
        print(f"{i}. {a['tipo']}  {a['nome']}")
        print(f"   ⏰ {a['prazo']}")
        if a["link"]:
            print(f"   🔗 {a['link']}")
        print()


def salvar(atividades: list[dict]) -> None:
    if not atividades:
        return
    with open(ARQUIVO_CSV, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=["nome", "tipo", "prazo", "link"])
        escritor.writeheader()
        escritor.writerows(atividades)
    with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
        json.dump(atividades, f, ensure_ascii=False, indent=2)
    print(f"💾 Salvo em {ARQUIVO_CSV} e {ARQUIVO_JSON}")
    print("🎉 Pronto!")


# Main
def main() -> None:
    print("🎓 Moodle Scraper — web scraping do painel do Moodle\n")

    nav = navegador_edge()
    # Perfil real persiste por si só; perfil dedicado usa arquivo de sessão
    usa_sessao_file = not USAR_PERFIL_REAL

    with sync_playwright() as p:
        context = abrir_contexto(p, nav)
        context.set_default_timeout(TIMEOUT_PADRAO)
        if usa_sessao_file:
            restaurar_sessao(context)
        page = context.pages[0] if context.pages else context.new_page()

        page.goto(f"{MOODLE_URL}/my/", timeout=30_000)
        garantir_login(page)

        atividades = coletar_calendario(page) if USAR_CALENDARIO else coletar_timeline(page)
        if usa_sessao_file:
            salvar_sessao(context)
        context.close()

    mostrar(atividades)
    salvar(atividades)


if __name__ == "__main__":
    main()