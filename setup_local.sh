#!/bin/bash

# ScriptDNA: Instalador Local (macOS)
# Este script prepara el entorno para que el equipo pueda correr la app localmente.

echo "🚀 Iniciando instalación de ScriptDNA..."

# 1. Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado. Instálalo desde python.org o usa 'brew install python'"
    exit 1
fi

# 2. Crear Entorno Virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual (venv)..."
    python3 -m venv venv
fi

# 3. Activar entorno e instalar dependencias
echo "📥 Instalando dependencias de Python..."
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# 4. Verificar FFmpeg (Crítico para video/audio)
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️ ADVERTENCIA: FFmpeg no detectado."
    echo "FFmpeg es necesario para extraer audio de videos."
    echo "Sugerencia: Ejecuta 'brew install ffmpeg' si tienes Homebrew."
else
    echo "✅ FFmpeg detectado."
fi

# 5. Crear archivo .env si no existe
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env base..."
    echo "GEMINI_API_KEY=" > .env
    echo "INSFORGE_BASE_URL=" >> .env
    echo "INSFORGE_ANON_KEY=" >> .env
    echo "VAULT_ROOT=./Vault" >> .env
    echo "Configura tus claves en el archivo .env antes de empezar."
fi

echo "✅ Instalación completada."
echo "👉 Para iniciar la app, ejecuta: python3 run_app.py"
