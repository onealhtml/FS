"""
Moodle Scraper — coleta de atividades pendentes no Moodle da UNISC
==================================================================
Usa o NAVEGADOR da própria pessoa pra não precisar logar toda vez:

  • Chrome / Edge → reaproveita o seu perfil REAL (onde você já está logado
    no dia a dia). Login automático. Exige o navegador fechado antes de rodar.
  • Firefox → o Playwright usa o Firefox dele (não o seu), então mantém um
    perfil DEDICADO: você loga uma vez e fica salvo pras próximas execuções.

O script detecta sozinho o que está instalado; se houver mais de um, pergunta.

Setup (uma vez):
    pip install -r requirements.txt
    playwright install firefox      # só o Firefox precisa ser baixado;
                                    # Chrome/Edge usam a instalação do sistema

Uso:
    1. Se for usar Chrome/Edge: FECHE o navegador por completo (janelas + ícone
       da bandeja). Pra Firefox não precisa.
    2. python moodle_scraper.py
"""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import Locator, Page, sync_playwright

# ─────────────────────────────── Configuração ───────────────────────────────
MOODLE_URL = "https://portalvirtual.unisc.br/moodle"

# Forçar uma escolha (deixe None pra detectar/perguntar automaticamente):
NAVEGADOR_FORCADO: str | None = None   # "chrome" | "msedge" | "firefox"
PERFIL_FORCADO: str | None = None      # ex: "Default", "Profile 1" (só Chrome/Edge)

ARQUIVO_CSV = "atividades_moodle.csv"
ARQUIVO_JSON = "atividades_moodle.json"
PERFIL_FIREFOX = Path(__file__).resolve().parent / ".perfil_firefox"

TIMEOUT_PADRAO = 10_000  # ms — limite padrão de cada operação do Playwright

# Nomes que aparecem soltos no calendário (cabeçalhos de data, não atividades).
NOMES_GENERICOS = {
    "hoje", "amanhã", "ontem",
    "segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo",
}


# ──────────────────────────── Detecção do navegador ─────────────────────────
def navegadores_instalados() -> list[dict]:
    """Lista os navegadores disponíveis neste computador.

    Cada item traz: canal (nome p/ Playwright), nome amigável, motor
    ("chromium"/"firefox"), processo (p/ checar se está aberto) e o diretório
    de perfil real do usuário.
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


def escolher_navegador(navegadores: list[dict]) -> dict:
    """Escolhe o navegador: respeita NAVEGADOR_FORCADO, senão pergunta se >1."""
    if NAVEGADOR_FORCADO:
        for nav in navegadores:
            if nav["canal"] == NAVEGADOR_FORCADO:
                return nav
        sys.exit(f"❌ NAVEGADOR_FORCADO='{NAVEGADOR_FORCADO}' não está instalado aqui.")

    if len(navegadores) == 1:
        return navegadores[0]

    print("🧭 Encontrei mais de um navegador. Onde está o seu login no Moodle?\n")
    for i, nav in enumerate(navegadores, 1):
        modo = "login reaproveitado" if nav["motor"] == "chromium" else "login uma vez"
        print(f"   {i}. {nav['nome']}  ({modo})")
    while True:
        escolha = input("\n   Digite o número: ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(navegadores):
            return navegadores[int(escolha) - 1]
        print("   ⚠️  Opção inválida, tente de novo.")


def perfil_ativo_chromium(user_data_dir: Path) -> str:
    """Descobre o perfil em uso lendo o 'Local State' do Chrome/Edge.

    Cai pra "Default" se não conseguir ler. Pode ser sobrescrito por
    PERFIL_FORCADO.
    """
    if PERFIL_FORCADO:
        return PERFIL_FORCADO
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
    """Bloqueia até a pessoa fechar o navegador (libera o lock do perfil real)."""
    while navegador_aberto(processo):
        print(f"⚠️  O {nome} está aberto e trava o seu perfil.")
        print("   Feche TODAS as janelas (e o ícone na bandeja, se houver).")
        input("   Depois pressione ENTER para continuar... ")


def abrir_contexto(p, nav: dict):
    """Abre o navegador certo: perfil real (Chrome/Edge) ou dedicado (Firefox)."""
    if nav["motor"] == "chromium":
        perfil = perfil_ativo_chromium(nav["dir"])
        print(f"🧭 {nav['nome']} (perfil: {perfil}) — reaproveitando o seu login")
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
                f"❌ Não consegui abrir o {nav['nome']}.\n"
                f"   Confira se ele está totalmente fechado e tente de novo.\n"
                f"   Detalhe: {erro}"
            )

    # Firefox: Playwright usa o Firefox dele, então mantemos um perfil próprio.
    print(f"🧭 Firefox — perfil dedicado em {PERFIL_FIREFOX.name}/")
    print("   (o login fica salvo aqui; na 1ª vez você loga, depois é automático)")
    try:
        return p.firefox.launch_persistent_context(
            user_data_dir=str(PERFIL_FIREFOX),
            headless=False,
        )
    except Exception as erro:
        sys.exit(
            "❌ Não consegui abrir o Firefox do Playwright.\n"
            "   Rode 'playwright install firefox' e tente de novo.\n"
            f"   Detalhe: {erro}"
        )


# ────────────────────────────── Coleta de dados ─────────────────────────────
def coletar_timeline(page: Page) -> list[dict]:
    """Coleta atividades da timeline do painel; cai pro calendário se vazia."""
    print("\n📋 Buscando atividades na timeline...")
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
    print("\n" + "=" * 60)
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
    print("🎓 Moodle Scraper — usando o seu próprio navegador\n")

    navegadores = navegadores_instalados()
    if not navegadores:
        sys.exit("❌ Não encontrei Chrome, Edge nem Firefox neste computador.")

    nav = escolher_navegador(navegadores)

    with sync_playwright() as p:
        context = abrir_contexto(p, nav)
        context.set_default_timeout(TIMEOUT_PADRAO)
        page = context.pages[0] if context.pages else context.new_page()

        page.goto(f"{MOODLE_URL}/my/", timeout=15_000)
        page.wait_for_timeout(2_000)

        # Chrome/Edge: normalmente já logado. Firefox (1ª vez): login manual.
        if any(t in page.url.lower() for t in ("login", "auth", "sso")):
            print("🔑 Faça login no navegador que abriu.")
            input("   Quando estiver no PAINEL, pressione ENTER aqui... ")
        else:
            print("✅ Já logado pelo seu perfil — nenhum login necessário.")

        atividades = coletar_timeline(page)
        context.close()

    mostrar(atividades)
    salvar(atividades)


if __name__ == "__main__":
    main()
