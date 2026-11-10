# Laboratório 11 — Test doubles e testes de unidade

Disciplina CC8550 — Simulação e Teste de Software, FEI, 2º semestre de 2026.
Soluções dos **exercícios 1 e 2** do Laboratório 11, cada uma em um projeto independente.

## Executar

Requer Python 3.12 ou superior. Na raiz do repositório:

```bash
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Execute cada exercício na sua pasta, conforme o material:

```bash
cd ex1
python -m pytest -q --cov=src --cov-branch --cov-report=term-missing --cov-fail-under=100
cd ../ex2
python -m pytest -q --cov=src --cov-branch --cov-report=term-missing --cov-fail-under=100
```

Não são necessárias credenciais, APIs ou serviços externos. O código de produção usa somente a biblioteca padrão; pytest e pytest-cov são dependências de desenvolvimento.

## Exercício 1 — Frete em dólar

Implementação: `ex1/src/conversor_frete.py`. Testes: `ex1/tests/test_conversor_frete.py`.

- Cotação recebida pelo construtor, sem consulta real à internet.
- Conversão entre centavos com `round`, inclusive empates para o inteiro par.
- Rejeição de taxas zero/negativas.
- Tradução de `TimeoutError` em `CotacaoIndisponivel`, preservando a causa.
- Stub escrito à mão e casos com `pytest.mark.parametrize`.
- Timeout simulado com `Mock` e `side_effect`.

### Resposta conceitual — por que não usar um serviço real de cotação?

O objetivo é verificar a regra do conversor, não a disponibilidade do serviço externo. Uma cotação real muda com o tempo, depende de rede e pode falhar por causas alheias ao código testado. Isso tornaria o teste lento e não repetível. Um stub fixa a taxa e permite escolher valores de fronteira; um Mock com `side_effect` produz o timeout de forma determinística. A conexão real exigiria testes de integração separados.

## Exercício 2 — Cobrança com tentativas

Implementação: `ex2/src/confirmacao.py`. Testes: `ex2/tests/test_confirmacao.py`.

- Aprovação: uma confirmação por e-mail e retorno `"aprovado"`.
- Negação: nenhum e-mail, nenhuma nova tentativa e retorno `"negado"`.
- `ConnectionError` no gateway: repetição até o limite total de cobranças.
- Última tentativa falhou: um e-mail `"falha na cobranca"` e propagação da última exceção.
- Limites menores que 1 são rejeitados antes de qualquer efeito.
- Erros diferentes de conexão não são repetidos.
- Falha no e-mail após aprovação não gera uma segunda cobrança.

### Resposta conceitual — por que conferir chamadas não é excesso?

Cobrar o pedido correto, passar o valor correto, respeitar o limite de tentativas e avisar uma única vez são os próprios requisitos observáveis. Conferir apenas o status retornado não detectaria uma cobrança duplicada ou um e-mail indevido. Por isso, os testes verificam quantidade, argumentos e ausência de chamadas, sem acoplar as verificações a variáveis internas do algoritmo.

As dependências são Mocks locais: nenhum pagamento ou envio de e-mail real acontece. A rotina de retry reproduz o contrato didático do laboratório; não pretende resolver idempotência de pagamentos em produção.

## Fontes

- [Atividade 11 no Moodle](https://moodle.fei.edu.br/mod/assign/view.php?id=37900), anexo `lab-11.pdf`, exercícios 1 e 2 (páginas 4 e 5), consultado em 09/11/2026, horário de Brasília.
- [Aula 11](https://moodle.fei.edu.br/mod/resource/view.php?id=4911): test doubles, isolamento e verificação de interações.

Os slides não são redistribuídos neste repositório.

## Validação executada

Ambiente: Python 3.13.18, pytest 9.1.1 e pytest-cov 7.1.0.

| Projeto | Testes aprovados | Cobertura de linhas e ramos |
| --- | ---: | ---: |
| ex1 | 12 | 100% |
| ex2 | 14 | 100% |

A cobertura confirma que os ramos implementados foram exercitados; a verificação dos resultados e efeitos está nas asserções dos testes.
