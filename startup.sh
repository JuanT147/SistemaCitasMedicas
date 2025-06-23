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
# Paso 2: Asegurar que pipenv esté disponible (ya se instaló, pero es una buena práctica)
pip install pipenv
# Paso 3: Generar requirements.txt desde Pipfile.lock y luego instalarlo
echo "Generando requirements.txt desde Pipfile.lock e instalando dependencias..."
# Redirigir la salida de 'pipenv requirements' a un archivo temporal y luego instalarlo con pip
pipenv requirements > requirements.txt
pip install -r requirements.txt
# Paso 4: Configurar PYTHONPATH (esto ya lo tenías y es correcto)
export PYTHONPATH=$PYTHONPATH:$(pwd)/SistemaCitasMedicas
echo "PYTHONPATH (final): $PYTHONPATH"
# Paso 5: Listar el contenido del entorno virtual para verificar Django
# Esto es para depuración y deberías ver 'django' listado
echo "Verificando instalación de Django en site-packages:"
ls -la "$VIRTUAL_ENV_PATH/lib/python3.11/site-packages/" | grep -i "django"
echo "--- FIN DEBUG INFO DE INSTALACIÓN ---"
# === PASO CRÍTICO: APLICAR MIGRACIONES DE DJANGO ===
echo "Aplicando migraciones de Django..."
python SistemaCitasMedicas/manage.py makemigrations --noinput
python SistemaCitasMedicas/manage.py migrate --noinput
echo "Migraciones de Django aplicadas."
# =========================================================================
# === PASO PARA CREAR SUPERUSUARIO (TEMPORAL) ===
echo "Creando superusuario de Django (si no existe)..."
# Usa variables de entorno para el nombre de usuario y contraseña para no hardcodearlos
# Asegúrate de configurar DJANGO_SUPERUSER_USERNAME y DJANGO_SUPERUSER_PASSWORD
# como variables de entorno en Azure App Service -> Configuración -> Configuración de la aplicación
python SistemaCitasMedicas/manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email admin@example.com || true
# La parte "|| true" es para que el script no falle si el superusuario ya existe.
echo "Intento de creación de superusuario finalizado."
# =========================================================================
# Iniciar Gunicorn con más verbosidad y un timeout más largo
echo "Iniciando Gunicorn..."
gunicorn SistemaCitasMedicas.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 300 --log-level debug --access-logfile - --error-logfile -
echo "El script startup.sh ha finalizado."