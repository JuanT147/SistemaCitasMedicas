# SistemaCitasMedicas/startup.sh

#!/bin/bash

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Realizar migraciones de base de datos
python manage.py migrate

# Iniciar Gunicorn
gunicorn SistemaCitasMedicas.wsgi --bind 0.0.0.0:$PORT --workers 4