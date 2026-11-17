"""
Módulo de Base de Datos SQLite para la Estética Automotriz.
Diseñado para ser ultra-ligero y ejecutarse sin problemas en Termux (Android / Poco X4 GT).
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "garagem.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Tabla de Inventario de Químicos (Estoque Físico)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        marca TEXT,
        categoria TEXT, -- shampoo, apc, plastico, cera, etc.
        volume_total_ml REAL NOT NULL,
        volume_atual_ml REAL NOT NULL,
        alerta_minimo_ml REAL NOT NULL,
        preco_pago REAL NOT NULL,
        data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Catálogo de Servicios y Receta de Consumo (Ficha Técnica)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS servicos_catalogo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_servico TEXT NOT NULL UNIQUE,
        preco_padrao REAL NOT NULL,
        tempo_estimado_min INTEGER NOT NULL,
        consumo_shampoo_ml REAL DEFAULT 20.0,
        consumo_apc_ml REAL DEFAULT 15.0,
        consumo_plastico_ml REAL DEFAULT 10.0,
        consumo_cera_ml REAL DEFAULT 15.0
    )
    """)

    # 3. Agenda de Turnos y Control de Tiempos en Taller
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_nome TEXT NOT NULL,
        veiculo_modelo TEXT NOT NULL,
        servico TEXT NOT NULL,
        valor_cobrado REAL NOT NULL,
        data_agendada TEXT NOT NULL, -- YYYY-MM-DD
        hora_agendada TEXT NOT NULL, -- HH:MM
        status TEXT DEFAULT 'agendado', -- agendado, em_andamento, concluido, cancelado
        inicio_real TIMESTAMP,
        fim_real TIMESTAMP,
        tempo_gasto_min INTEGER,
        observacoes TEXT
    )
    """)

    # 4. Flujo Financiero (Caja, Ingresos y Gastos)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL, -- entrada, saida
        categoria TEXT NOT NULL, -- servico, compra_insumo, custo_fixo, outros
        valor REAL NOT NULL,
        descricao TEXT NOT NULL,
        data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    # Cargar datos iniciales si está vacía
    cursor.execute("SELECT COUNT(*) FROM servicos_catalogo")
    if cursor.fetchone()[0] == 0:
        _seed_datos_iniciales(cursor)
        conn.commit()

    conn.close()

def _seed_datos_iniciales(cursor):
    # Servicios comunes en estética automotriz en Brasil
    servicos = [
        ("Lavagem Detalhada (Hatch)", 90.0, 120, 20.0, 15.0, 10.0, 15.0),
        ("Lavagem Detalhada (Sedã)", 110.0, 140, 25.0, 20.0, 12.0, 18.0),
        ("Lavagem Detalhada (SUV/Picape)", 140.0, 160, 35.0, 25.0, 18.0, 25.0),
        ("Higienização Interna Completa", 180.0, 180, 0.0, 60.0, 15.0, 0.0),
        ("Combo Completo (Detalhada + Interiores)", 250.0, 240, 25.0, 60.0, 15.0, 20.0),
        ("Revitalização / Proteção de Plásticos", 70.0, 45, 0.0, 10.0, 20.0, 0.0)
    ]
    cursor.executemany("""
    INSERT INTO servicos_catalogo 
    (nome_servico, preco_padrao, tempo_estimado_min, consumo_shampoo_ml, consumo_apc_ml, consumo_plastico_ml, consumo_cera_ml)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, servicos)

    # Insumos iniciales típicos (Vonixx / marcas de Brasil)
    estoque_inicial = [
        ("V-Floc Shampoo 1.5L", "Vonixx", "shampoo", 1500.0, 1500.0, 200.0, 48.90),
        ("Sintra Pro Limpador 1.2L", "Vonixx", "apc", 1200.0, 1200.0, 150.0, 39.90),
        ("Restaurax Restaurador de Plásticos 500ml", "Vonixx", "plastico", 500.0, 500.0, 80.0, 38.50),
        ("Blend Cera Líquida 500ml", "Vonixx", "cera", 500.0, 500.0, 80.0, 49.90)
    ]
    cursor.executemany("""
    INSERT INTO estoque 
    (nome, marca, categoria, volume_total_ml, volume_atual_ml, alerta_minimo_ml, preco_pago)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, estoque_inicial)

if __name__ == "__main__":
    init_db()
    print("Base de datos SQLite inicializada exitosamente.")
