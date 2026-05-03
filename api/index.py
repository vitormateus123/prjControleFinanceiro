import sys
import os

# Garante que a raiz do projeto esteja no path
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

from app import app

# Handler WSGI para a Vercel
handler = app
