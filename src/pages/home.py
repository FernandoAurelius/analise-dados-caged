import streamlit as st
from typing import Callable


class HomePage:
    """
    Classe responsável pela página inicial da aplicação.
    
    Segue o princípio de responsabilidade única (S do SOLID),
    focando apenas na renderização da homepage.
    """
    
    def __init__(self) -> None:
        """
        Inicializa a página inicial com suas configurações.
        """
        pass
    
    def render(self) -> None:
        """
        Renderiza a página inicial da aplicação.
        """
        st.title('Análise de Dados do CAGED')
        
        st.markdown("""
        ## Bem-vindo ao Dashboard de Análise do CAGED
        
        Este dashboard permite a exploração e análise dos dados do **Cadastro Geral de Empregados e Desempregados (CAGED)**, 
        disponibilizados pelo Ministério da Economia.
        
        ### Sobre o CAGED
        
        O Cadastro Geral de Empregados e Desempregados (CAGED) foi instituído pela Lei nº 4.923, em 23 de dezembro de 1965.
        É uma fonte de informação de âmbito nacional e de periodicidade mensal, que registra as admissões e demissões de
        trabalhadores sob o regime da CLT.
        
        ### Funcionalidades Disponíveis
        
        - **Análise Exploratória**: Visualize dados e estatísticas do CAGED de forma interativa
        - **Algoritmo 1** *(Em desenvolvimento)*: Análise avançada dos dados usando algoritmo especializado
        - **Algoritmo 2** *(Em desenvolvimento)*: Outra abordagem de análise usando um algoritmo diferente
        
        ### Como Usar
        
        Utilize o menu lateral para navegar entre as diferentes seções do dashboard.
        Em cada seção, você encontrará controles interativos para filtrar e visualizar os dados de acordo com suas necessidades.
        """)
        
        st.image('https://www.gov.br/trabalho-e-emprego/pt-br/composicao/orgaos-especificos/secretaria-de-trabalho/imgs-st/banner-caged.png', 
                caption='Fonte: Ministério do Trabalho e Emprego', 
                use_column_width=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info('### Análise Exploratória', icon="📊")
            st.write("Explore visualizações e estatísticas dos dados do CAGED.")
            
        with col2:
            st.info('### Algoritmo 1', icon="🔍")
            st.write("Em desenvolvimento. Análise avançada será disponibilizada em breve.")
            
        with col3:
            st.info('### Algoritmo 2', icon="📈")
            st.write("Em desenvolvimento. Outra abordagem de análise será disponibilizada em breve.")
        
        st.markdown("---")
        
        st.markdown("""
        ### Fonte dos Dados
        
        Os dados utilizados neste dashboard são provenientes da **Base dos Dados**, que disponibiliza 
        os dados originais do Ministério da Economia.
        
        [Acesse o dataset na Base dos Dados](https://basedosdados.org/dataset/562b56a3-0b01-4735-a049-eeac5681f056?table=95106d6f-e36e-4fed-b8e9-99c41cd99ecf)
        """)
