import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from src.data.data_loader import DataLoader
from src.data.data_processor import DataProcessor
from src.visualization.plots import PlotGenerator


class ExploratoryPage:
    """
    Classe responsável pela página de análise exploratória de dados.
    
    Segue o princípio de responsabilidade única (S do SOLID),
    focando apenas na renderização e lógica da página de análise exploratória.
    """
    
    def __init__(self, data_loader: DataLoader, data_processor: DataProcessor) -> None:
        """
        Inicializa a página de análise exploratória.
        
        Args:
            data_loader: Instância de DataLoader para carregar os dados
            data_processor: Instância de DataProcessor para processar os dados
        """
        self.data_loader = data_loader
        self.data_processor = data_processor
        self.plot_generator = PlotGenerator()
        
        # Define tipos de gráficos disponíveis
        self.available_charts = {
            "Série Temporal": "time_series",
            "Gráfico de Barras": "bar_chart",
            "Gráfico de Pizza": "pie_chart",
            "Histograma": "histogram",
            "Boxplot": "boxplot",
            "Mapa de Calor": "heatmap",
            "Gráfico de Dispersão": "scatter_plot"
        }

    def render(self) -> None:
        """
        Renderiza a página de análise exploratória.
        """
        st.title("Análise Exploratória")
        
        # Configuração de filtros de dados
        st.write("## Configuração de Filtros")
        
        with st.expander("Filtros de Dados", expanded=True):
            col1, col2, col3 = st.columns(3) # Adicionado col3 para o botão de limpar
            
            with col1:
                # Filtro de ano
                years = list(range(2020, 2023))
                selected_year = st.selectbox("Selecione o Ano", options=years, index=0)
                
                # Filtro de estado (UF)
                states = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
                         'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 
                         'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
                selected_state = st.selectbox("Selecione o Estado (UF)", options=['Todos'] + states, index=0)
            
            with col2:
                # Filtro de mês
                months = [(1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
                         (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'), 
                         (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')]
                month_options = [m[1] for m in months]
                selected_month_name = st.selectbox("Selecione o Mês", options=['Todos'] + month_options, index=0)
                
                # Filtro de limite de linhas
                row_limit = st.number_input("Limite de Linhas", min_value=100, max_value=10000, value=1000, step=100)

            with col3: # Coluna para botões de ação
                st.write("") # Espaçador para alinhar
                st.write("") # Espaçador para alinhar
                if st.button("Carregar Dados", key="load_data"):
                    # Preparação dos parâmetros para consulta
                    location = {}
                    filters = {}
                    
                    # Converte o mês selecionado de nome para número
                    selected_month = None
                    if selected_month_name != 'Todos':
                        for m in months:
                            if m[1] == selected_month_name:
                                selected_month = m[0]
                                break
                    
                    # Adiciona filtro de UF se não for 'Todos'
                    if selected_state != 'Todos':
                        location['uf'] = selected_state
                    
                    with st.spinner("Carregando dados do CAGED..."):
                        # Carrega os dados com base nos filtros selecionados
                        df = self.data_loader.load_caged_data(
                            year=selected_year, 
                            month=selected_month,
                            location=location,
                            filters=filters,
                            limit=row_limit
                        )
                        
                        # Processa os dados carregados
                        if not df.empty:
                            processed_df = self.data_processor.process_data(df)
                            
                            # Armazena os dados processados na sessão para uso em outras partes
                            st.session_state['caged_data'] = processed_df
                            
                            # Mostra informações sobre os dados carregados
                            st.success(f"Dados carregados com sucesso! {len(processed_df)} registros encontrados.")
                            # st.rerun() # Força o rerender para exibir os dados imediatamente
                        else:
                            st.error("Não foi possível carregar os dados. Verifique os filtros e tente novamente.")
                            if 'caged_data' in st.session_state:
                                del st.session_state['caged_data'] # Limpa dados antigos se o carregamento falhar
                
                if st.button("Limpar Dados e Filtros", key="clear_data"):
                    if 'caged_data' in st.session_state:
                        del st.session_state['caged_data']
                    st.info("Dados e filtros limpos. Configure e carregue novos dados.")
                    st.rerun()

        # Verifica se os dados estão na sessão e os exibe
        if 'caged_data' in st.session_state and not st.session_state['caged_data'].empty:
            processed_df = st.session_state['caged_data']
            
            # Renderiza a visualização de dados
            self._render_data_view(processed_df)
            
            # Seção de visualizações
            self._render_visualizations(processed_df)
        elif 'caged_data' in st.session_state and st.session_state['caged_data'].empty:
            st.warning("Os filtros aplicados não retornaram dados. Tente carregar com filtros diferentes.")
        else:
            st.info("Configure os filtros e clique em 'Carregar Dados' para iniciar a análise.")

    def _render_visualizations(self, df: pd.DataFrame) -> None:
        """
        Renderiza a seção de visualizações e gráficos.
        
        Args:
            df: DataFrame processado com os dados
        """
        if df.empty:
            return
        
        st.write("## Visualizações")
        
        chart_type = st.selectbox(
            "Selecione o tipo de gráfico", 
            options=list(self.available_charts.keys())
        )
        
        # Configurações específicas para cada tipo de gráfico
        chart_method = self.available_charts[chart_type]
        
        if chart_method == "time_series":
            # Configurações para série temporal
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            
            if 'data' in df.columns and len(numeric_cols) > 0:
                y_column = st.selectbox("Selecione a coluna para o eixo Y", options=numeric_cols)
                group_by_option = st.selectbox(
                    "Agrupar por (opcional)", 
                    options=['Nenhum'] + df.select_dtypes(include=['object', 'category']).columns.tolist()
                )
                
                group_by = None if group_by_option == 'Nenhum' else group_by_option
                
                # Gera o gráfico de série temporal
                fig = self.plot_generator.create_time_series(df, y_column=y_column, group_by=group_by)
                self.plot_generator.streamlit_display(fig)
            else:
                st.warning("Dados insuficientes para gráfico de série temporal. É necessário uma coluna de data e pelo menos uma coluna numérica.")
        
        elif chart_method == "bar_chart":
            # Configurações para gráfico de barras
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            
            if len(categorical_cols) > 0:
                x_column = st.selectbox("Selecione a coluna para o eixo X", options=categorical_cols)
                
                y_options = ['Contagem'] + numeric_cols
                y_selection = st.selectbox("Selecione a coluna para o eixo Y", options=y_options)
                
                y_column = None if y_selection == 'Contagem' else y_selection
                
                group_by_option = st.selectbox(
                    "Agrupar por (opcional)", 
                    options=['Nenhum'] + [col for col in categorical_cols if col != x_column]
                )
                
                group_by = None if group_by_option == 'Nenhum' else group_by_option
                
                orientation = st.radio("Orientação", options=["Vertical", "Horizontal"])
                
                # Gera o gráfico de barras
                fig = self.plot_generator.create_bar_chart(
                    df, 
                    x_column=x_column, 
                    y_column=y_column, 
                    group_by=group_by,
                    orientation='v' if orientation == "Vertical" else 'h'
                )
                self.plot_generator.streamlit_display(fig)
            else:
                st.warning("Dados insuficientes para gráfico de barras. É necessário pelo menos uma coluna categórica.")
        
        elif chart_method == "pie_chart":
            # Configurações para gráfico de pizza
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            
            if len(categorical_cols) > 0:
                column = st.selectbox("Selecione a coluna para segmentar", options=categorical_cols)
                
                values_options = ['Contagem'] + numeric_cols
                values_selection = st.selectbox("Selecione a coluna de valores", options=values_options)
                
                values = None if values_selection == 'Contagem' else values_selection
                
                # Gera o gráfico de pizza
                fig = self.plot_generator.create_pie_chart(df, column=column, values=values)
                self.plot_generator.streamlit_display(fig)
            else:
                st.warning("Dados insuficientes para gráfico de pizza. É necessário pelo menos uma coluna categórica.")
        
        elif chart_method == "histogram":
            # Configurações para histograma
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            
            if len(numeric_cols) > 0:
                column = st.selectbox("Selecione a coluna para o histograma", options=numeric_cols)
                
                bins = st.slider("Número de bins", min_value=5, max_value=100, value=30)
                
                categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                group_by_option = st.selectbox(
                    "Agrupar por (opcional)", 
                    options=['Nenhum'] + categorical_cols
                )
                
                group_by = None if group_by_option == 'Nenhum' else group_by_option
                
                # Gera o histograma
                fig = self.plot_generator.create_histogram(df, column=column, bins=bins, group_by=group_by)
                self.plot_generator.streamlit_display(fig)
            else:
                st.warning("Dados insuficientes para histograma. É necessário pelo menos uma coluna numérica.")
        
        elif chart_method == "boxplot":
            # Configurações para boxplot
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if len(numeric_cols) > 0:
                y_column = st.selectbox("Selecione a coluna numérica (eixo Y)", options=numeric_cols)
                
                x_options = ['Nenhum'] + categorical_cols
                x_selection = st.selectbox("Selecione a coluna categórica (eixo X, opcional)", options=x_options)
                
                x_column = None if x_selection == 'Nenhum' else x_selection
                
                # Gera o boxplot
                fig = self.plot_generator.create_boxplot(df, y_column=y_column, x_column=x_column)
                self.plot_generator.streamlit_display(fig)
            else:
                st.warning("Dados insuficientes para boxplot. É necessário pelo menos uma coluna numérica.")
        
        elif chart_method == "heatmap":
            # Configurações para mapa de calor
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            
            if len(numeric_cols) >= 2:
                selected_columns = st.multiselect(
                    "Selecione as colunas para o mapa de calor", 
                    options=numeric_cols,
                    default=numeric_cols[:min(5, len(numeric_cols))]
                )
                
                # Gera o mapa de calor
                if selected_columns and len(selected_columns) >= 2:
                    fig = self.plot_generator.create_heatmap(df, columns=selected_columns)
                    self.plot_generator.streamlit_display(fig)
                else:
                    st.warning("Selecione pelo menos duas colunas para gerar o mapa de calor.")
            else:
                st.warning("Dados insuficientes para mapa de calor. São necessárias pelo menos duas colunas numéricas.")
        
        elif chart_method == "scatter_plot":
            # Configurações para gráfico de dispersão
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
            
            if len(numeric_cols) >= 2:
                x_column = st.selectbox("Selecione a coluna para o eixo X", options=numeric_cols)
                y_column = st.selectbox(
                    "Selecione a coluna para o eixo Y", 
                    options=[col for col in numeric_cols if col != x_column]
                )
                
                all_cols = df.columns.tolist()
                color_by_option = st.selectbox(
                    "Colorir por (opcional)", 
                    options=['Nenhum'] + all_cols
                )
                
                size_by_option = st.selectbox(
                    "Tamanho por (opcional)", 
                    options=['Nenhum'] + numeric_cols
                )
                
                color_by = None if color_by_option == 'Nenhum' else color_by_option
                size_by = None if size_by_option == 'Nenhum' else size_by_option
                
                # Gera o gráfico de dispersão
                fig = self.plot_generator.create_scatter_plot(
                    df, 
                    x_column=x_column, 
                    y_column=y_column, 
                    color_by=color_by,
                    size_by=size_by
                )
                self.plot_generator.streamlit_display(fig)
            else:
                st.warning("Dados insuficientes para gráfico de dispersão. São necessárias pelo menos duas colunas numéricas.")

    def _render_data_view(self, df: pd.DataFrame) -> None:
        """
        Renderiza a seção de visualização dos dados brutos.
        
        Args:
            df: DataFrame processado com os dados
        """
        st.subheader("Visualização dos Dados")
        
        # Filtro de colunas
        if not df.empty:
            all_columns = df.columns.tolist()
            selected_columns = st.multiselect(
                "Selecione as colunas para visualizar", 
                options=all_columns,
                default=all_columns[:min(8, len(all_columns))]
            )
            
            if selected_columns:
                st.dataframe(df[selected_columns])
            else:
                st.dataframe(df)
            
            # Estatísticas descritivas
            st.write("### Estatísticas Descritivas")
            
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            if not numeric_cols.empty:
                st.dataframe(df[numeric_cols].describe())
            else:
                st.info("Não há colunas numéricas para calcular estatísticas descritivas.")
                
            # Informações de valores nulos
            st.write("### Valores Ausentes")
            
            null_counts = df.isnull().sum()
            null_percentages = (df.isnull().mean() * 100).round(2)
            
            null_df = pd.DataFrame({
                'Contagem de Nulos': null_counts,
                'Percentual de Nulos (%)': null_percentages
            })
            
            st.dataframe(null_df)
            
            # Download dos dados
            st.write("### Download dos Dados")
            
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download como CSV",
                data=csv,
                file_name="caged_data.csv",
                mime="text/csv",
            )
        else:
            st.error("Não há dados para exibir.")
