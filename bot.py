"""
BOT PRINCIPAL DE TELEGRAM: SISTEMA MULTI-AGENTE PARA ESTÉTICA AUTOMOTRIZ
Diseñado para ejecutarse en Termux (Poco X4 GT) con consumo mínimo de batería y memoria.
"""

import os
import sys
import subprocess
import telebot
from telebot import types
from dotenv import load_dotenv

from database import init_db, get_connection
from agents.agent_financeiro import (
    obtener_resumen_financiero, 
    registrar_transacao, 
    verificar_e_cotar_estoque_baixo, 
    consultar_cfo
)
from agents.agent_garaje import (
    agendar_servico, 
    ver_agenda, 
    iniciar_servico, 
    finalizar_servico, 
    consultar_gestor
)
from agents.agent_estratega import (
    analisar_mudanca_ponto, 
    analisar_nova_ferramenta_ou_servico, 
    consulta_estrategica_livre
)

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

if not TOKEN:
    print("⚠️ AVISO: TELEGRAM_BOT_TOKEN no configurado en .env.")
    # Permitir importar sin crashear para pruebas unitarias
    bot = telebot.TeleBot("DUMMY_TOKEN")
else:
    bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

# Inicializar Base de Datos al arrancar
init_db()

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_agenda = types.KeyboardButton("📋 Agenda de Hoje")
    btn_caixa = types.KeyboardButton("💰 Caixa & Lucro")
    btn_compras = types.KeyboardButton("🛒 Checar Estoque & Compras")
    btn_futuro = types.KeyboardButton("🚀 Painel Estratégico")
    markup.add(btn_agenda, btn_caixa, btn_compras, btn_futuro)
    return markup

@bot.message_handler(commands=['start', 'menu'])
def cmd_start(message):
    texto = (
        "🚗💨 **BEM-VINDO AO SEU TIME DE AGENTES DE ESTÉTICA AUTOMOTIVA!**\n\n"
        "Seus 3 agentes estão a postos no seu Poco X4 GT:\n\n"
        "1. 📋 **Gestor de Garagem:** Agenda, cronômetro e mililitros de estoque.\n"
        "2. 💰 **Diretor Financeiro:** Entradas, saídas e caçador de ofertas no Brasil.\n"
        "3. 🚀 **Estrategista de Futuro:** Mudança para ponto comercial, ROI e expansão.\n\n"
        "Use os botões abaixo ou mande comandos rápidos!"
    )
    bot.send_message(message.chat.id, texto, reply_markup=get_main_keyboard())

# ==================== COMANDOS DO GESTOR DE GARAGEM ====================

@bot.message_handler(func=lambda m: m.text == "📋 Agenda de Hoje")
@bot.message_handler(commands=['hoje'])
def cmd_agenda_hoje(message):
    resposta = ver_agenda()
    bot.send_message(message.chat.id, resposta)

@bot.message_handler(commands=['agendar'])
def cmd_agendar(message):
    """
    Formato: /agendar Cliente | Modelo | Servico | Valor | Data(YYYY-MM-DD) | Hora(HH:MM)
    Exemplo: /agendar João | Onix Prata | Lavagem Detalhada (Hatch) | 90.0 | 2026-11-18 | 09:00
    """
    try:
        dados = message.text.replace("/agendar", "").strip().split("|")
        if len(dados) < 6:
            bot.reply_to(message, "❌ Formato incorreto!\nUse: `/agendar Cliente | Modelo | Servico | Valor | YYYY-MM-DD | HH:MM`")
            return
        
        cliente, modelo, servico, valor_str, data_str, hora_str = [d.strip() for d in dados]
        valor = float(valor_str)
        res = agendar_servico(cliente, modelo, servico, valor, data_str, hora_str)
        bot.send_message(message.chat.id, res)
    except Exception as e:
        bot.reply_to(message, f"❌ Erro ao agendar: {str(e)}")

@bot.message_handler(commands=['iniciar'])
def cmd_iniciar(message):
    """Exemplo: /iniciar 1"""
    try:
        job_id = int(message.text.split()[1])
        res = iniciar_servico(job_id)
        bot.send_message(message.chat.id, res)
    except:
        bot.reply_to(message, "❌ Use: `/iniciar [ID_DO_SERVIÇO]` (Ex: `/iniciar 1`)")

@bot.message_handler(commands=['finalizar'])
def cmd_finalizar(message):
    """Exemplo: /finalizar 1"""
    try:
        job_id = int(message.text.split()[1])
        res = finalizar_servico(job_id)
        bot.send_message(message.chat.id, res)
    except:
        bot.reply_to(message, "❌ Use: `/finalizar [ID_DO_SERVIÇO]` (Ex: `/finalizar 1`)")

# ==================== COMANDOS DO DIRETOR FINANCEIRO ====================

@bot.message_handler(func=lambda m: m.text == "💰 Caixa & Lucro")
@bot.message_handler(commands=['caixa'])
def cmd_caixa(message):
    resumo = obtener_resumen_financiero()
    texto = (
        "📊 **RESUMO DO FLUXO DE CAIXA ATUAL:**\n\n"
        f"💵 **Total Entradas:** R$ {resumo['entradas']:.2f}\n"
        f"💸 **Total Saídas:** R$ {resumo['saidas']:.2f}\n"
        f"💎 **Saldo Líquido:** R$ {resumo['saldo']:.2f}\n\n"
        "📜 **Últimas movimentações:**\n"
    )
    for u in resumo['ultimas']:
        sinal = "+" if u['tipo'] == 'entrada' else "-"
        texto += f"• `{u['data_registro'][:10]}`: {sinal}R$ {u['valor']:.2f} ({u['descricao']})\n"
    
    bot.send_message(message.chat.id, texto)

@bot.message_handler(commands=['gasto'])
def cmd_gasto(message):
    """
    Registrar una despesa/saída rápida.
    Exemplo: /gasto 45.0 | Pano de microfibra e fita
    """
    try:
        dados = message.text.replace("/gasto", "").strip().split("|")
        valor = float(dados[0].strip())
        desc = dados[1].strip() if len(dados) > 1 else "Despesa operacional"
        res = registrar_transacao("saida", "custo_operacional", valor, desc)
        bot.send_message(message.chat.id, res)
    except:
        bot.reply_to(message, "❌ Use: `/gasto [VALOR] | [DESCRIÇÃO]` (Ex: `/gasto 50.0 | Luz da oficina`)")

@bot.message_handler(func=lambda m: m.text == "🛒 Checar Estoque & Compras")
@bot.message_handler(commands=['compras'])
def cmd_compras(message):
    bot.send_message(message.chat.id, "🔎 *O Agente Financeiro está escaneando seu estoque e checando o Mercado Livre...*")
    res = verificar_e_cotar_estoque_baixo()
    bot.send_message(message.chat.id, res)

# ==================== COMANDOS DO ESTRATEGISTA ====================

@bot.message_handler(func=lambda m: m.text == "🚀 Painel Estratégico")
@bot.message_handler(commands=['estrategia'])
def cmd_estrategia(message):
    texto = (
        "🚀 **PAINEL DO ESTRATEGISTA DE EXPANSÃO (CSO)**\n\n"
        "Como posso ajudar o crescimento do seu negócio hoje?\n\n"
        "1. 🏬 **Simular Mudança para Ponto Comercial:**\n"
        "   Use: `/mudanca [VALOR_ALUGUEL]` (Ex: `/mudanca 2500`)\n\n"
        "2. 🛠️ **Avaliar Nova Máquina ou Serviço (ROI):**\n"
        "   Use: `/investir [EQUIPAMENTO] | [CUSTO] | [PREÇO_SERVIÇO]`\n"
        "   (Ex: `/investir Politriz Roto-Orbital | 1200 | 350`)\n\n"
        "3. 🧠 **Pergunta Livre de Futuro:**\n"
        "   Use: `/futuro [SUA DÚVIDA]`"
    )
    bot.send_message(message.chat.id, texto)

@bot.message_handler(commands=['mudanca'])
def cmd_mudanca(message):
    try:
        aluguel = float(message.text.replace("/mudanca", "").strip())
        resumo = obtener_resumen_financiero()
        bot.send_message(message.chat.id, "🧠 *DeepSeek / Gemini Thinking está calculando os cenários tributários, ambientais e de ponto de equilíbrio...*")
        res = analisar_mudanca_ponto(aluguel, resumo['entradas'])
        bot.send_message(message.chat.id, res)
    except:
        bot.reply_to(message, "❌ Use: `/mudanca [VALOR_DO_ALUGUEL]` (Ex: `/mudanca 2000`)")

@bot.message_handler(commands=['investir'])
def cmd_investir(message):
    try:
        dados = message.text.replace("/investir", "").strip().split("|")
        equip, custo_str, preco_str = [d.strip() for d in dados]
        custo = float(custo_str)
        preco = float(preco_str)
        bot.send_message(message.chat.id, f"🧠 *Analisando Payback e Viabilidade para: {equip}...*")
        res = analisar_nova_ferramenta_ou_servico(equip, custo, preco)
        bot.send_message(message.chat.id, res)
    except:
        bot.reply_to(message, "❌ Use: `/investir Equipamento | Custo | Preço_Cobrado` (Ex: `/investir Gerador de Ozônio | 400 | 100`)")

@bot.message_handler(commands=['futuro'])
def cmd_futuro(message):
    pergunta = message.text.replace("/futuro", "").strip()
    if not pergunta:
        bot.reply_to(message, "❌ Escreva sua dúvida após `/futuro`. Ex: `/futuro vale a pena contratar um ajudante de meio período?`")
        return
    bot.send_message(message.chat.id, "🧠 *Consultando o Estrategista de Crescimento...*")
    res = consulta_estrategica_livre(pergunta)
    bot.send_message(message.chat.id, res)

# ==================== SISTEMA DE AUTO-ATUALIZAÇÃO (GITHUB) ====================

@bot.message_handler(commands=['update'])
def cmd_update(message):
    """
    Descarga los últimos cambios de GitHub en el Poco X4 GT y reinicia el bot automáticamente.
    """
    msg_espera = bot.send_message(message.chat.id, "🔄 **Verificando e baixando atualizações do GitHub...**")
    try:
        resultado = subprocess.run(
            ["git", "pull"], 
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        saida = resultado.stdout.strip() or resultado.stderr.strip()
        
        if "Already up to date" in saida or "Já atualizado" in saida:
            bot.edit_message_text("✅ **O bot já está na versão mais recente!** Nenhuma alteração pendente.", chat_id=message.chat.id, message_id=msg_espera.message_id)
            return

        bot.edit_message_text(f"🚀 **Atualização aplicada com sucesso!**\n\n```\n{saida}\n```\n\n🔄 Reiniciando agentes agora...", chat_id=message.chat.id, message_id=msg_espera.message_id)
        
        # Reiniciar el script en Python
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        bot.edit_message_text(f"❌ **Erro ao atualizar via Git:** {str(e)}", chat_id=message.chat.id, message_id=msg_espera.message_id)

# ==================== ROTEADOR INTELIGENTE (TEXTO LIVRE) ====================

@bot.message_handler(func=lambda m: True)
def router_texto_livre(message):
    texto = message.text.lower()
    
    # Roteamento básico por intenção
    if any(palavra in texto for palavra in ["hoje", "agenda", "carro", "lavar", "iniciar", "terminar", "tempo"]):
        # Rota para Agente 2 (Gestor de Garagem)
        res = consultar_gestor(message.text)
        bot.reply_to(message, f"📋 **[Gestor de Garagem]:**\n\n{res}")
    elif any(palavra in texto for palavra in ["dinheiro", "caixa", "lucro", "faturamento", "gasto", "comprar", "preço", "custo"]):
        # Rota para Agente 1 (Financiero)
        res = consultar_cfo(message.text)
        bot.reply_to(message, f"💰 **[Diretor Financeiro]:**\n\n{res}")
    else:
        # Rota para Agente 3 (Estratega)
        res = consulta_estrategica_livre(message.text)
        bot.reply_to(message, f"🚀 **[Estrategista de Futuro]:**\n\n{res}")

if __name__ == "__main__":
    print("🤖 Bot de Estética Automotiva iniciado com sucesso!")
    print("Aguardando mensagens do Telegram...")
    bot.infinity_polling()
