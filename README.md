# 🚗💨 Sistema Multi-Agente para Estética Automotiva
### Operación Garaje en Poco X4 GT (Termux) | 100% Costo-Beneficio

Sistema integral de gestión de operaciones, finanzas y estrategia a futuro para estética automotriz en Brasil, diseñado para ejecutarse localmente en un smartphone Android (**Poco X4 GT** o similar) mediante **Termux**, utilizando una arquitectura multi-API optimizada para gastar prácticamente **R$ 0,00**.

---

## 👥 Tu Equipo de Agentes

| Agente | Rol | Especialidad | API / Modelo |
| :--- | :--- | :--- | :--- |
| **💰 1. Diretor Financeiro (CFO)** | Finanzas & Compras | Control de caja, costos fijos y variables, balance neto y **rastreador de ofertas en Mercado Livre Brasil y Shopee** cuando falta producto. | **Google Gemini 2.0 Flash** *(Free Tier en Google AI Studio)* |
| **📋 2. Gestor de Garagem (COO)** | Operaciones & Taller | Agenda de turnos, cronómetro de tiempos por auto, control de mililitros en botellas y alertas de stock bajo. | **Groq Cloud (Llama 3.3 70B)** *(Free Tier ultra-rápido)* |
| **🚀 3. Estrategista de Futuro (CSO)** | Crecimiento & Expansión | Simulación de mudanza a local comercial (con cálculo de agua/luz comercial y caja separadora de agua/aceite), evaluación de nuevos servicios (pulido, vitrificado, ozono) y cálculo de Payback/ROI. | **DeepSeek-R1** *(o Gemini Flash Thinking gratuito)* |

---

## 📱 Guía de Instalación en tu Poco X4 GT (Paso a Paso)

### Paso 1: Instalar Termux
1. En tu teléfono, descarga e instala **Termux** (se recomienda descargarlo desde [F-Droid](https://f-droid.org/en/packages/com.termux/) para tener la versión más actualizada y estable).
2. Abre Termux y dale permisos de almacenamiento si lo requieres:
   ```bash
   termux-setup-storage
   ```

### Paso 2: Copiar o Clonar el Proyecto
Puedes transferir esta carpeta `estetica_automotiva_ai` a la memoria interna de tu teléfono o clonarla:
```bash
cd ~
git clone <URL_DE_TU_REPOSITORIO> estetica_automotiva_ai
cd estetica_automotiva_ai
```
*(O si copiaste la carpeta a Downloads de tu teléfono: `cp -r /sdcard/Download/estetica_automotiva_ai ~/`)*

### Paso 3: Ejecutar el Instalador Automático
Dentro de la carpeta en Termux, simplemente ejecuta:
```bash
chmod +x setup_termux.sh
./setup_termux.sh
```
El script activará el `termux-wake-lock` (para que Xiaomi/MIUI no suspenda el bot con la pantalla apagada), instalará Python, las librerías ligeras e inicializará la base de datos `garagem.db`.

---

## 🔑 Configurar tus Claves Gratuitas (`.env`)

Edita el archivo `.env` en Termux con `nano .env`:

1. **`TELEGRAM_BOT_TOKEN`**:
   * Abre Telegram en tu teléfono y busca `@BotFather`.
   * Envía `/newbot`, ponle nombre (ej. `GarajeDetalleBot`) y usuario (ej. `garaje_detalle_bot`).
   * Copia el token que te da y pégalo aquí.
2. **`GEMINI_API_KEY`**:
   * Entra en [Google AI Studio](https://aistudio.google.com/) con tu cuenta de Google.
   * Ve a "Get API key" -> "Create API key" (100% gratis).
3. **`GROQ_API_KEY`**:
   * Entra en [Groq Console](https://console.groq.com/) e inicia sesión con Google.
   * Ve a "API Keys" -> "Create API Key" (100% gratis).
4. **`DEEPSEEK_API_KEY` (Opcional)**:
   * Si lo dejas vacío, el sistema usará automáticamente Gemini Thinking gratis para el Estratega.

---

## 🚀 Poner en Marcha el Sistema

En Termux, ejecuta:
```bash
python bot.py
```
¡Listo! Abre Telegram, busca tu bot y presiona **/start**.

---

## 🛠️ Comandos Principales en Telegram

### 📋 Operaciones & Garaje (Agente 2)
* `📋 Agenda de Hoje` o `/hoje`: Ver autos del día.
* `/agendar Cliente | Modelo | Servico | Valor | YYYY-MM-DD | HH:MM`:
  * *Ejemplo:* `/agendar Marcos | Civic Preto | Lavagem Detalhada (Sedã) | 110.0 | 2026-11-18 | 09:30`
* `/iniciar [ID]`: Comienza a cronometrar el servicio. *(Ej: `/iniciar 1`)*
* `/finalizar [ID]`: Detiene el cronómetro, descuenta los mililitros de químicos del stock e ingresa automáticamente el dinero en caja.

### 💰 Finanzas & Compras (Agente 1)
* `💰 Caixa & Lucro` o `/caixa`: Resumen de entradas, salidas y margen neto.
* `/gasto [VALOR] | [MOTIVO]`: Registra un egreso. *(Ej: `/gasto 35.0 | Pano de microfibra`)*
* `🛒 Checar Estoque & Compras` o `/compras`: Escanea el nivel de los frascos y, si alguno está bajo, consulta en vivo las ofertas más baratas con flete gratis en Mercado Livre Brasil y Shopee.

### 🚀 Estrategia & Futuro (Agente 3)
* `🚀 Painel Estratégico` o `/estrategia`: Menú de opciones de crecimiento.
* `/mudanca [VALOR_ALUGUEL]`: Simula mudarse de la casa a un local comercial. *(Ej: `/mudanca 2200`)*
* `/investir [EQUIPO] | [COSTO] | [PRECIO_COBRADO]`: Evalúa en cuántos autos recuperas la inversión de una máquina. *(Ej: `/investir Politriz Roto-Orbital | 1200 | 350`)*
* `/futuro [PREGUNTA]`: Consulta libre sobre contratación, nuevos servicios o visión del negocio.

### 🔄 Mantenimiento y Actualizaciones (Desde Telegram)
* `/update`: Descarga automáticamente los últimos cambios de GitHub y reinicia el bot sin tocar el teléfono.

