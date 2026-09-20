# Material de aula — LLM as a Judge

PDF de apoio para ensinar o conceito de **LLM as a Judge**, usando este próprio
repositório como estudo de caso.

## Conteúdo do PDF (`aula_llm_as_a_judge.pdf`)

1. Capa
2. O que é LLM as a Judge (conceito)
3. Como implementar: o juiz em código (trechos reais de `rules.py` e `judge.py`)
4. Simulação: um caso real onde o juiz aprova o atendente e outro onde pega uma
   violação (regra R3), capturados rodando `agent.py` + `judge.py`
5. Conclusão e exercício prático

## Como regenerar o PDF

```powershell
.\.venv\Scripts\python.exe -m pip install -r material_aula\requirements.txt
.\.venv\Scripts\python.exe material_aula\gerar_pdf.py
```

O script lê os exemplos de `cenarios_capturados.json`. Para capturar novos
exemplos reais (chama a API do Gemini de novo), rode:

```powershell
.\.venv\Scripts\python.exe material_aula\capturar_cenarios.py
```

e cole a saída em `cenarios_capturados.json` antes de gerar o PDF novamente.
