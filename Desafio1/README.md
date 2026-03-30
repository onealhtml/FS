# Banco CLI com Lista Encadeada

Projeto simples em Python para atividade de estrutura de dados, usando lista encadeada para armazenar contas bancarias.
Neste modelo, a classe `Conta` tambem funciona como no da lista (campo `prox`).

## Funcionalidades

- Inclusao de conta
- Numero da conta gerado automaticamente
- CPF informado no cadastro (exatamente 11 digitos)
- Exclusao de conta
- Consulta de conta
- Relatorio de contas
- Deposito
- Saque

## Arquivos principais

- `listaencadeada.py`: implementacao da lista encadeada
- `banco.py`: regras de negocio do banco
- `banco_cli.py`: menu interativo no terminal
- `main.py`: ponto de entrada do CLI
- `smoke_cli.py`: teste rapido sem interacao

## Executar

```bash
python Listas/ListaEncadeada/main.py
```

## Teste rapido

```bash
python Listas/ListaEncadeada/smoke_cli.py
```


