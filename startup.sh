#!/bin/bash
echo "--- DEBUG INFO ---"
echo "Directorio actual (pwd): <span class="math-inline">\(pwd\)"
\# Paso 1\: Asegurarse de que tenemos un entorno virtual y activarlo
\# Oryx ya debería crear 'antenv' y activarlo, pero nos aseguramos
VIRTUAL\_ENV\_PATH\=</span>(pwd)/antenv
if [ ! -d "$VIRTUAL_ENV_PATH" ]; then
    echo "Creando entorno virtual en $VIRTUAL_ENV_PATH"
    python -m venv "$VIRTUAL_ENV_PATH"
fi

source "$VIRTUAL_ENV_PATH/bin/activate"
echo "Entorno virtual activado: $VIRTUAL_ENV_PATH"

# Paso 2: Instalar dependencias directamente con pip
echo "Instalando dependencias desde Pipfile.lock..."
# Esta línea le dice a pipenv que genere un requirements.txt basado en Pipfile.lock y luego pip lo instala
pip install -r <(pipenv lock --requirements)

# Paso 3: Configurar PYTHONPATH
export PYTHONPATH=<span class="math-inline">PYTHONPATH\:</span>(pwd)/SistemaCitasMedicas
echo "PYTHONPATH (final): $PYTHONPATH"

# Paso 4: Listar el contenido del entorno virtual para verificar Django
echo "Contenido de site-packages:"
ls -la "$VIRTUAL_ENV_PATH/lib/python3.11/site-packages/" | grep -i "django" # Busca la carpeta de Django

ls -la $(pwd)/ # lista el contenido de la raíz del despliegue
ls -la $(pwd)/SistemaCitasMedicas/ # Deberia listar wsgi.py, settings.py
echo "--- END DEBUG INFO ---"

# Iniciar Gunicorn con más verbosidad y un timeout más largo
gunicorn SistemaCitasMedicas.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 300 --log-level debug --access-logfile - --error-logfile -