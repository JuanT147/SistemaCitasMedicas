#!/bin/bash

echo "--- DEBUG INFO ---"
echo "Directorio actual (pwd): $(pwd)"

# Paso 1: Asegurarse de que tenemos un entorno virtual y activarlo
# Oryx ya debería crear 'antenv' y activarlo, pero nos aseguramos
VIRTUAL_ENV_PATH=$(pwd)/antenv
if [ ! -d "$VIRTUAL_ENV_PATH" ]; then
    echo "Creando entorno virtual en $VIRTUAL_ENV_PATH"
    python -m venv "$VIRTUAL_ENV_PATH"
fi

# Activar el entorno virtual. Esto es crucial para que 'pip' y 'pipenv' operen dentro de él.
source "$VIRTUAL_ENV_PATH/bin/activate"
echo "Entorno virtual activado: $VIRTUAL_ENV_PATH"

# Paso 2: Asegurar que pipenv esté disponible para generar los requirements
# Aunque Oryx suele tenerlo, una instalación preventiva no hace daño
pip install pipenv

# Paso 3: Instalar dependencias directamente con pip usando Pipfile.lock
echo "Instalando dependencias desde Pipfile.lock..."
# pipenv lock --requirements genera un archivo requirements.txt temporal que pip instala
pip install -r <(pipenv lock --requirements)

# Paso 4: Configurar PYTHONPATH (esto ya lo tenías y es correcto)
export PYTHONPATH=$PYTHONPATH:$(pwd)/SistemaCitasMedicas
echo "PYTHONPATH (final): $PYTHONPATH"

# Paso 5: Listar el contenido del entorno virtual para verificar Django
# Esto es para depuración y deberías ver 'django' listado
echo "Verificando instalación de Django en site-packages:"
ls -la "$VIRTUAL_ENV_PATH/lib/python3.11/site-packages/" | grep -i "django"
echo "--- FIN DEBUG INFO DE INSTALACIÓN ---"

# Iniciar Gunicorn con más verbosidad y un timeout más largo
echo "Iniciando Gunicorn..."
gunicorn SistemaCitasMedicas.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 300 --log-level debug --access-logfile - --error-logfile -

echo "El script startup.sh ha finalizado."