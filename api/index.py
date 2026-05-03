import sys
import os

# Adiciona a raiz do projeto ao path para que os imports funcionem
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Handler para a Vercel (WSGI)
handler = app
