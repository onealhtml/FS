# Banco CLI com Lista Encadeada

Projeto simples em Python para atividade de estrutura de dados, usando lista encadeada para armazenar contas bancárias.
Neste modelo, a classe `Conta` também funciona como nó da lista (campo `prox`).

## Funcionalidades

- Inclusão de conta
- Número da conta gerado automaticamente
- CPF informado no cadastro (exatamente 11 dígitos)
- Exclusão de conta
- Consulta de conta
- Relatório de contas
- Depósito
- Saque

## Arquivos principais

- `listaencadeada.py`: implementação da lista encadeada
- `banco.py`: regras de negócio do banco
- `banco_cli.py`: menu interativo no terminal
- `main.py`: ponto de entrada do CLI
- `smoke_cli.py`: teste rápido sem interação

## Executar

```bash
python Listas/ListaEncadeada/main.py
```

## Teste rápido

```bash
python Listas/ListaEncadeada/smoke_cli.py
```


