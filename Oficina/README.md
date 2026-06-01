# 🎓 Oficina de Web Scraping

Dois exemplos práticos, do mais simples ao caso real do Moodle da UNISC.

| Script | O que faz | Ferramenta |
|--------|-----------|------------|
| `webscraping_demo.py` | Coleta citações de um site estático e salva em CSV | `requests` + `BeautifulSoup` |
| `moodle_scraper.py` | Lista atividades pendentes no Moodle usando **o seu próprio navegador** | `playwright` |

## Setup (uma vez)

```bash
pip install -r requirements.txt
playwright install firefox   # só o Firefox é baixado; Chrome/Edge usam o do sistema
```

## Rodar o demo simples

```bash
python webscraping_demo.py
```

## Rodar o scraper do Moodle

Ele usa o **seu próprio navegador** pra reaproveitar o login. O script detecta
o que está instalado (Chrome, Edge ou Firefox) e, se houver mais de um, pergunta
qual tem o seu login no Moodle.

```bash
python moodle_scraper.py
```

Saída: `atividades_moodle.csv` e `atividades_moodle.json`.

### Como cada navegador reaproveita o login

| Navegador | Como funciona | Login |
|-----------|---------------|-------|
| **Chrome / Edge** | Usa o seu **perfil real** (o de todo dia) via `launch_persistent_context(channel=...)` | Automático — você já está logado |
| **Firefox** | O Playwright usa o **Firefox dele** (não o seu), com um perfil **dedicado** (`.perfil_firefox/`) | Uma vez na 1ª execução; depois fica salvo |

> ⚠️ **Chrome/Edge: feche o navegador por completo antes de rodar** (todas as
> janelas e o ícone da bandeja). O navegador trava o perfil real enquanto
> estiver aberto. Se sobrar algo aberto, o script avisa e espera você fechar.
> **Firefox não precisa** — o perfil é separado.

Para Chrome/Edge, o script ainda descobre **sozinho qual perfil está em uso**
(lê o `Local State` do navegador), então funciona mesmo se você tiver vários
perfis e o do Moodle não for o "Default".

### Ajustes rápidos (no topo de `moodle_scraper.py`)

- `MOODLE_URL` — endereço do Moodle.
- `NAVEGADOR_FORCADO` — `None` detecta/pergunta; ou fixe `"chrome"`, `"msedge"`,
  `"firefox"` pra pular o menu.
- `PERFIL_FORCADO` — `None` detecta o perfil ativo do Chrome/Edge; ou force
  `"Profile 1"`, `"Profile 2"`, etc.

### Resolução de problemas

- **"Não consegui abrir o navegador" / erro de perfil em uso (Chrome/Edge):**
  sobrou um processo aberto. No Windows, finalize pelo Gerenciador de Tarefas
  (`chrome.exe` / `msedge.exe`) e rode de novo.
- **Firefox: "Não consegui abrir o Firefox do Playwright":** rode
  `playwright install firefox`.
- **Caiu na tela de login:** sua sessão expirou. Faça login na janela que abriu
  e pressione ENTER no terminal — o script segue a partir daí.
- **Nenhuma atividade encontrada:** os seletores do Moodle podem ter mudado.
  Use F12 no navegador pra inspecionar e ajuste os seletores em
  `coletar_timeline` / `coletar_calendario`.
