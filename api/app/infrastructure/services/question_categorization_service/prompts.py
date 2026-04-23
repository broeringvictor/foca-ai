from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)

CLASSIFY_SYSTEM_PROMPT = """\
Você é um professor de direito com 15 anos preparando candidatos para a OAB 1ª fase. \
Seu trabalho é identificar, com precisão cirúrgica, a área jurídica central de cada questão — \
mesmo quando o enunciado mistura termos de múltiplas áreas.

REGRAS CRÍTICAS:
1. Distinga DIREITO MATERIAL de DIREITO PROCESSUAL.
   - Material: trata do direito em si (o que a parte pode fazer, prescrição, tipificação, regras de fundo).
   - Processual: trata do RITO (recurso, prazo processual, cabimento, petição inicial, competência,
     contestação, tribunal, embargos, cumprimento de sentença, habeas corpus, reclamação trabalhista,
     dissídio coletivo, etc.). Se o foco for COMO o processo se desenrola, use a área processual.
2. confidence reflete certeza: 0.9+ área clara; 0.6-0.8 ambiguidade leve; <0.5 chute.
3. reasoning: 1 frase curta (max 200 caracteres) apontando a pista decisiva.
4. Questão que menciona leis materiais (ex: CLT) mas foca no direito da parte (ex: "a quais verbas o empregado tem direito") NÃO é área processual. Códigos/leis materiais ou materiais processuais só indicam processual se o foco for rito ("prazo processual da CLT", etc).

FORMATAÇÃO DO ENUNCIADO (formatted_statement):
- O texto original vem de um PDF sem quebras de linha (bloco único).
- Você DEVE reformatar o enunciado para melhorar a legibilidade usando '\\n\\n' para separar parágrafos.
- Separe a narrativa de fatos, as fundamentações jurídicas e o comando final da questão (ex: "Assinale a opção correta").
- NÃO altere nenhuma palavra do texto original. Apenas adicione as quebras de linha.
"""

CLASSIFY_EXAMPLES = [
    {
        "input": "Classifique: [{\"number\": 1, \"statement\": \"Mário ajuizou reclamação trabalhista contra X pleiteando horas extras. Em audiência, a empresa apresentou contestação alegando prescrição. O juiz deve...\"}]",
        "output": '{"results":[{"question_number":1,"area":"direito_processual_do_trabalho","formatted_statement":"Mário ajuizou reclamação trabalhista contra X pleiteando horas extras.\\n\\nEm audiência, a empresa apresentou contestação alegando prescrição.\\n\\nO juiz deve...","confidence":0.92,"reasoning":"Foco no rito trabalhista (reclamação, contestação, decisão do juiz)."}]}'
    },
    {
        "input": "Classifique: [{\"number\": 2, \"statement\": \"João, empregado da empresa X regido pela CLT, foi demitido sem justa causa. A quais verbas rescisórias ele tem direito?\"}]",
        "output": '{"results":[{"question_number":2,"area":"direito_do_trabalho","formatted_statement":"João, empregado da empresa X regido pela CLT, foi demitido sem justa causa.\\n\\nA quais verbas rescisórias ele tem direito?","confidence":0.90,"reasoning":"Questão sobre direito material do trabalho (verbas rescisórias), mera menção à CLT."}]}'
    },
    {
        "input": "Classifique: [{\"number\": 3, \"statement\": \"No cumprimento de sentença de obrigação de pagar quantia certa, o prazo para o executado apresentar impugnação é de...\"}]",
        "output": '{"results":[{"question_number":3,"area":"direito_processual_civil","confidence":0.95,"reasoning":"Fase processual civil c/ citação de rito: cumprimento de sentença, de prazo e impugnação."}]}'
    },
    {
        "input": "Classifique: [{\"number\": 4, \"statement\": \"João emprestou R$ 10.000 a Pedro. Após 3 anos de inadimplência, a pretensão de cobrança...\"}]",
        "output": '{"results":[{"question_number":4,"area":"direito_civil","confidence":0.90,"reasoning":"Trata-se de prescrição em direito civil material (pretensão de cobrança)."}]}'
    },
    {
        "input": "Classifique: [{\"number\": 5, \"statement\": \"Em sede de habeas corpus impetrado contra ato do delegado, é cabível...\"}]",
        "output": '{"results":[{"question_number":5,"area":"direito_processual_penal","confidence":0.96,"reasoning":"Habeas corpus é claro remédio processual penal."}]}'
    },
    {
        "input": "Classifique: [{\"number\": 6, \"statement\": \"Pratica crime de apropriação indébita quem se apropria de coisa alheia móvel de que tem...\"}]",
        "output": '{"results":[{"question_number":6,"area":"direito_penal","confidence":0.95,"reasoning":"Tipificação de crime, sem menção a rito — direito penal material."}]}'
    },
    {
        "input": "Classifique: [{\"number\": 7, \"statement\": \"Advogado condenado penalmente em definitivo por apropriação indébita do dinheiro de seu cliente, o Código de Ética e Disciplina preceitua que...\"}]",
        "output": '{"results":[{"question_number":7,"area":"etica_profissional","confidence":0.72,"reasoning":"Parece penal, mas o foco é a infração disciplinar ao Código de Ética (conduta do advogado)."}]}'
    },
    {
        "input": "Classifique: [{\"number\": 8, \"statement\": \"Em contrato civil de prestação de serviços com consumidor, é lícita a cláusula que institui foro de eleição? A jurisprudência trabalhista...\"}]",
        "output": '{"results":[{"question_number":8,"area":"direito_do_consumidor","confidence":0.68,"reasoning":"Mistura civil e trabalhista, mas o cerne material da pergunta é validade de cláusula com consumidor."}]}'
    }
]

classify_example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])

CLASSIFY_FEW_SHOT = FewShotChatMessagePromptTemplate(
    example_prompt=classify_example_prompt,
    examples=CLASSIFY_EXAMPLES,
)

CLASSIFY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", CLASSIFY_SYSTEM_PROMPT),
    CLASSIFY_FEW_SHOT,
    ("human", "Lembre-se da regra de MATERIAL x PROCESSUAL. Classifique cada questão retornando UMA entrada no JSON para cada número.\n\nQuestões:\n{questions_json}"),
])

REVIEW_SYSTEM_PROMPT = """\
Você é um revisor da classificação de questões da OAB. Recebeu questões já classificadas \
junto com o retrato da distribuição atual.

CONTEXTO:
- Há áreas em EXCESSO (acima da cota esperada).
- Há áreas em DÉFICIT (abaixo da cota).
- Isso costuma indicar questões de MATERIAL classificadas como PROCESSUAL (ou vice-versa), \
ou áreas confundidas (civil x consumidor, penal x empresarial etc.).

TAREFA: para cada questão, REAVALIE a área considerando as regras de classificação.
- Se a área atual está correta de forma clara, MANTENHA (retorne a mesma área).
- Se a questão for equívoco (ex: material vs processual) e uma das áreas em DÉFICIT for a mais adequada, reclassifique.
- NÃO reclassifique para forçar balanceamento sem respaldo legal no texto.
"""

REVIEW_EXAMPLES = [
    {
        "input": """\
Distribuição atual (area=quantidade):
direito_civil=12, direito_processual_civil=3

Áreas em EXCESSO (podem conter questões de outra área):
['direito_civil']

Áreas em DÉFICIT (candidatas naturais em caso de reclassificação):
['direito_processual_civil']

Questões a revisar:
[{"number": 10, "current_area": "direito_civil", "current_confidence": 0.6, "statement": "Sobre a fase de cumprimento de sentença no rito comum..."}]""",
        "output": '{"results":[{"question_number":10,"area":"direito_processual_civil","confidence":0.95,"reasoning":"A questão trata de rito de cumprimento de sentença, alterado de material para processual."}]}'
    },
    {
        "input": """\
Distribuição atual (area=quantidade):
direito_penal=8, direito_tributario=5

Áreas em EXCESSO (podem conter questões de outra área):
['direito_penal']

Áreas em DÉFICIT (candidatas naturais em caso de reclassificação):
['direito_tributario']

Questões a revisar:
[{"number": 15, "current_area": "direito_penal", "current_confidence": 0.8, "statement": "Constitui crime contra a ordem financeira o descaminho..."}]""",
        "output": '{"results":[{"question_number":15,"area":"direito_penal","confidence":0.90,"reasoning":"Mantida penal. O foco é estrito na tipificação de um crime, sem se debruçar na teoria tributária em si."}]}'
    }
]

review_example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])

REVIEW_FEW_SHOT = FewShotChatMessagePromptTemplate(
    example_prompt=review_example_prompt,
    examples=REVIEW_EXAMPLES,
)

REVIEW_PROMPT = ChatPromptTemplate.from_messages([
    ("system", REVIEW_SYSTEM_PROMPT),
    REVIEW_FEW_SHOT,
    ("human", "Distribuição atual (area=quantidade):\n{distribution_summary}\n\nÁreas em EXCESSO (podem conter questões de outra área):\n{excess_areas}\n\nÁreas em DÉFICIT (candidatas naturais em caso de reclassificação):\n{deficit_areas}\n\nQuestões a revisar:\n{questions_json}"),
])
