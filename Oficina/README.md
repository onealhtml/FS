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

O script abre o navegador num **perfil dedicado** (próprio dele, em
`.perfil_moodle_<navegador>/`) e vai pro painel:

1. **1ª vez:** se cair na tela de login, você loga normalmente (usuário/senha ou
   SSO) **na janela que abriu**. O Playwright fica observando a página e, no
   instante em que o painel logado aparece, **detecta sozinho** e começa a
   coletar — você não aperta nada no terminal.
2. **Próximas vezes:** a sessão fica salva no perfil dedicado. Como o Moodle da
   UNISC usa SSO, normalmente ele **reentra sem você digitar nada**.

O sinal de "logado" que ele observa é o link de logout do Moodle
(`a[href*='login/logout.php']`) — existe em qualquer tema e nunca na tela de
login, então a detecção é confiável.

> ✅ Não precisa fechar o seu navegador do dia a dia: o perfil é separado.

### Ajustes rápidos (no topo de `moodle_scraper.py`)

- `MOODLE_URL` — endereço do Moodle.
- `NAVEGADOR_FORCADO` — `None` usa o 1º navegador instalado (preferência:
  Chrome → Edge → Firefox); ou fixe `"chrome"`, `"msedge"`, `"firefox"`.
- `TIMEOUT_LOGIN` — quanto tempo (ms) ele espera você logar (padrão: 5 min).

### Resolução de problemas

- **"Não detectei o login em 5 minutos":** demorou pra logar (ou o painel não
  abriu). Rode de novo e faça o login. Se precisar de mais tempo, aumente
  `TIMEOUT_LOGIN`.
- **"Não consegui abrir o navegador":** se for Firefox, rode
  `playwright install firefox`. Chrome/Edge usam a instalação do sistema.
- **Quer logar do zero / sessão bugada:** apague a pasta
  `.perfil_moodle_<navegador>/` e rode de novo.
- **Nenhuma atividade encontrada:** os seletores do Moodle podem ter mudado.
  Use F12 no navegador pra inspecionar e ajuste os seletores em
  `coletar_timeline` / `coletar_calendario`.
