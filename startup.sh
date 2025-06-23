#!/bin/bash

# Este script se ejecutará desde la raíz de la aplicación desplegada por Oryx.
# En Azure, la raíz de la app desplegada es /tmp/xxxxxxx/.
# Aquí, la carpeta 'SistemaCitasMedicas' (con settings.py) es una subcarpeta directa.

# Añadir la raíz del proyecto al PYTHONPATH para que Python encuentre 'SistemaCitasMedicas'.
# `$(pwd)/` se refiere al directorio actual, que en Azure será la raíz del despliegue.
export PYTHONPATH=$PYTHONPATH:$(pwd)/SistemaCitasMedicas

# --- Líneas para depuración (¡Muy importantes ahora!) ---
echo "--- DEBUG INFO ---"
echo "Directorio actual (pwd): $(pwd)"
echo "PYTHONPATH (después de añadir): $PYTHONPATH"
ls -la $(pwd)/ # Lista el contenido de la raíz del despliegue
ls -la $(pwd)/SistemaCitasMedicas/ # Debería listar wsgi.py, settings.py
echo "--- END DEBUG INFO ---"
# --------------------------------------------------------

# Iniciar Gunicorn.
# 'SistemaCitasMedicas.wsgi' se refiere al módulo Python (SistemaCitasMedicas/wsgi.py).
# Como la raíz del proyecto (donde está la carpeta SistemaCitasMedicas/) está en PYTHONPATH,
# Python lo encontrará correctamente.
gunicorn SistemaCitasMedicas.wsgi --bind 0.0.0.0:$PORT --workers 2 --timeout 120