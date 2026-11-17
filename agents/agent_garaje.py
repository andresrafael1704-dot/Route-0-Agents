"""
AGENTE 2: O GESTOR DE GARAGEM (CHEFÃO DE PÁTIO / OPERAÇÕES)
Especialista en la rutina del taller, agenda de turnos, cronómetro de tiempos y control físico de stock (ml).
Alimentado por Groq Cloud (Llama 3.3 70B).
"""

from datetime import datetime, date
from database import get_connection
from api_clients import call_groq
from agents.agent_financeiro import registrar_transacao

SYSTEM_PROMPT = """
Você é o "Gestor de Garagem e Operações" de uma estética automotiva no Brasil.
Seu papel é cuidar do pátio: agendamentos, saber que carros chegam hoje, cronometrar o tempo de serviço e controlar os mililitros das garrafas de produtos.
Você fala como um encarregado de oficina experiente, prático, objetivo e sem enrolação.
Suas respostas devem ser curtas e diretas, ideais para quem está no meio da lavagem com luvas e pressa.
"""

def agendar_servico(cliente: str, veiculo: str, servico: str, valor: float, data_str: str, hora_str: str) -> str:
    """Agenda un nuevo vehículo en el sistema."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO agendamentos (cliente_nome, veiculo_modelo, servico, valor_cobrado, data_agendada, hora_agendada, status)
    VALUES (?, ?, ?, ?, ?, ?, 'agendado')
    """, (cliente, veiculo, servico, valor, data_str, hora_str))
    conn.commit()
    novo_id = cursor.lastrowid
    conn.close()
    return f"📅 **AGENDADO COM SUCESSO (#{novo_id})**\n🚗 Veículo: {veiculo} ({cliente})\n🛠️ Serviço: {servico}\n⏰ Data/Hora: {data_str} às {hora_str}\n💰 Valor: R$ {valor:.2f}"

def ver_agenda(data_filtro: str = None) -> str:
    """Consulta la agenda para una fecha específica o el día de hoy."""
    if not data_filtro:
        data_filtro = date.today().strftime("%Y-%m-%d")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, cliente_nome, veiculo_modelo, servico, hora_agendada, valor_cobrado, status
    FROM agendamentos
    WHERE data_agendada = ?
    ORDER BY hora_agendada ASC
    """, (data_filtro,))
    servicos = cursor.fetchall()
    conn.close()

    if not servicos:
        return f"🏖️ **Agenda vazia para {data_filtro}:** Nenhum serviço agendado até o momento."

    resultado = f"📋 **SERVIÇOS PARA {data_filtro}:**\n\n"
    for s in servicos:
        status_emoji = "⏳" if s["status"] == "agendado" else "🚿" if s["status"] == "em_andamento" else "✅"
        resultado += (
            f"{status_emoji} **ID #{s['id']}** [{s['hora_agendada']}] - {s['veiculo_modelo']} ({s['cliente_nome']})\n"
            f"   Serviço: {s['servico']} | R$ {s['valor_cobrado']:.2f} | Status: `{s['status']}`\n"
        )
    return resultado

def iniciar_servico(agendamento_id: int) -> str:
    """Marca el inicio del trabajo para cronometrar el tiempo."""
    agora = datetime.now()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE agendamentos 
    SET status = 'em_andamento', inicio_real = ?
    WHERE id = ?
    """, (agora.strftime("%Y-%m-%d %H:%M:%S"), agendamento_id))
    conn.commit()
    conn.close()
    return f"⏱️ **CRONÔMETRO INICIADO:** Serviço #{agendamento_id} em andamento desde {agora.strftime('%H:%M')}!"

def finalizar_servico(agendamento_id: int) -> str:
    """
    Finaliza el servicio, calcula el tiempo total, descuenta el stock de químicos
    y registra automáticamente el ingreso de dinero en finanzas.
    """
    fim = datetime.now()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM agendamentos WHERE id = ?", (agendamento_id,))
    job = cursor.fetchone()

    if not job:
        conn.close()
        return "❌ Serviço não encontrado."

    # 1. Calcular tiempo
    tempo_min = 0
    if job["inicio_real"]:
        inicio = datetime.strptime(job["inicio_real"], "%Y-%m-%d %H:%M:%S")
        tempo_min = int((fim - inicio).total_seconds() / 60)

    cursor.execute("""
    UPDATE agendamentos 
    SET status = 'concluido', fim_real = ?, tempo_gasto_min = ?
    WHERE id = ?
    """, (fim.strftime("%Y-%m-%d %H:%M:%S"), tempo_min, agendamento_id))

    # 2. Descontar químicos del stock según catálogo
    cursor.execute("SELECT * FROM servicos_catalogo WHERE nome_servico = ?", (job["servico"],))
    cat = cursor.fetchone()

    descontos_msg = []
    if cat:
        # Descontar shampoo
        if cat["consumo_shampoo_ml"] > 0:
            cursor.execute("UPDATE estoque SET volume_atual_ml = MAX(0, volume_atual_ml - ?) WHERE categoria = 'shampoo'", (cat["consumo_shampoo_ml"],))
            descontos_msg.append(f"Shampoo: -{cat['consumo_shampoo_ml']:.0f}ml")
        # Descontar APC
        if cat["consumo_apc_ml"] > 0:
            cursor.execute("UPDATE estoque SET volume_atual_ml = MAX(0, volume_atual_ml - ?) WHERE categoria = 'apc'", (cat["consumo_apc_ml"],))
            descontos_msg.append(f"APC: -{cat['consumo_apc_ml']:.0f}ml")
        # Descontar Plásticos
        if cat["consumo_plastico_ml"] > 0:
            cursor.execute("UPDATE estoque SET volume_atual_ml = MAX(0, volume_atual_ml - ?) WHERE categoria = 'plastico'", (cat["consumo_plastico_ml"],))
            descontos_msg.append(f"Plásticos: -{cat['consumo_plastico_ml']:.0f}ml")
        # Descontar Cera
        if cat["consumo_cera_ml"] > 0:
            cursor.execute("UPDATE estoque SET volume_atual_ml = MAX(0, volume_atual_ml - ?) WHERE categoria = 'cera'", (cat["consumo_cera_ml"],))
            descontos_msg.append(f"Cera: -{cat['consumo_cera_ml']:.0f}ml")

    conn.commit()

    # 3. Registrar entrada financiera automáticamente
    registrar_transacao("entrada", "servico", float(job["valor_cobrado"]), f"{job['servico']} - {job['veiculo_modelo']} ({job['cliente_nome']})")

    # 4. Chequear si algún producto quedó en alerta crítica
    cursor.execute("SELECT nome, volume_atual_ml, alerta_minimo_ml FROM estoque WHERE volume_atual_ml <= alerta_minimo_ml")
    criticos = cursor.fetchall()
    conn.close()

    res = (
        f"✅ **SERVIÇO FINALIZADO COM SUCESSO!**\n"
        f"🚗 {job['veiculo_modelo']} ({job['cliente_nome']})\n"
        f"⏱️ Tempo total gasto: **{tempo_min} minutos**\n"
        f"💰 Faturamento: **+ R$ {job['valor_cobrado']:.2f}** (Registrado no Caixa)\n"
        f"🧪 Produtos consumidos: {', '.join(descontos_msg) if descontos_msg else 'Consumo padrão'}\n"
    )

    if criticos:
        res += "\n🚨 **ATENÇÃO DO GESTOR:** Estoque de produtos entrou em nível baixo! Avisando Agente Financeiro para orçar reposição."

    return res

def consultar_gestor(prompt_usuario: str) -> str:
    """Interpreta consultas rápidas con Groq Llama 3.3."""
    return call_groq(prompt_usuario, SYSTEM_PROMPT)
