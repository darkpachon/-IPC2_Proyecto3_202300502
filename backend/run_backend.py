import subprocess
import sys
import os

def run_backend():
    """Ejecuta el backend Flask"""
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    subprocess.run([sys.executable, 'app.py'])

if __name__ == '__main__':
    run_backend()