# AGENTS.md

Instruções para agentes de código (Copilot, Claude Code, Codex etc.) que trabalham neste repositório.

## O que é este projeto

Demo em Python de **Eval com LLM as a Judge**. Um atendente de call center (IA) responde a um
cliente sem sinal de internet, e um segundo modelo (o juiz) confere, regra por regra, se a
resposta seguiu as regras de negócio. A interface é uma página Streamlit em localhost.

Tudo usa um endpoint compatível com a API de chat completions da OpenAI (SDK `openai`),
apontando por padrão para um modelo Qwen. A chave, a URL base e o modelo vêm do `.env`
(`LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`).

## Comandos

```bash
python -m venv .venv                 # criar o ambiente virtual
pip install -r requirements.txt      # instalar dependências
streamlit run app.py                 # subir a página em http://localhost:8501
```

Não há suíte de testes automatizados. Para checar a sintaxe: `python -m py_compile *.py`.

## Estrutura

| Arquivo | Papel |
|---|---|
| `app.py` | Página Streamlit: chat à esquerda, painel do juiz à direita |
| `agent.py` | Atendente de call center e o modo de falhas propositais |
| `judge.py` | Juiz: parecer por regra, nota e veredito |
| `llm.py` | Único lugar que chama o LLM (chave, URL base e modelo vêm do `.env`) |
| `rules.py` | Regras de negócio (R1 a R5) e cenários de teste |

## Convenções

- **Idioma:** textos da interface, prompts, comentários e documentação em português do Brasil.
- **Regras de negócio só em `rules.py`.** O atendente e o juiz leem `BUSINESS_RULES` de lá.
  Ao adicionar ou alterar uma regra, atualize também a tabela de regras do `README.md`.
- **Chamadas ao LLM só em `llm.py`.** `agent.py` e `judge.py` não importam o SDK diretamente.
- **O juiz só classifica.** Ele devolve `cumprida`, `violada` ou `nao_aplicavel` por regra, com
  temperatura 0. A nota (0 a 10) e o veredito são calculados em Python em `judge.avaliar`.
  Não peça a nota ao modelo.
- **R1 só vale na primeira resposta do atendente.** O `app.py` informa isso ao juiz por meio de
  `primeira_resposta`.
- **Modo com falhas** (`agent._FALHAS_PROPOSITAIS`) existe só para demonstrar o juiz pegando
  erros. Não o ative por padrão e não o use fora da demo.
- **Estado da página** fica em `st.session_state` (`messages`, `pending`). Cada mensagem do
  atendente guarda a própria `avaliacao`.
- **Visual:** a página usa a paleta da Claro (vermelho `#DA291C`, preto, branco e cinza claro), definida em `.streamlit/config.toml` e em um pequeno CSS no início do `app.py`. **Não adicione logotipo da Claro** nem outros elementos gráficos da marca; só as cores.
- Evite o parâmetro `use_container_width` do Streamlit, que está sendo descontinuado.

## Segurança

- **Nunca commite o `.env`.** Ele está no `.gitignore` e contém a chave da API.
- **Nunca escreva chaves no código nem nos exemplos.** Use o `.env.example` com o valor de exemplo.
- Os dados dos cenários (nomes, protocolos, planos) são fictícios. Não use dados reais de clientes.

## Ao mexer no código

1. Rode `python -m py_compile *.py` depois de editar.
2. Se mudar prompts, regras ou o formato do parecer, teste na página com os três cenários,
   com e sem o modo de falhas, e confira se o juiz continua reprovando as violações esperadas.
3. Se o modelo padrão mudar, atualize `DEFAULT_MODEL` em `llm.py` e o `.env.example`.
