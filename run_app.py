import os
import subprocess
import webbrowser
import time
import sys
from pathlib import Path

def run():
    print("🚀 Iniciando ScriptDNA...")
    
    # Directorio base
    base_dir = Path(__file__).resolve().parent
    
    # 1. Verificar entorno virtual
    venv_path = base_dir / "backend" / "venv"
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
        
    if not python_exe.exists():
        print(f"❌ Error: No se encontró el entorno virtual en {venv_path}")
        print("Por favor, ejecuta primero: bash setup_local.sh")
        return

    # 2. Comando para iniciar uvicorn
    # Usamos el python del venv para asegurar que tiene las dependencias
    cmd = [
        str(python_exe), 
        "-m", "uvicorn", 
        "backend.main:app", 
        "--host", "127.0.0.1", 
        "--port", "8000",
        "--reload"
    ]
    
    print("🔗 Servidor iniciándose en http://127.0.0.1:8000")
    
    # 3. Abrir navegador después de un pequeño delay
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://127.0.0.1:8000/app")
        print("🌍 Navegador abierto.")

    # Iniciar el proceso del servidor
    try:
        # Abrimos el navegador en un hilo separado o simplemente antes si no bloquea
        # En Python, el servidor bloquea, así que podemos intentar abrirlo justo antes de lanzar el subproceso
        # o usar un pequeño delay.
        
        # Lanzar el servidor
        print("📡 Accede a la App en: http://127.0.0.1:8000/app")
        
        # En macOS/Linux, podemos lanzar el navegador y luego el servidor
        if sys.platform != "win32":
            subprocess.Popen(["sleep 2 && open http://127.0.0.1:8000/app"], shell=True)
        
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 ScriptDNA detenido por el usuario.")
    except Exception as e:
        print(f"❌ Error al iniciar el servidor: {e}")

if __name__ == "__main__":
    run()
