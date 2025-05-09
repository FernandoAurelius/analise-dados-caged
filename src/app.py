import streamlit as st
import os
from src.data.data_loader import DataLoader
from src.data.data_processor import DataProcessor
from src.pages.home import HomePage
from src.pages.exploratory import ExploratoryPage
from src.pages.algorithm1 import Algorithm1Page
from src.pages.algorithm2 import Algorithm2Page
from typing import Dict, Callable


class CAGEDApp:
    """
    Classe principal da aplicação Streamlit para análise de dados do CAGED.
    
    Implementa um padrão de design semelhante ao padrão Strategy para gerenciar diferentes páginas.
    """
    
    def __init__(self) -> None:
        """
        Inicializa a aplicação principal.
        """
        # Configuração da aplicação Streamlit
        self._config_streamlit()
        
        # Inicializa componentes de dados
        self.data_loader = DataLoader(project_id=st.secrets["PROJECT_ID"])
        self.data_processor = DataProcessor()
        
        # Inicializa páginas
        self.pages = {
            "Início": HomePage(),
            "Análise Exploratória": ExploratoryPage(self.data_loader, self.data_processor),
            "Algoritmo 1 - Análise Preditiva": Algorithm1Page(),
            "Algoritmo 2 - Agrupamento e Segmentação": Algorithm2Page()
        }
    
    def _config_streamlit(self) -> None:
        """
        Configura as definições do Streamlit.
        """
        st.set_page_config(
            page_title="Análise de Dados do CAGED",
            page_icon="📊",
            layout="wide",
            initial_sidebar_state="expanded",
        )
        
        # CSS personalizado
        st.markdown("""
        <style>
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        h1, h2, h3 {
            color: #1E88E5;
        }
        .stButton button {
            background-color: #1E88E5;
            color: white;
        }
        .stProgress .st-bo {
            background-color: #1E88E5;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def run(self) -> None:
        """
        Executa a aplicação Streamlit.
        """
        # Título no sidebar
        st.sidebar.title("Navegação")
        
        # Seleção de página no sidebar
        selection = st.sidebar.radio("Ir para", list(self.pages.keys()))
        
        # Informações sobre o projeto
        st.sidebar.markdown("---")
        st.sidebar.info(
            "Este dashboard foi desenvolvido para análise exploratória de dados "
            "do CAGED (Cadastro Geral de Empregados e Desempregados)."
        )
        
        # Exibe a página selecionada
        page = self.pages[selection]

        try:
            st.write(f"SECRET_TEST: {st.secrets['PROJECT_ID'][:3]}...")
            st.success("Secrets estão configurados corretamente!")
        except Exception as e:  
            st.error(f"Erro ao acessar secrets: {e}")
        page.render()


if __name__ == "__main__":
    app = CAGEDApp()
    app.run()
