# 🎓 Oficina de Web Scraping

Dois exemplos práticos, do mais simples ao caso real do Moodle da UNISC.

| Script | O que faz | Ferramenta |
|--------|-----------|------------|
| `webscraping_demo.py` | Coleta citações de um site estático e salva em CSV | `requests` + `BeautifulSoup` |
| `moodle_scraper.py` | Lista atividades pendentes no Moodle com **login automático** | `playwright` |

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

```bash
python moodle_scraper.py
```

Saída: `atividades_moodle.csv` e `atividades_moodle.json`.

### Login automático (sem apertar ENTER)

Em qualquer modo, o Playwright **detecta sozinho** quando o login termina (o
painel logado aparece) e já começa a coletar — você não aperta nada no terminal.
O sinal observado é o link de logout do Moodle (`a[href*='login/logout.php']`),
que existe em qualquer tema e nunca na tela de login.

Há dois modos, controlados por `USAR_PERFIL_REAL` no topo do script:

**Modo padrão — `USAR_PERFIL_REAL = True` (seu perfil real do Chrome/Edge)**

Usa o perfil onde você já está logado no dia a dia.

> ⚠️ **Feche o navegador por completo antes de rodar** (todas as janelas, o ícone
> da bandeja e o *startup boost*). Ele trava o perfil enquanto aberto; o script
> avisa e espera se ainda estiver rodando.

Se você **continua logado** no Moodle depois de reabrir o navegador, aqui também
entra **direto, sem login**. Se você sempre precisa relogar ao reabrir, então seu
login é "de sessão" (vive só na memória) e nem o perfil real evita o login —
nesse caso use o modo dedicado abaixo ou peça o modo CDP.

**Modo alternativo — `USAR_PERFIL_REAL = False` (perfil dedicado)**

Usa um perfil próprio do script (`.perfil_moodle_<navegador>/`) e guarda os
cookies em `sessao_moodle.json`. Você loga **uma vez** e as próximas execuções
reinjetam a sessão e entram sozinhas. **Não precisa fechar o seu navegador.**

> 💡 **No 1º login, marque "Continuar conectado" / "Confiar neste dispositivo"**
> pra não repetir o 2FA depois.

#### Como saber se o modo perfil real vai te dar "zero login"

Feche o navegador **completamente** (Gerenciador de Tarefas → encerre todos os
`msedge.exe`/`chrome.exe`), reabra e entre no Moodle:

- **Continua logado?** → login persistente → o perfil real entra direto. 🎉
- **Pede login de novo?** → login só de sessão → use o modo dedicado (ou CDP).

### Ajustes rápidos (no topo de `moodle_scraper.py`)

- `USAR_PERFIL_REAL` — `True` usa o seu perfil real (fecha o navegador antes);
  `False` usa perfil dedicado + `sessao_moodle.json` (loga 1x e reusa).
- `MOODLE_URL` — endereço do Moodle.
- `NAVEGADOR_FORCADO` — `None` usa o 1º navegador instalado (preferência:
  Chrome → Edge → Firefox); ou fixe `"chrome"`, `"msedge"`, `"firefox"`.
- `TIMEOUT_LOGIN` — quanto tempo (ms) ele espera você logar (padrão: 5 min).

### Resolução de problemas

- **"Não detectei o login em 5 minutos":** demorou pra logar (ou o painel não
  abriu). Rode de novo e faça o login. Se precisar de mais tempo, aumente
  `TIMEOUT_LOGIN`.
- **"Não consegui abrir o navegador com o seu perfil real":** o navegador ainda
  está aberto (lock). Encerre todos os `msedge.exe`/`chrome.exe` no Gerenciador
  de Tarefas (ou desligue o *startup boost*) e rode de novo.
- **"Não consegui abrir o navegador" (Firefox):** rode `playwright install firefox`.
- **Ainda pede login/2FA toda vez:** faça o teste de "zero login" acima. Se o seu
  login é só de sessão, troque pra `USAR_PERFIL_REAL = False` (loga 1x e reusa via
  `sessao_moodle.json`) e marque "Continuar conectado" / "Confiar neste dispositivo".
- **Quer logar do zero / sessão bugada:** apague `sessao_moodle.json` e a pasta
  `.perfil_moodle_<navegador>/` e rode de novo.
- **Nenhuma atividade encontrada:** os seletores do Moodle podem ter mudado.
  Use F12 no navegador pra inspecionar e ajuste os seletores em
  `coletar_timeline` / `coletar_calendario`.
