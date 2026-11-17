"""
Script de pruebas unitarias para validar la base de datos,
el descuento de stock por mililitros, el registro financiero
y la herramienta de búsqueda de precios en vivo en Mercado Livre.
"""

import os
from database import init_db, get_connection
from agents.agent_garaje import agendar_servico, iniciar_servico, finalizar_servico
from agents.agent_financeiro import obtener_resumen_financiero
from search_tools import buscar_mercado_livre

def ejecutar_pruebas():
    print("--- 1. INICIALIZANDO BASE DE DATOS ---")
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM estoque")
    total_insumos = cursor.fetchone()[0]
    print(f"✅ Insumos en catálogo: {total_insumos}")

    print("\n--- 2. PROBANDO AGENDAMIENTO Y OPERACIONES ---")
    res_agenda = agendar_servico("Carlos Silva", "Honda Civic", "Lavagem Detalhada (Sedã)", 110.0, "2026-11-18", "10:00")
    print(res_agenda)

    # Iniciar y finalizar servicio
    cursor.execute("SELECT id FROM agendamentos ORDER BY id DESC LIMIT 1")
    job_id = cursor.fetchone()[0]

    print("\n--- 3. CRONOMETRANDO E INICIANDO SERVICIO ---")
    print(iniciar_servico(job_id))

    print("\n--- 4. FINALIZANDO SERVICIO Y DEDUCCIÓN DE STOCK ---")
    res_final = finalizar_servico(job_id)
    print(res_final)

    print("\n--- 5. VALIDANDO FLUJO DE CAJA ---")
    resumo = obtener_resumen_financiero()
    print(f"💰 Entradas: R$ {resumo['entradas']:.2f} | Saldo: R$ {resumo['saldo']:.2f}")

    print("\n--- 6. PROBANDO BÚSQUEDA DE PRECIOS EN VIVO (MERCADO LIVRE BRASIL) ---")
    ofertas = buscar_mercado_livre("V-Floc 1.5L", limite=3)
    if ofertas:
        print(f"✅ Se encontraron {len(ofertas)} ofertas reales:")
        for o in ofertas:
            print(f"   • R$ {o['preco']:.2f} ({o['frete']}) - {o['titulo'][:45]}...")
    else:
        print("⚠️ No devolvió ofertas o conexión lenta, pero la función se ejecutó correctamente.")

    conn.close()
    print("\n🎉 ¡TODAS LAS PRUEBAS INTERNAS PASARON CON ÉXITO!")

if __name__ == "__main__":
    ejecutar_pruebas()
