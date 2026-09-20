# Eval com LLM as a Judge: demo de call center

Demo em Python que mostra na prática a ideia de **Eval**: medir se uma aplicação de IA
entrega o que deveria, em vez de apenas assumir que ela funciona.

**Caso de uso:** um cliente liga para o call center de uma empresa de internet reclamando
de falta de sinal. Um atendente (IA) responde e, depois de cada resposta, um segundo
modelo (o juiz) confere se as **regras de negócio** foram cumpridas.

## Como funciona

```
Cliente ──► Atendente (LLM) ──► resposta
                                  │
                                  ▼
              Juiz (LLM, temperatura 0) confere cada regra: cumprida / violada / não se aplica
                                  │
                                  ▼
                    Nota (calculada em Python) + veredito + justificativa por regra
```

O modelo é acessado via qualquer endpoint compatível com a API de chat completions da
OpenAI (por padrão, um endpoint Qwen configurado em `.env`).

- **Modo com falhas propositais:** o atendente passa a quebrar uma regra de forma educada
  e convincente. É a demonstração do ponto central do post: uma resposta bem escrita
  ainda pode estar errada, e só uma avaliação sistemática pega isso.
- **Nota previsível:** o juiz só classifica as regras. A nota (0 a 10) e o veredito saem de
  uma conta simples em Python, o que facilita auditar o resultado.

## Regras de negócio da demo

| Regra | O que exige |
|---|---|
| R1 | Cumprimentar pelo nome e informar o protocolo na primeira resposta |
| R2 | Considerar o status da região antes de orientar qualquer procedimento |
| R3 | Com queda na região: informar previsão, sem pedir reinício do modem nem abrir visita |
| R4 | Sem queda: pedir reinício do modem; visita só se persistir, em até 48 horas úteis |
| R5 | Nunca prometer desconto, reembolso ou crédito; encaminhar ao financeiro |

Para mudar as regras ou os cenários, edite `rules.py`.

## Visual

A página usa a paleta de cores abaixo :vermelho `#DA291C` como cor principal, com preto,
branco e cinza claro de apoio. Não há nenhum logotipo da marca, só as cores.
Para trocar a paleta, edite `.streamlit/config.toml` e a constante `VERMELHO_CLARO` no `app.py`.

## Rodando no VS Code

Pré-requisito: Python 3.10 ou mais novo.

```bash
# 1. dentro da pasta do projeto, crie e ative o ambiente virtual
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 2. instale as dependências
pip install -r requirements.txt

# 3. copie .env.example para .env e preencha LLM_API_KEY (e LLM_BASE_URL/LLM_MODEL, se necessário)

# 4. suba a página
streamlit run app.py
```

A página abre em http://localhost:8501.

No VS Code, selecione o interpretador da `.venv` (Ctrl+Shift+P, "Python: Select Interpreter")
e use o terminal integrado para rodar os comandos acima.

## Subindo para o GitHub

O arquivo `.env` (com a sua chave) já está no `.gitignore`, então não vai para o repositório.
Quem baixar o projeto copia o `.env.example` para `.env` e preenche a própria chave.

```bash
git init
git add .
git commit -m "Demo de Eval com LLM as a Judge"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

Depois, para baixar em outra máquina: `git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git`.

## Estrutura

| Arquivo | Papel |
|---|---|
| `app.py` | Página Streamlit: chat à esquerda, painel do juiz à direita |
| `agent.py` | Atendente de call center (com modo de falhas propositais) |
| `judge.py` | LLM as a Judge: parecer por regra, nota e veredito |
| `llm.py` | Chamadas ao LLM via API compatível com OpenAI (chave, URL e modelo vêm do `.env`) |
| `rules.py` | Regras de negócio e cenários |
| `AGENTS.md` | Instruções para agentes de código (Copilot, Claude Code etc.) |

## Solução de problemas

- **"Chave do LLM não configurada":** preencha `LLM_API_KEY` no `.env` e reinicie o Streamlit.
- **Erro de modelo não encontrado:** troque `LLM_MODEL` no `.env` por um modelo disponível no
  endpoint configurado em `LLM_BASE_URL`.
- **Erro de SSL/certificado no Windows (`RecursionError` ou `CERTIFICATE_VERIFY_FAILED`):**
  redes corporativas costumas interceptar HTTPS com certificado próprio. `llm.py` já força o
  cliente a validar com o bundle do `certifi` em vez do backend `truststore` do Windows, que
  tem um bug de recursão nesse cenário. Se o erro persistir, é preciso confiar no certificado
  raiz da rede corporativa (não desative a verificação SSL).
