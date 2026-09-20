"""Demo de Eval com LLM as a Judge: call center de internet.

Como rodar:  streamlit run app.py
"""

import streamlit as st

from agent import responder
from judge import avaliar
from llm import LLMConfigError, get_model_name
from rules import BUSINESS_RULES, RULE_BY_ID, SCENARIOS

st.set_page_config(page_title="Eval com LLM as a Judge", page_icon="📡", layout="wide")

VERMELHO_CLARO = "#DA291C"
ICONES = {"cumprida": "✅", "violada": "❌", "nao_aplicavel": "➖"}
ROTULOS = {"cumprida": "cumprida", "violada": "violada", "nao_aplicavel": "não se aplica"}


def aplicar_tema(tema: str):
    escuro = tema == "Escuro"
    cores = {
        "bg": "#0E1117" if escuro else "#FFFFFF",
        "surface": "#181B22" if escuro else "#F7F7F8",
        "surface_alt": "#20242D" if escuro else "#FFFFFF",
        "sidebar": "#12151C" if escuro else "#F3F4F6",
        "text": "#FFFFFF" if escuro else "#111827",
        "muted": "#A7AAB1" if escuro else "#5B6472",
        "border": "#313640" if escuro else "#D7DAE0",
        "danger_bg": "#4B2428" if escuro else "#FDE8E7",
        "danger_text": "#FF7B72" if escuro else "#A61B12",
        "success_bg": "#173B29" if escuro else "#E7F6EC",
        "success_text": "#7EE2A8" if escuro else "#176B3A",
    }
    st.markdown(
        f"""
        <style>
        .stApp, [data-testid="stAppViewContainer"] {{
            background: {cores['bg']};
            color: {cores['text']};
        }}
        header[data-testid="stHeader"] {{
            background: {cores['bg']};
            border-top: 6px solid {VERMELHO_CLARO};
        }}
        [data-testid="stSidebar"] {{ background: {cores['sidebar']}; }}
        h1, [data-testid="stHeading"] h1 {{ color: {VERMELHO_CLARO}; }}
        h2, h3, p, li, label, [data-testid="stMarkdownContainer"], [data-testid="stMetricLabel"],
        [data-testid="stMetricValue"] {{ color: {cores['text']}; }}
        [data-testid="stCaptionContainer"], small {{ color: {cores['muted']} !important; }}
        [data-testid="stBottom"] {{ background: {cores['bg']}; }}
        [data-testid="stChatInput"] {{ background: {cores['bg']}; }}
        [data-testid="stChatInput"] textarea {{
            background: {cores['surface_alt']};
            color: {cores['text']};
            border: 1px solid {cores['border']};
        }}
        [data-testid="stChatInput"] textarea::placeholder {{
            color: {cores['muted']};
            opacity: 1;
        }}
        [data-testid="stChatInput"] button {{ color: {VERMELHO_CLARO}; }}
        [data-testid="stChatMessage"], div[data-testid="stExpander"], [data-testid="stDataFrame"] {{
            background: {cores['surface']};
            border: 1px solid {cores['border']};
            border-radius: 8px;
        }}
        .stButton > button {{
            width: 100%;
            min-height: 48px;
            justify-content: flex-start;
            text-align: left;
            border: 1px solid {cores['border']};
            border-radius: 8px;
            background: {cores['surface']};
            color: {cores['text']};
        }}
        .stButton > button:hover {{
            border-color: {VERMELHO_CLARO};
            color: {cores['text']};
        }}
        .turno-meta {{
            min-height: 48px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 0.35rem 0.65rem;
            border: 1px solid {cores['border']};
            border-radius: 8px;
            background: {cores['surface_alt']};
        }}
        .turno-meta span {{ color: {cores['muted']}; font-size: 0.75rem; }}
        .turno-meta strong {{ color: {cores['text']}; font-size: 0.95rem; }}
        .turno-meta.aprovada strong {{ color: {cores['success_text']}; }}
        .turno-meta.reprovada strong {{ color: {cores['danger_text']}; }}
        .parecer-ok {{
            padding: 1rem;
            border-radius: 8px;
            background: {cores['success_bg']};
            color: {cores['success_text']};
        }}
        .parecer-erro {{
            padding: 1rem;
            border-radius: 8px;
            background: {cores['danger_bg']};
            color: {cores['danger_text']};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def resetar():
    st.session_state.messages = []
    st.session_state.selected_turn_index = None


st.session_state.setdefault("messages", [])
st.session_state.setdefault("selected_turn_index", None)
st.session_state.setdefault("tema", "Escuro")


def montar_turnos(mensagens: list[dict]) -> list[dict]:
    turnos = []
    turno_atual = None
    for mensagem in mensagens:
        if mensagem["role"] == "cliente":
            turno_atual = {"cliente": mensagem, "agente": None, "avaliacao": None}
            turnos.append(turno_atual)
        elif turno_atual is not None and turno_atual["agente"] is None:
            turno_atual["agente"] = mensagem
            turno_atual["avaliacao"] = mensagem.get("avaliacao")
    return turnos


def indice_selecionado(turnos: list[dict]) -> int | None:
    if not turnos:
        return None
    indice = st.session_state.selected_turn_index
    if indice is None or indice >= len(turnos):
        return len(turnos) - 1
    return indice


def resumo_curto(av: dict) -> str:
    if av["aprovada"]:
        return f"Juiz: nota {av['nota']:.1f}/10, aprovada"
    return f"Juiz: nota {av['nota']:.1f}/10, reprovada (violou {', '.join(av['violadas'])})"


# ---------- Barra lateral ----------
with st.sidebar:
    st.header("Configuração da demo")
    st.radio("Tema", options=["Escuro", "Claro"], horizontal=True, key="tema")
    scenario_key = st.selectbox(
        "Cenário",
        options=list(SCENARIOS),
        format_func=lambda k: SCENARIOS[k]["nome"],
        key="scenario_key",
        on_change=resetar,
    )
    st.caption(SCENARIOS[scenario_key]["descricao"])

    com_falhas = st.toggle(
        "Agente com falhas propositais",
        key="com_falhas",
        help="Liga um atendente que quebra uma regra de forma educada e convincente. "
        "Serve para ver o juiz pegando o erro.",
    )
    st.button("Limpar conversa", on_click=resetar)

    with st.expander("Regras de negócio (o gabarito do juiz)"):
        for r in BUSINESS_RULES:
            st.markdown(f"**{r['id']} – {r['titulo']}**")
            st.caption(r["texto"])

    st.caption(f"Modelo: {get_model_name()}")

scenario = SCENARIOS[scenario_key]
aplicar_tema(st.session_state.tema)

# ---------- Cabeçalho ----------
st.title("Eval na prática: um juiz avalia o atendente")
st.write(
    "O atendente (IA) responde ao cliente. Depois de cada resposta, outro modelo "
    "confere se as regras de negócio foram cumpridas."
)
with st.expander("Dados do sistema neste atendimento"):
    for chave, valor in scenario["contexto_sistema"].items():
        st.markdown(f"- **{chave}:** {valor}")

# ---------- Entrada e processamento ----------
prompt = st.chat_input("Escreva livremente a fala do cliente")

erro = None
if prompt:
    historico = st.session_state.messages + [{"role": "cliente", "content": prompt}]
    primeira_resposta = not any(m["role"] == "agente" for m in st.session_state.messages)

    resposta = None
    try:
        with st.spinner("O atendente está respondendo..."):
            resposta = responder(historico, scenario, com_falhas)
    except LLMConfigError as e:
        erro = str(e)
    except Exception as e:  # noqa: BLE001 - mostramos o erro na tela
        erro = f"Não foi possível gerar a resposta do atendente: {e}"

    if resposta is not None:
        avaliacao = None
        try:
            with st.spinner("O juiz está avaliando..."):
                avaliacao = avaliar(scenario, historico, resposta, primeira_resposta).model_dump()
        except Exception as e:  # noqa: BLE001
            erro = f"A resposta foi gerada, mas o juiz falhou: {e}"
        st.session_state.messages = historico + [
            {"role": "agente", "content": resposta, "avaliacao": avaliacao}
        ]
        st.session_state.selected_turn_index = len(montar_turnos(st.session_state.messages)) - 1

if erro:
    st.error(erro)

mensagens = st.session_state.messages
turnos = montar_turnos(mensagens)
turno_selecionado = indice_selecionado(turnos)

# ---------- Layout: chat à esquerda, juiz à direita ----------
col_chat, col_juiz = st.columns([3, 2], gap="large")

with col_chat:
    st.subheader("Atendimento")
    if not turnos:
        st.info("Escreva a fala do cliente no campo abaixo. O atendente responde e o juiz avalia cada resposta.")
    for i, turno in enumerate(turnos):
        avaliacao = turno["avaliacao"]
        selecionado = i == turno_selecionado
        prefixo = "▶ " if selecionado else ""
        linha = st.columns([6, 1.2, 1.6], gap="small")
        with linha[0]:
            if st.button(f"{prefixo}{turno['cliente']['content']}", key=f"turno_{i}"):
                st.session_state.selected_turn_index = i
                st.rerun()
        if avaliacao:
            status = "Aprovada" if avaliacao["aprovada"] else "Reprovada"
            classe_status = "aprovada" if avaliacao["aprovada"] else "reprovada"
            nota = f"{avaliacao['nota']:.1f}/10"
        else:
            status = "Sem parecer"
            classe_status = ""
            nota = "--"
        with linha[1]:
            st.markdown(
                f"<div class='turno-meta'><span>Nota</span><strong>{nota}</strong></div>",
                unsafe_allow_html=True,
            )
        with linha[2]:
            st.markdown(
                f"<div class='turno-meta {classe_status}'><span>Status</span><strong>{status}</strong></div>",
                unsafe_allow_html=True,
            )
        if turno["agente"]:
            with st.chat_message("assistant", avatar="🎧"):
                st.write(turno["agente"]["content"])
                if avaliacao:
                    st.caption(resumo_curto(avaliacao))

with col_juiz:
    st.subheader("Painel do juiz")
    if turno_selecionado is None:
        st.info("O parecer aparece aqui depois da primeira resposta do atendente.")
    else:
        turno = turnos[turno_selecionado]
        ultima = turno["avaliacao"]
        st.caption(f"Pergunta selecionada: {turno['cliente']['content']}")

        if not ultima:
            st.warning("Ainda não há parecer do juiz para esta pergunta.")
            st.stop()

        c1, c2 = st.columns(2)
        c1.metric("Nota da resposta", f"{ultima['nota']:.1f} / 10")
        c2.metric("Veredito", "Aprovada" if ultima["aprovada"] else "Reprovada")

        if ultima["aprovada"]:
            st.markdown(f"<div class='parecer-ok'>{ultima['resumo']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='parecer-erro'>{ultima['resumo']}</div>", unsafe_allow_html=True)

        for r in ultima["regras"]:
            st.markdown(
                f"{ICONES[r['status']]} **{r['id']} – {RULE_BY_ID[r['id']]['titulo']}** "
                f"({ROTULOS[r['status']]})"
            )
            st.caption(r["justificativa"])

        avaliacoes = [t["avaliacao"] for t in turnos if t["avaliacao"]]
        if len(avaliacoes) > 1:
            st.markdown("**Histórico de respostas**")
            st.dataframe(
                [
                    {
                        "Resposta": n,
                        "Nota": a["nota"],
                        "Veredito": "Aprovada" if a["aprovada"] else "Reprovada",
                        "Regras violadas": ", ".join(a["violadas"]) or "nenhuma",
                    }
                    for n, a in enumerate(avaliacoes, start=1)
                ],
                hide_index=True,
            )
            aprovadas = sum(a["aprovada"] for a in avaliacoes)
            st.caption(f"Taxa de aprovação: {aprovadas}/{len(avaliacoes)} respostas")
