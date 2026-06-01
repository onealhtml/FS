"""
Moodle Scraper — coleta de atividades pendentes no Moodle da UNISC
==================================================================
Web scraping do painel do Moodle com Playwright.

Login (sem apertar ENTER — o Playwright detecta sozinho quando você entra):
  • Padrão (USAR_PERFIL_REAL=True): usa o SEU perfil real do Chrome/Edge, onde
    você já está logado. Se o seu login for persistente (continua logado ao
    reabrir o navegador), aqui também entra direto. Exige o navegador FECHADO
    antes de rodar (o navegador trava o perfil enquanto aberto).
  • Alternativa (USAR_PERFIL_REAL=False): usa um perfil dedicado próprio do
    script e guarda os cookies em sessao_moodle.json — você loga 1x e as
    próximas execuções reentram sozinhas. Não precisa fechar o navegador.

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

# ─────────────────────────────── Configuração ───────────────────────────────
MOODLE_URL = "https://portalvirtual.unisc.br/moodle"

# Deixe None pra usar o 1º navegador instalado; ou fixe "chrome"/"msedge"/"firefox".
NAVEGADOR_FORCADO: str | None = None

# True  = usa o SEU perfil real do Chrome/Edge (precisa FECHAR o navegador antes).
#         Zero login só se o seu login for persistente (continua logado ao reabrir).
# False = usa um perfil dedicado + sessao_moodle.json (loga 1x, depois reusa).
# (Firefox sempre usa perfil dedicado — o Playwright roda o Firefox dele.)
USAR_PERFIL_REAL: bool = True

# Sinal de "estou logado": só aparece no painel do Moodle, nunca na tela de
# login. O link de logout existe em qualquer tema; os outros são reforço.
SINAL_LOGADO = "a[href*='login/logout.php'], body.userloggedin, [data-region='timeline']"

ARQUIVO_CSV = "atividades_moodle.csv"
ARQUIVO_JSON = "atividades_moodle.json"
PASTA_PERFIS = Path(__file__).resolve().parent  # onde ficam os .perfil_moodle_*
# Cookies salvos entre execuções (inclui os de sessão, que o perfil em disco
# descarta ao fechar). É isso que evita relogar/refazer 2FA toda vez.
SESSAO_FILE = PASTA_PERFIS / "sessao_moodle.json"

TIMEOUT_PADRAO = 10_000   # ms — operações normais
TIMEOUT_LOGIN = 300_000   # ms — quanto o script espera o usuário logar (5 min)

# Nomes que aparecem soltos no calendário (cabeçalhos de data, não atividades).
NOMES_GENERICOS = {
    "hoje", "amanhã", "ontem",
    "segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo",
}


# ──────────────────────────── Navegador / login ─────────────────────────────
def navegadores_instalados() -> list[dict]:
    """Lista os navegadores disponíveis (ordem de preferência: Chrome, Edge, Firefox).

    Cada item traz: canal, nome, motor, processo (p/ checar se está aberto) e
    `dir` (diretório de perfil real do usuário).
    """
    home = Path.home()
    if sys.platform.startswith("win"):
        local = Path(os.environ.get("LOCALAPPDATA", home / "AppData/Local"))
        roaming = Path(os.environ.get("APPDATA", home / "AppData/Roaming"))
        candidatos = [
            ("chrome", "Chrome", "chromium", "chrome.exe", local / "Google/Chrome/User Data"),
            ("msedge", "Edge", "chromium", "msedge.exe", local / "Microsoft/Edge/User Data"),
            ("firefox", "Firefox", "firefox", "firefox.exe", roaming / "Mozilla/Firefox"),
        ]
    elif sys.platform == "darwin":
        sup = home / "Library/Application Support"
        candidatos = [
            ("chrome", "Chrome", "chromium", "Google Chrome", sup / "Google/Chrome"),
            ("msedge", "Edge", "chromium", "Microsoft Edge", sup / "Microsoft Edge"),
            ("firefox", "Firefox", "firefox", "firefox", sup / "Firefox"),
        ]
    else:  # linux
        candidatos = [
            ("chrome", "Chrome", "chromium", "chrome", home / ".config/google-chrome"),
            ("msedge", "Edge", "chromium", "msedge", home / ".config/microsoft-edge"),
            ("firefox", "Firefox", "firefox", "firefox", home / ".mozilla/firefox"),
        ]
    return [
        {"canal": c, "nome": n, "motor": m, "processo": proc, "dir": caminho}
        for c, n, m, proc, caminho in candidatos
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


def perfil_ativo_chromium(user_data_dir: Path) -> str:
    """Descobre o perfil em uso lendo o 'Local State' do Chrome/Edge (cai pra Default)."""
    try:
        estado = json.loads((user_data_dir / "Local State").read_text(encoding="utf-8"))
        return estado.get("profile", {}).get("last_used") or "Default"
    except Exception:
        return "Default"


def navegador_aberto(processo: str) -> bool:
    """True se o navegador estiver rodando (e travando o perfil real)."""
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
        return False  # sem tasklist/pgrep — segue e deixa o Playwright avisar


def garantir_navegador_fechado(processo: str, nome: str) -> None:
    """Bloqueia até o usuário fechar o navegador (libera o lock do perfil real)."""
    while navegador_aberto(processo):
        print(f"⚠️  O {nome} está aberto e trava o seu perfil.")
        print("   Feche TODAS as janelas (e o ícone na bandeja / startup boost).")
        input("   Depois pressione ENTER para continuar... ")


def abrir_contexto(p, nav: dict):
    """Abre o navegador: perfil REAL (Chrome/Edge) ou dedicado, conforme a config."""
    # Perfil real só faz sentido pra Chromium (Firefox o Playwright roda o dele).
    if USAR_PERFIL_REAL and nav["motor"] == "chromium":
        perfil = perfil_ativo_chromium(nav["dir"])
        print(f"🧭 {nav['nome']} — SEU perfil real (perfil: {perfil})")
        garantir_navegador_fechado(nav["processo"], nav["nome"])
        try:
            return p.chromium.launch_persistent_context(
                user_data_dir=str(nav["dir"]),
                channel=nav["canal"],
                headless=False,
                args=[f"--profile-directory={perfil}"],
                no_viewport=True,
            )
        except Exception as erro:
            sys.exit(
                f"❌ Não consegui abrir o {nav['nome']} com o seu perfil real.\n"
                f"   Confira se ele está TOTALMENTE fechado e tente de novo.\n"
                f"   Detalhe: {erro}"
            )

    # Perfil dedicado (padrão do Firefox, ou USAR_PERFIL_REAL=False).
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


def restaurar_sessao(context) -> None:
    """Reinjeta os cookies salvos da última vez (incluindo os de sessão).

    É o que mantém você logado entre execuções: o perfil em disco descarta os
    cookies de sessão ao fechar, então nós os guardamos à parte e devolvemos.
    """
    if not SESSAO_FILE.exists():
        return
    try:
        dados = json.loads(SESSAO_FILE.read_text(encoding="utf-8"))
        cookies = dados.get("cookies", [])
        if cookies:
            context.add_cookies(cookies)
    except Exception:
        pass  # sessão corrompida/inválida — segue pro login normal


def salvar_sessao(context) -> None:
    """Salva todos os cookies atuais (Moodle + provedor SSO) pra próxima vez."""
    try:
        context.storage_state(path=str(SESSAO_FILE))
    except Exception:
        pass


def garantir_login(page: Page) -> None:
    """Espera (sem ENTER manual) até o painel logado aparecer.

    Se a sessão salva ainda valer, resolve em segundos. Senão, o usuário loga na
    janela e o Playwright detecta o fim do login sozinho.
    """
    print("⏳ Abrindo o painel...")
    print("   Se aparecer a tela de login, faça o login na janela que abriu —")
    print("   eu detecto sozinho quando você entrar (não precisa apertar nada).")
    print("   💡 Marque 'Continuar conectado' / 'Confiar neste dispositivo' pra")
    print("      não repetir o 2FA nas próximas execuções.")

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
    # No perfil real, a persistência é o próprio perfil — não exportamos cookies
    # pra um arquivo (evita despejar TODOS os seus cookies em disco).
    usa_sessao_file = not (USAR_PERFIL_REAL and nav["motor"] == "chromium")

    with sync_playwright() as p:
        context = abrir_contexto(p, nav)
        context.set_default_timeout(TIMEOUT_PADRAO)
        if usa_sessao_file:
            restaurar_sessao(context)        # devolve os cookies salvos
        page = context.pages[0] if context.pages else context.new_page()

        page.goto(f"{MOODLE_URL}/my/", timeout=30_000)
        garantir_login(page)

        atividades = coletar_timeline(page)
        if usa_sessao_file:
            salvar_sessao(context)           # guarda a sessão pra próxima vez
        context.close()

    mostrar(atividades)
    salvar(atividades)


if __name__ == "__main__":
    main()
