"""
AGENTE 3: O ESTRATEGISTA DE CRESCIMENTO & FUTURO (CSO)
Especialista en proyectos de expansión, mudanza a local comercial, evaluación de nuevos servicios,
análisis de ROI y proyección de ganancias futuras.
Alimentado por DeepSeek-R1 / Gemini 2.0 Flash Thinking.
"""

from database import get_connection
from api_clients import call_deepseek
from agents.agent_financeiro import obtener_resumen_financiero

SYSTEM_PROMPT = """
Você é o "Diretor de Estratégia, Expansão e Crescimento (CSO)" de um negócio de estética automotiva no Brasil.
Seu trabalho é pensar grande, mas com os pés no chão.
Você analisa:
1. MUDANÇA DE PONTO: Quando sair da garagem de casa para um galpão/loja comercial (custos reais no Brasil: aluguel, seguro fiança, IPTU, água/luz comercial e a exigência ambiental da Caixa Separadora de Água e Óleo).
2. NOVOS SERVIÇOS E FERRAMENTAS: Avaliar se vale a pena comprar politriz roto-orbital (polimento), máquina extratora profissional ou gerador de ozônio (oxi-sanitização).
3. RETORNO DE INVESTIMENTO (ROI e Payback): Em quantos carros a máquina se paga.
4. PRÓS E CONTRAS HONESTOS: Nunca venda ilusão. Diga se o momento for arriscado.

Responda sempre com estrutura clara, números justificados e um veredito direto:
[VIABILIDADE: ALTA / MÉDIA / CRÍTICA]
[PONTO DE EQUILÍBRIO (BREAK-EVEN)]
[PRÓS E CONTRAS]
[RECOMENDAÇÃO PRÁTICA]
"""

def analisar_mudanca_ponto(aluguel_estimado: float, faturamento_atual: float) -> str:
    """
    Analiza la viabilidad económica y ambiental de mudarse a un local en Brasil.
    """
    # En Brasil, un alquiler comercial acarrea gastos fijos adicionales
    custo_fixo_adicional = (
        aluguel_estimado + 
        (aluguel_estimado * 0.15) +  # IPTU e taxas
        500.0 +                     # Água e Energia comercial
        150.0                       # Manutenção / seguro
    )
    
    prompt = (
        f"ANÁLISE DE MUDANÇA DA GARAGEM PARA PONTO COMERCIAL:\n"
        f"- Aluguel pretendido: R$ {aluguel_estimado:.2f}/mês\n"
        f"- Custo fixo mensal real estimado (com IPTU, energia/água comercial): R$ {custo_fixo_adicional:.2f}/mês\n"
        f"- Faturamento atual na garagem: R$ {faturamento_atual:.2f}/mês\n\n"
        f"Por favor, faça uma análise crítica de viabilidade considerando:\n"
        f"1. Quantos carros a mais por mês preciso fazer só para pagar o local novo.\n"
        f"2. Exigências obrigatórias no Brasil (como licença ambiental e caixa separadora).\n"
        f"3. Seu parecer estratégico: É hora de mudar ou melhor consolidar a garagem?"
    )
    return call_deepseek(prompt, SYSTEM_PROMPT)

def analisar_nova_ferramenta_ou_servico(nome_equipamento: str, custo_estimado: float, preco_medio_servico: float) -> str:
    """
    Calcula el Payback y ROI de incorporar una nueva máquina o servicio (ej: politriz, ozônio).
    """
    prompt = (
        f"AVALIAÇÃO DE NOVO EQUIPAMENTO / SERVIÇO:\n"
        f"- Equipamento / Serviço pretendido: {nome_equipamento}\n"
        f"- Custo de investimento: R$ {custo_estimado:.2f}\n"
        f"- Preço que pretendo cobrar por serviço: R$ {preco_medio_servico:.2f}\n\n"
        f"Faça o cálculo de ROI e Payback:\n"
        f"1. Em quantos carros o equipamento se paga totalmente (Payback).\n"
        f"2. Custo de insumos por serviço e esforço físico necessário.\n"
        f"3. Prós e contras de adicionar esse serviço na garagem de casa agora.\n"
        f"4. Veredito final: Comprar já ou esperar?"
    )
    return call_deepseek(prompt, SYSTEM_PROMPT)

def consulta_estrategica_livre(pergunta_usuario: str) -> str:
    """Consulta abierta de visión de futuro y crecimiento."""
    resumo = obtener_resumen_financiero()
    
    # Contar servicios realizados hasta hoy
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM agendamentos WHERE status = 'concluido'")
    total_carros = cursor.fetchone()[0]
    conn.close()

    contexto = (
        f"CONTEXTO ATUAL DO NEGÓCIO:\n"
        f"- Total de carros atendidos no histórico: {total_carros}\n"
        f"- Faturamento bruto acumulado: R$ {resumo['entradas']:.2f}\n"
        f"- Saldo em caixa disponível: R$ {resumo['saldo']:.2f}\n\n"
        f"PERGUNTA ESTRATÉGICA DO PROPRIETÁRIO: {pergunta_usuario}"
    )
    return call_deepseek(contexto, SYSTEM_PROMPT)
