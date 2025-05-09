import sys
import os

# Adiciona o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa a aplicação principal
from src.app import CAGEDApp

# Executa a aplicação
if __name__ == "__main__":
    app = CAGEDApp()
    app.run()
