# Banco CLI com Hash + Lista Encadeada

Projeto simples em Python para atividade de estrutura de dados, usando tabela hash com tratamento de colisão por encadeamento separado (`ListaEncadeada`).
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
- Busca de conta por hash FNV-1a
- Importação de contas por CSV (`numero,titular,cpf,saldo,ativa`)

## Diagrama de Classes

![Diagrama de Classes - Sistema Bancário](Banco%20Account%20Management-2026-03-30-023524.svg)

## Arquivos principais

- `listaencadeada.py`: implementação da lista encadeada
- `banco.py`: regras de negócio do banco, hash FNV-1a e importação CSV
- `banco_cli.py`: menu interativo no terminal
- `smoke_cli.py`: teste rápido sem interação

## Executar

```bash
python Desafio1/banco_cli.py
```

## Teste rápido

```bash
python Desafio1/smoke_cli.py
```

## Formato do CSV

Cada linha deve ter 5 campos:

```text
numero,titular,cpf,saldo,ativa
```

Exemplo:

```text
386573,Bruno Silva,104.332.181-96,27842.88,False
```

Valores aceitos em `ativa`: `True/False`, `1/0`, `sim/nao`, `ativo/inativo`.


