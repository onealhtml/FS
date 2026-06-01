# 🎓 Oficina de Web Scraping

Dois exemplos práticos, do mais simples ao caso real do Moodle da UNISC.

| Script | O que faz | Ferramenta |
|--------|-----------|------------|
| `webscraping_demo.py` | Coleta citações de um site estático e salva em CSV | `requests` + `BeautifulSoup` |
| `moodle_scraper.py` | Lista atividades pendentes no Moodle usando **o seu próprio navegador** | `playwright` |

## Setup (uma vez)

```bash
pip install -r requirements.txt
playwright install
```

## Rodar o demo simples

```bash
python webscraping_demo.py
```

## Rodar o scraper do Moodle

Ele usa o **navegador real** (Chrome ou Edge) com o perfil onde você já está
logado — então **não precisa logar de novo a cada execução**.

> ⚠️ **Antes de rodar, feche o Chrome/Edge por completo** (todas as janelas e o
> ícone na bandeja). O navegador trava o perfil enquanto estiver aberto, e o
> script precisa desse perfil pra reaproveitar a sua sessão. Se algo continuar
> aberto, o próprio script avisa e espera você fechar.

```bash
python moodle_scraper.py
```

Saída: `atividades_moodle.csv` e `atividades_moodle.json`.

### Como ele reaproveita o login

Em vez de abrir um Chromium "limpo" e pedir login toda vez, o script chama
`launch_persistent_context()` apontando para o diretório de perfil do seu
navegador instalado:

```python
context = p.chromium.launch_persistent_context(
    user_data_dir=user_data_dir,   # perfil real do Chrome/Edge
    channel="chrome",              # ou "msedge"
    headless=False,
)
```

Como é o mesmo perfil de sempre, os cookies e a sessão SSO da UNISC continuam
válidos — login automático.

### Ajustes rápidos (no topo de `moodle_scraper.py`)

- `MOODLE_URL` — endereço do Moodle.
- `PERFIL` — `"Default"` por padrão. Se você usa vários perfis no navegador,
  troque por `"Profile 1"`, `"Profile 2"`, etc.

### Resolução de problemas

- **"Não consegui abrir o navegador" / erro de perfil em uso:** sobrou um
  processo aberto. No Windows, finalize pelo Gerenciador de Tarefas
  (`chrome.exe` / `msedge.exe`) e rode de novo.
- **Caiu na tela de login:** sua sessão expirou. Faça login na janela que abriu
  e pressione ENTER no terminal — o script segue a partir daí.
- **Nenhuma atividade encontrada:** os seletores do Moodle podem ter mudado.
  Use F12 no navegador pra inspecionar e ajuste os seletores em
  `coletar_timeline` / `coletar_calendario`.
