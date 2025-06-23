#!/bin/bash

echo "--- DEBUG INFO ---"
echo "Directorio actual (pwd): $(pwd)"

# Asegurarse que pipenv esté disponible
pip install pipenv

echo "Instalando o verificando dependencias con pipenv install --system --deploy --ignore-pipfile..."
pipenv install --system --deploy --ignore-pipfile || { echo "ERROR: Falló la instalación de dependencias." >&2; exit 1; }
echo "Fin de instalación de dependencias."

# Configurar PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)/SistemaCitasMedicas
echo "PYTHONPATH (final): $PYTHONPATH"

# Aplicar migraciones de Django
echo "Aplicando migraciones de Django..."
python manage.py migrate --noinput || { echo "ERROR: Fallaron las migraciones." >&2; exit 1; }
echo "Migraciones de Django aplicadas."

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos de Django..."
python manage.py collectstatic --noinput || { echo "ERROR: Falló collectstatic." >&2; exit 1; }
echo "Archivos estáticos recolectados."

# Iniciar Gunicorn
echo "Iniciando Gunicorn..."
gunicorn SistemaCitasMedicas.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 300 --log-level debug --access-logfile - --error-logfile - || { echo "ERROR: Falló el inicio de Gunicorn." >&2; exit 1; }

echo "El script startup.sh ha finalizado."