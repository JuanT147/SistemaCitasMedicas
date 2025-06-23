#!/bin/bash

# Ruta donde Oryx desempaqueta tu aplicación.
# En tu caso, es /tmp/8ddb1f2f8995e19 o similar.
# La variable $APP_PATH ya debería contener esto en el entorno de Azure.
# Si no, $(pwd) debería ser /tmp/xxxxxx.

# Añadir la raíz de tu proyecto al PYTHONPATH de forma explícita.
# Asegurémonos de que el directorio donde manage.py está (y donde reside la carpeta SistemaCitasMedicas)
# sea incluido en PYTHONPATH.
export PYTHONPATH="/usr/local/python/site-packages:$PYTHONPATH:$(pwd)"

# Puedes añadir un print para depurar y ver el PYTHONPATH actual
# echo "PYTHONPATH después de setear: $PYTHONPATH"

# Iniciar Gunicorn
# $PORT es una variable de entorno inyectada por Azure
gunicorn SistemaCitasMedicas.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120