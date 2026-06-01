"""
🎓 Web Scraping no Moodle com Playwright
=========================================
Busca atividades pendentes no painel do Moodle.

Requisitos:
    pip install playwright
    playwright install chromium

Uso:
    python moodle_scraper.py
"""

from playwright.sync_api import sync_playwright
import csv, json, os, re

# ⚙️ CONFIGURAÇÃO
MOODLE_URL = "https://portalvirtual.unisc.br/moodle"
AUTH_FILE = "auth.json"


def fazer_login(page):
    print("🌐 Abrindo o Moodle...")
    page.goto(MOODLE_URL, timeout=15000)
    print("🔑 Faça login no navegador que abriu.")
    print("   Depois de entrar no PAINEL, pressione ENTER aqui...")
    input()


def coletar_timeline(page):
    """Coleta atividades da timeline do painel."""
    print("\n📋 Buscando atividades na timeline...")

    page.goto(f"{MOODLE_URL}/my/", timeout=15000)
    page.wait_for_timeout(3000)

    # Tenta expandir
    try:
        btn = page.locator("a[data-limit='0'], [data-action='more-events']").first
        if btn.is_visible(timeout=2000):
            btn.click()
            page.wait_for_timeout(2000)
    except Exception:
        pass

    for seletor in [
        "[data-region='event-list-item']",
        ".event-list-item",
        "[data-region='timeline'] .list-group-item",
    ]:
        loc = page.locator(seletor)
        if loc.count() > 0:
            print(f"   ✅ {loc.count()} itens na timeline")
            return extrair_itens(loc)

    print("   ⚠️  Timeline vazia, tentando calendário...")
    return coletar_calendario(page)


def coletar_calendario(page):
    """Coleta do calendário de próximos eventos."""
    print("📅 Buscando no calendário...")

    page.goto(f"{MOODLE_URL}/calendar/view.php?view=upcoming", timeout=15000)
    page.wait_for_timeout(3000)

    eventos = page.locator("[data-event-id]")
    count = eventos.count()

    if count == 0:
        eventos = page.locator(".event")
        count = eventos.count()

    print(f"   → {count} eventos encontrados")
    return extrair_itens(eventos)


def extrair_itens(locator):
    """Extrai nome, prazo e link de cada item."""
    raw = []

    for i in range(locator.count()):
        item = locator.nth(i)
        try:
            # Nome
            nome = ""
            for sel in ["a[href*='mod/']", ".event-name-container a", "h6 a"]:
                try:
                    el = item.locator(sel).first
                    if el.is_visible(timeout=500):
                        nome = el.inner_text(timeout=1000).strip()
                        break
                except Exception:
                    continue

            if not nome:
                nome = item.inner_text(timeout=1000).split("\n")[0].strip()

            # Prazo
            prazo = "Sem prazo"
            for sel in ["small", ".text-muted", "time", ".event-time"]:
                try:
                    el = item.locator(sel).first
                    if el.is_visible(timeout=500):
                        prazo = el.inner_text(timeout=1000).strip()
                        break
                except Exception:
                    continue

            # Link
            link = ""
            try:
                link = item.locator("a[href*='mod/']").first.get_attribute("href", timeout=500) or ""
            except Exception:
                pass

            # Limpa o link (remove &action=editsubmission etc)
            link_limpo = re.sub(r"[&?]action=\w+", "", link)

            if nome and len(nome) > 2:
                raw.append({
                    "nome": nome,
                    "prazo": prazo,
                    "link": link,
                    "link_base": link_limpo,
                    "tipo": identificar_tipo(link, nome),
                })
        except Exception:
            continue

    return deduplicar(raw)


def deduplicar(itens):
    """Remove duplicatas pelo link, priorizando o item com nome mais descritivo."""
    # Nomes genéricos = provavelmente pegou o header de data errado
    def eh_nome_generico(nome):
        genericos = ["hoje", "amanhã", "ontem", "segunda", "terça", "quarta",
                      "quinta", "sexta", "sábado", "domingo"]
        return nome.lower().strip().rstrip(",") in genericos

    # Agrupa por link base (sem parâmetros de ação)
    por_link = {}
    sem_link = []

    for item in itens:
        if not item["link_base"]:
            sem_link.append(item)
            continue

        chave = item["link_base"]
        if chave not in por_link:
            por_link[chave] = item
        else:
            existente = por_link[chave]
            # Prefere o nome mais descritivo (não genérico e mais longo)
            if eh_nome_generico(existente["nome"]) and not eh_nome_generico(item["nome"]):
                por_link[chave] = item
            elif len(item["nome"]) > len(existente["nome"]) and not eh_nome_generico(item["nome"]):
                por_link[chave] = item
            # Se o existente não tem prazo bom mas o novo tem, pega o prazo
            if existente["prazo"] == "Sem prazo" and item["prazo"] != "Sem prazo":
                por_link[chave]["prazo"] = item["prazo"]
            elif existente["prazo"] in ["Ver no Moodle"] and item["prazo"] not in ["Sem prazo", "Ver no Moodle"]:
                por_link[chave]["prazo"] = item["prazo"]

    # Deduplica sem_link por nome
    nomes_vistos = set()
    sem_link_unicos = []
    for item in sem_link:
        if item["nome"] not in nomes_vistos and not eh_nome_generico(item["nome"]):
            nomes_vistos.add(item["nome"])
            sem_link_unicos.append(item)

    resultado = list(por_link.values()) + sem_link_unicos

    # Remove campo auxiliar
    for r in resultado:
        r.pop("link_base", None)

    return resultado


def identificar_tipo(link, nome):
    link = (link or "").lower()
    nome = (nome or "").lower()

    if "assign" in link or "tarefa" in nome or "trabalho" in nome:
        return "📝 Trabalho"
    elif "quiz" in link or "prova" in nome or "questionário" in nome:
        return "📝 Questionário"
    elif "forum" in link or "fórum" in nome:
        return "💬 Fórum"
    elif "glossary" in link or "glossário" in nome:
        return "📖 Glossário"
    elif "data" in link and "mod/data" in link:
        return "🗃️ Base de dados"
    elif "workshop" in link:
        return "🔧 Workshop"
    elif "choice" in link:
        return "✅ Escolha"
    return "📄 Atividade"


def main():
    print("🎓 Moodle Scraper\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        if os.path.exists(AUTH_FILE):
            print("🔄 Reutilizando sessão salva...")
            context = browser.new_context(storage_state=AUTH_FILE)
        else:
            context = browser.new_context()

        context.set_default_timeout(10000)
        page = context.new_page()

        page.goto(f"{MOODLE_URL}/my/", timeout=15000)
        page.wait_for_timeout(2000)

        url_atual = page.url.lower()
        if "login" in url_atual or "auth" in url_atual or "sso" in url_atual:
            print("❌ Sessão expirou ou primeiro acesso.")
            fazer_login(page)

        context.storage_state(path=AUTH_FILE)
        print("✅ Logado!\n")

        atividades = coletar_timeline(page)
        browser.close()

    # Resultados
    print("\n" + "=" * 60)
    print(f"📊 RESULTADO: {len(atividades)} atividades encontradas!")
    print("=" * 60 + "\n")

    if not atividades:
        print("Nenhuma atividade encontrada.")
        print("💡 Use F12 no Moodle pra verificar os seletores CSS")
        return

    for i, a in enumerate(atividades, 1):
        print(f"{i}. {a['tipo']}  {a['nome']}")
        print(f"   ⏰ {a['prazo']}")
        if a["link"]:
            print(f"   🔗 {a['link']}")
        print()

    # Salva
    with open("atividades_moodle.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["nome", "tipo", "prazo", "link"])
        w.writeheader()
        w.writerows(atividades)

    with open("atividades_moodle.json", "w", encoding="utf-8") as f:
        json.dump(atividades, f, ensure_ascii=False, indent=2)

    print("💾 Salvo em atividades_moodle.csv e atividades_moodle.json")
    print("🎉 Pronto!")


if __name__ == "__main__":
    main()