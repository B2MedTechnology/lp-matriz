"""Verificador de fatos: a 2ª IA confere se o texto afirma sobre o cliente algo que ele nunca disse.
Calibrado na rodada 6 (28-09): a versão literal acusou 45 "fatos" — quase tudo paráfrase — e piorou a página.
Aqui só conta o que o paciente poderia COBRAR da clínica e que os insumos não sustentam."""
import json

CAMPOS_VERIFICADOS = ["NUMEROS", "QUEM_HEAD", "MOTIVOS", "CORPO_LEAD", "CORPO_CLINICO", "GRUPOS", "FILTRO", "PASSOS",
                      "SALA_HEAD", "SALA_TEXTO", "FAQ", "PAGINA_PRINCIPAL"]

SISTEMA = """Você é o VERIFICADOR DE FATOS da agência. Recebe os INSUMOS de um cliente (briefing, perfil público) e o CONTEÚDO
de uma landing page. Aponte SÓ promessas ou fatos NOVOS sobre o cliente — algo que um paciente poderia cobrar da clínica
e que os insumos NÃO sustentam nem de forma resumida.

APONTE (exemplos): política que ninguém disse (nota fiscal para reembolso, parcelamento, desconto, encaixe no mesmo dia);
serviço, exame, técnica ou público que não aparece (atende crianças, cirurgia refrativa, sem pontos, cola biológica);
número sem fonte (anos, cirurgias, cidades, médicos, preço diferente do dito); pessoa, cargo ou registro inventado;
"feito no mesmo dia" quando os insumos não dizem; promessa de resultado ou de segurança.
Em GRUPOS, cada card é [título, ícone, texto, etiquetas]: aponte o card cujo ÍCONE (o nome já diz o assunto: holep, vasectomia,
catarata/lio, retina…) NÃO corresponde ao título — a foto do card mostraria outra coisa.

NÃO APONTE: paráfrase, resumo ou sinônimo de algo dos insumos; título/etiqueta/nome curto ("O Instituto", "Atendimento
somente particular" quando os insumos dizem que não atende convênio); explicação geral de doença, exame ou procedimento
(o que é catarata, o que a tomografia mostra, qual condição um exame investiga); o termo de busca; o texto da mensagem de
WhatsApp; horários, endereço e telefones dos FATOS FIXOS; nota e total do Google (podem vir dos fatos fixos OU do perfil
público — valem os dois); o agendamento pelo WhatsApp (é o canal da página); dizer que o valor é informado pelo WhatsApp antes do agendamento; adjetivo vago (outro revisor cuida disso).

Na dúvida, NÃO aponte. Uma página com 0 a 5 achados é o normal.
Responda JSON {"achados": [{"campo": "...", "trecho": "...", "por_que": "..."}]}."""

def checar_fatos(conteudo, insumos, fixos, chamar, ler, modelo="google/gemini-2.5-pro"):
    tx = {k: conteudo[k] for k in CAMPOS_VERIFICADOS if k in conteudo}
    m = [{"role": "system", "content": SISTEMA},
         {"role": "user", "content": "INSUMOS:\n" + insumos + "\n\nFATOS FIXOS:\n" + fixos + "\n\nCONTEÚDO:\n"
          + json.dumps(tx, ensure_ascii=False, indent=0)}]
    r = chamar(m, modelo)
    u = r.get("usage") or {}
    custo = u.get("cost") or (u.get("cost_details") or {}).get("upstream_inference_cost") or 0
    try:
        return json.loads(ler(r)[0]).get("achados", []), custo
    except Exception:
        return [], custo
