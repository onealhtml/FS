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
- Busca por hash com estratégia configurável (`divisao` ou `fnv1a`)
- Métricas da distribuição da tabela hash (colisões, fator de carga, maior cadeia, etc.)
- Métrica comparativa completa entre `divisao` x `fnv1a` (distribuição + tempo)
- Visualização da lista encadeada de cada bucket
- Importação de contas por CSV (`numero,titular,cpf,saldo,ativa`)

## Diagrama de Classes

![Diagrama de Classes - Sistema Bancário](Banco%20Account%20Management-2026-03-30-023524.svg)

## Arquivos principais

- `listaencadeada.py`: implementação da lista encadeada
- `banco.py`: regras de negócio, hash configurável, métricas e importação CSV
- `banco_cli.py`: menu interativo no terminal
- `smoke_cli.py`: teste rápido sem interação
- `smoke_csv_hash.py`: smoke de importação CSV + debug de buckets

## Executar

```bash
python Desafio1/banco_cli.py
```

No início da execução você pode configurar:

- tamanho da tabela hash
- estratégia de hash (`divisao` ou `fnv1a`)

No menu há opções para:

- listar buckets com encadeamento
- exibir métricas da distribuição
- comparar as duas hashes com benchmark de busca

## Teste rápido

```bash
python Desafio1/smoke_cli.py
```

## Smoke CSV + buckets

```bash
python Desafio1/smoke_csv_hash.py
python Desafio1/smoke_csv_hash.py --csv Desafio1/clientes_banco.csv --table-size 20011
python Desafio1/smoke_csv_hash.py --mostrar-vazios --max-erros 10
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


