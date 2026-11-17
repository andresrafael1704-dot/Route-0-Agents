#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# SCRIPT DE INSTALACIÓN RÁPIDA PARA TERMUX (POCO X4 GT / ANDROID)
# ==============================================================================

echo "🚀 Iniciando instalación del sistema de agentes en Termux..."

# 1. Mantener despierto el procesador (evita que MIUI / HyperOS suspenda el bot)
echo "🔋 Activando Wake-Lock para ejecución continua en segundo plano..."
termux-wake-lock

# 2. Actualizar paquetes básicos de Termux
echo "📦 Actualizando repositorios e instalando Python..."
pkg update -y
pkg install -y python git

# 3. Instalar librerías de Python requeridas
echo "🐍 Instalando dependencias de Python ultra-ligeras..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Verificar archivo de configuración .env
if [ ! -f .env ]; then
    echo "⚠️ Creando archivo .env a partir de .env.example..."
    cp .env.example .env
    echo "📝 Por favor, edita el archivo .env con tus claves: nano .env"
else
    echo "✅ Archivo .env ya existente."
fi

# 5. Inicializar la base de datos SQLite
echo "🗄️ Inicializando base de datos SQLite..."
python database.py

echo ""
echo "🎉 ¡TODO LISTO! Para arrancar tus agentes, ejecuta:"
echo "   python bot.py"
echo ""
