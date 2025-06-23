#!/bin/bash

# Cambiar al directorio raíz de tu aplicación desplegada
# Azure ya se encarga de esto con 'cd /home/site/wwwroot' en su appCommandLine,
# pero es una buena práctica incluirlo si controlamos el inicio.
# En tu caso, tu proyecto 'SistemaCitasMedicas' ya está en /home/site/wwwroot.

# Configurar PYTHONPATH para que Python encuentre tu aplicación Django
# /home/site/wwwroot/ es la raíz de tu proyecto desplegado.
export PYTHONPATH=$PYTHONPATH:/home/site/wwwroot/

# Opcional: Recolectar archivos estáticos (si no lo hiciste en GitHub Actions)
# python manage.py collectstatic --noinput

# Opcional: Realizar migraciones de base de datos (si no lo hiciste en GitHub Actions)
# python manage.py migrate

# Iniciar Gunicorn
# $PORT es una variable de entorno inyectada por Azure que contiene el puerto a escuchar
gunicorn SistemaCitasMedicas.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120