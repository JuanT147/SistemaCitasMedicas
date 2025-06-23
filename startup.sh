#!/bin/bash

# Aseguramos que el script sea ejecutable y que Gunicorn use el PORT de Azure
# Primero, cambiamos al directorio donde Oryx ha desempaquetado nuestra aplicación.
# Esta ruta temporal la podemos obtener de la variable de entorno ORYX_BUILD_SOURCE
# o directamente de los logs que nos muestran '/tmp/8ddb1f1dce72680' como App path.
# Lo más seguro es usar el directorio de trabajo actual que es donde el startup.sh se ejecuta.

# Añadir el directorio actual (que será /tmp/xxxxxx/ donde está manage.py) al PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Iniciar Gunicorn
# $PORT es una variable de entorno inyectada por Azure
gunicorn SistemaCitasMedicas.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120