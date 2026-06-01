"""
Moodle Scraper — coleta de atividades pendentes no Moodle da UNISC
==================================================================
Web scraping do painel do Moodle com Playwright.

Login sem precisar apertar ENTER:
  • O script abre o navegador num PERFIL DEDICADO (próprio dele) e vai pro
    painel. Se já houver sessão salva, segue direto.
  • Se precisar logar, você digita usuário/senha (ou faz o SSO) na janela que
    abriu — o Playwright DETECTA SOZINHO quando o login termina (o painel
    logado aparece) e já começa a coletar.
  • A sessão fica salva no perfil dedicado, então nas próximas execuções
    costuma reentrar sem digitar nada.

Setup (uma vez):
    pip install -r requirements.txt
    playwright install firefox     # Chrome/Edge usam a instalação do sistema

Uso:
    python moodle_scraper.py
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import (
    Locator,
    Page,
    TimeoutError as PlaywrightTimeout,
    sync_playwright,
)

# ─────────────────────────────── Configuração ───────────────────────────────
MOODLE_URL = "https://portalvirtual.unisc.br/moodle"

# Deixe None pra usar o 1º navegador instalado; ou fixe "chrome"/"msedge"/"firefox".
NAVEGADOR_FORCADO: str | None = None

# Sinal de "estou logado": só aparece no painel do Moodle, nunca na tela de
# login. O link de logout existe em qualquer tema; os outros são reforço.
SINAL_LOGADO = "a[href*='login/logout.php'], body.userloggedin, [data-region='timeline']"

ARQUIVO_CSV = "atividades_moodle.csv"
ARQUIVO_JSON = "atividades_moodle.json"
PASTA_PERFIS = Path(__file__).resolve().parent  # onde ficam os .perfil_moodle_*

TIMEOUT_PADRAO = 10_000   # ms — operações normais
TIMEOUT_LOGIN = 300_000   # ms — quanto o script espera o usuário logar (5 min)

# Nomes que aparecem soltos no calendário (cabeçalhos de data, não atividades).
NOMES_GENERICOS = {
    "hoje", "amanhã", "ontem",
    "segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo",
}


# ──────────────────────────── Navegador / login ─────────────────────────────
def navegadores_instalados() -> list[dict]:
    """Lista os navegadores disponíveis (ordem de preferência: Chrome, Edge, Firefox)."""
    home = Path.home()
    if sys.platform.startswith("win"):
        local = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))
        roaming = Path(os.environ.get("APPDATA", home / "AppData/Roaming"))
        candidatos = [
            ("chrome", "Chrome", "chromium", local / "Google/Chrome/User Data"),
            ("msedge", "Edge", "chromium", local / "Microsoft/Edge/User Data"),
            ("firefox", "Firefox", "firefox", roaming / "Mozilla/Firefox"),
        ]
    elif sys.platform == "darwin":
        sup = home / "Library/Application Support"
        candidatos = [
            ("chrome", "Chrome", "chromium", sup / "Google/Chrome"),
            ("msedge", "Edge", "chromium", sup / "Microsoft Edge"),
            ("firefox", "Firefox", "firefox", sup / "Firefox"),
        ]
    else:  # linux
        candidatos = [
            ("chrome", "Chrome", "chromium", home / ".config/google-chrome"),
            ("msedge", "Edge", "chromium", home / ".config/microsoft-edge"),
            ("firefox", "Firefox", "firefox", home / ".mozilla/firefox"),
        ]
    return [
        {"canal": c, "nome": n, "motor": m}
        for c, n, m, caminho in candidatos
        if caminho.exists()
    ]


def escolher_navegador() -> dict:
    """Respeita NAVEGADOR_FORCADO; senão usa o primeiro navegador instalado."""
    instalados = navegadores_instalados()
    if not instalados:
        sys.exit("❌ Não encontrei Chrome, Edge nem Firefox neste computador.")
    if NAVEGADOR_FORCADO:
        for nav in instalados:
            if nav["canal"] == NAVEGADOR_FORCADO:
                return nav
        sys.exit(f"❌ NAVEGADOR_FORCADO='{NAVEGADOR_FORCADO}' não está instalado aqui.")
    return instalados[0]


def abrir_contexto(p, nav: dict):
    """Abre o navegador num perfil dedicado (a sessão de login fica salva nele)."""
    perfil = PASTA_PERFIS / f".perfil_moodle_{nav['canal']}"
    print(f"🧭 {nav['nome']} — perfil dedicado ({perfil.name}/)")
    try:
        if nav["motor"] == "chromium":
            return p.chromium.launch_persistent_context(
                user_data_dir=str(perfil),
                channel=nav["canal"],
                headless=False,
                no_viewport=True,
            )
        return p.firefox.launch_persistent_context(
            user_data_dir=str(perfil),
            headless=False,
        )
    except Exception as erro:
        sys.exit(
            f"❌ Não consegui abrir o {nav['nome']}.\n"
            f"   Se for Firefox, rode 'playwright install firefox'.\n"
            f"   Detalhe: {erro}"
        )


def garantir_login(page: Page) -> None:
    """Espera (sem ENTER manual) até o painel logado aparecer.

    Se já houver sessão salva, resolve em segundos. Senão, o usuário loga na
    janela e o Playwright detecta o fim do login sozinho.
    """
    print("⏳ Abrindo o painel...")
    print("   Se aparecer a tela de login, faça o login na janela que abriu —")
    print("   eu detecto sozinho quando você entrar (não precisa apertar nada).")

    inicio = time.monotonic()
    try:
        page.wait_for_selector(SINAL_LOGADO, state="attached", timeout=TIMEOUT_LOGIN)
    except PlaywrightTimeout:
        sys.exit("❌ Não detectei o login em 5 minutos. Rode de novo e faça o login.")

    if time.monotonic() - inicio < 8:
        print("✅ Sessão reaproveitada — sem digitar nada.\n")
    else:
        print("✅ Login detectado! Vamos coletar...\n")


# ────────────────────────────── Coleta de dados ─────────────────────────────
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
            return extrair_itens(itens)

    print("   ⚠️  Timeline vazia, tentando o calendário...")
    return coletar_calendario(page)


def coletar_calendario(page: Page) -> list[dict]:
    """Coleta os próximos eventos do calendário."""
    print("📅 Buscando no calendário...")
    page.goto(f"{MOODLE_URL}/calendar/view.php?view=upcoming", timeout=15_000)
    page.wait_for_timeout(3_000)

    eventos = page.locator("[data-event-id]")
    if eventos.count() == 0:
        eventos = page.locator(".event")

    print(f"   → {eventos.count()} eventos encontrados")
    return extrair_itens(eventos)


def extrair_itens(itens: Locator) -> list[dict]:
    """Extrai nome, prazo, link e tipo de cada item da lista."""
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
                    # link sem parâmetros de ação (&action=...) — chave de dedupe
                    "link_base": re.sub(r"[&?]action=\w+", "", link),
                    "tipo": identificar_tipo(link, nome),
                })
        except Exception:
            continue

    return deduplicar(coletados)


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


def deduplicar(itens: list[dict]) -> list[dict]:
    """Remove duplicatas pelo link, mantendo o nome/prazo mais descritivo.

    O calendário do Moodle renderiza cada evento em dois elementos (um com a
    data, outro com o nome completo). Agrupamos por `link_base` e fundimos.
    """
    por_link: dict[str, dict] = {}
    sem_link: list[dict] = []

    for item in itens:
        chave = item["link_base"]
        if not chave:
            sem_link.append(item)
            continue

        if chave not in por_link:
            por_link[chave] = item
            continue

        atual = por_link[chave]
        # Prefere o nome não-genérico e mais descritivo.
        if eh_nome_generico(atual["nome"]) and not eh_nome_generico(item["nome"]):
            por_link[chave] = item
        elif len(item["nome"]) > len(atual["nome"]) and not eh_nome_generico(item["nome"]):
            por_link[chave] = item
        # Completa o prazo se o registro vencedor não tiver um bom.
        if por_link[chave]["prazo"] in ("Sem prazo", "Ver no Moodle") and item["prazo"] not in ("Sem prazo", "Ver no Moodle"):
            por_link[chave]["prazo"] = item["prazo"]

    vistos: set[str] = set()
    sem_link_unicos = []
    for item in sem_link:
        if item["nome"] not in vistos and not eh_nome_generico(item["nome"]):
            vistos.add(item["nome"])
            sem_link_unicos.append(item)

    resultado = list(por_link.values()) + sem_link_unicos
    for r in resultado:
        r.pop("link_base", None)  # campo auxiliar, fora do output final
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


# ──────────────────────────────── Saída ─────────────────────────────────────
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


# ──────────────────────────────── Main ──────────────────────────────────────
def main() -> None:
    print("🎓 Moodle Scraper — web scraping do painel do Moodle\n")

    nav = escolher_navegador()

    with sync_playwright() as p:
        context = abrir_contexto(p, nav)
        context.set_default_timeout(TIMEOUT_PADRAO)
        page = context.pages[0] if context.pages else context.new_page()

        page.goto(f"{MOODLE_URL}/my/", timeout=30_000)
        garantir_login(page)

        atividades = coletar_timeline(page)
        context.close()

    mostrar(atividades)
    salvar(atividades)


if __name__ == "__main__":
    main()
