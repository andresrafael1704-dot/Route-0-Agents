"""
AGENTE 1: O DIRETOR FINANCEIRO & COMPRADOR (CFO)
Especialista en flujo de caja, balance neto, costos fijos y rastreo de mejores precios en Brasil.
Alimentado por Google Gemini 2.0 Flash.
"""

from database import get_connection
from search_tools import cotizar_reposicion_insumo
from api_clients import call_gemini

SYSTEM_PROMPT = """
Você é o "Diretor Financeiro & Comprador (CFO)" de uma estética automotiva de garagem no Brasil.
Seu foco é 100% em DINHEIRO, MARGENS DE LUCRO, FLUXO DE CAIXA e ECONOMIA NAS COMPRAS.
Você é direto, preciso com números e sempre pensa no lucro líquido real do dono da oficina.
Quando responder:
1. Mostre os valores sempre em Reais (R$).
2. Separe o faturamento bruto do lucro limpo (descontando produtos, água, luz e insumos).
3. Seja transparente se uma despesa estiver muito alta ou se for hora de economizar.
"""

def registrar_transacao(tipo: str, categoria: str, valor: float, descricao: str) -> str:
    """Registra una entrada o salida en el flujo de caja."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO financeiro (tipo, categoria, valor, descricao)
    VALUES (?, ?, ?, ?)
    """, (tipo, categoria, valor, descricao))
    conn.commit()
    conn.close()
    
    simbolo = "💰 ENTRADA" if tipo == "entrada" else "💸 SAÍDA"
    return f"{simbolo} REGISTRADA: R$ {valor:.2f} | {descricao}"

def obtener_resumen_financiero() -> dict:
    """Calcula totales de ingresos, egresos y ganancia neta."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COALESCE(SUM(valor), 0) FROM financeiro WHERE tipo = 'entrada'")
    total_entradas = cursor.fetchone()[0]
    
    cursor.execute("SELECT COALESCE(SUM(valor), 0) FROM financeiro WHERE tipo = 'saida'")
    total_saidas = cursor.fetchone()[0]
    
    saldo_liquido = total_entradas - total_saidas
    
    # Últimas 5 transacciones
    cursor.execute("SELECT tipo, valor, descricao, data_registro FROM financeiro ORDER BY id DESC LIMIT 5")
    ultimas = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return {
        "entradas": total_entradas,
        "saidas": total_saidas,
        "saldo": saldo_liquido,
        "ultimas": ultimas
    }

def verificar_e_cotar_estoque_baixo() -> str:
    """
    Revisa si hay productos en nivel crítico y dispara la búsqueda de precios.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT nome, volume_atual_ml, alerta_minimo_ml, preco_pago 
    FROM estoque 
    WHERE volume_atual_ml <= alerta_minimo_ml
    """)
    produtos_criticos = cursor.fetchall()
    conn.close()

    if not produtos_criticos:
        return "✅ **Estoque Seguro:** Nenhum produto está abaixo do nível mínimo de reposição no momento."

    resposta = "🚨 **ALERTA DE COMPRAS - ESTOQUE CRÍTICO DETECTADO:**\n\n"
    for p in produtos_criticos:
        nome = p["nome"]
        atual = p["volume_atual_ml"]
        alerta = p["alerta_minimo_ml"]
        resposta += f"⚠️ **{nome}**: Restam apenas {atual:.0f}ml (Limite de alerta: {alerta:.0f}ml).\n"
        resposta += cotizar_reposicion_insumo(nome)
        resposta += "\n" + ("=" * 35) + "\n\n"

    return resposta

def consultar_cfo(pergunta_usuario: str) -> str:
    """Consulta abierta al Agente Financiero usando Gemini."""
    resumo = obtener_resumen_financiero()
    contexto = (
        f"Dados atuais da oficina:\n"
        f"- Faturamento total entradas: R$ {resumo['entradas']:.2f}\n"
        f"- Total de saídas/despesas: R$ {resumo['saidas']:.2f}\n"
        f"- Saldo em caixa atual: R$ {resumo['saldo']:.2f}\n\n"
        f"Pergunta do proprietário: {pergunta_usuario}"
    )
    return call_gemini(contexto, SYSTEM_PROMPT)
