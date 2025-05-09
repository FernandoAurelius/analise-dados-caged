import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional, Tuple, Any, Union
import streamlit as st


class PlotGenerator:
    """
    Classe responsável por gerar visualizações para os dados do CAGED.
    
    Implementa o princípio de responsabilidade única (S do SOLID),
    focando apenas na geração de gráficos e visualizações.
    """
    
    def __init__(self) -> None:
        """
        Inicializa o gerador de gráficos com configurações padrão.
        """
        # Configuração de aparência para gráficos do matplotlib/seaborn
        sns.set(style="whitegrid")
        self.color_palette = sns.color_palette("viridis", 10)
        self.title_fontsize = 16
        self.label_fontsize = 12
        
        # Mapeamentos para legendas mais descritivas
        self.column_labels = {
            'ano': 'Ano',
            'mes': 'Mês',
            'uf': 'UF',
            'idade': 'Idade',
            'sexo': 'Sexo',
            'sexo_desc': 'Sexo',
            'grau_instrucao': 'Grau de Instrução',
            'grau_instrucao_desc': 'Grau de Instrução',
            'cbo_2002': 'Ocupação (CBO)',
            'categoria': 'Categoria do Trabalhador',
            'subclasse_cnae_2': 'Setor Econômico (CNAE)',
            'salario': 'Salário',
            'tipo_movimentacao': 'Tipo de Movimentação',
            'tipo_movimentacao_desc': 'Tipo de Movimentação',
            'tipo_estabelecimento': 'Tipo de Estabelecimento',
            'faixa_etaria': 'Faixa Etária',
            'faixa_salarial': 'Faixa Salarial'
        }
    
    def create_time_series(self, df: pd.DataFrame, 
                          y_column: str, 
                          x_column: str = 'data',
                          group_by: Optional[str] = None) -> go.Figure:
        """
        Cria um gráfico de série temporal.
        
        Args:
            df: DataFrame processado
            y_column: Coluna para o eixo Y
            x_column: Coluna para o eixo X (padrão é 'data')
            group_by: Coluna opcional para agrupar os dados
            
        Returns:
            Figura Plotly com o gráfico de série temporal
        """
        if x_column not in df.columns or y_column not in df.columns:
            # Retorna um gráfico vazio se as colunas não existirem
            fig = go.Figure()
            fig.update_layout(title="Dados não disponíveis para gráfico de série temporal")
            return fig
        
        title = f'{self.column_labels.get(y_column, y_column)} ao longo do tempo'
        
        if group_by and group_by in df.columns:
            fig = px.line(df, x=x_column, y=y_column, color=group_by, 
                         title=title,
                         labels={
                             x_column: self.column_labels.get(x_column, x_column),
                             y_column: self.column_labels.get(y_column, y_column),
                             group_by: self.column_labels.get(group_by, group_by)
                         })
        else:
            fig = px.line(df, x=x_column, y=y_column, 
                         title=title,
                         labels={
                             x_column: self.column_labels.get(x_column, x_column),
                             y_column: self.column_labels.get(y_column, y_column)
                         })
        
        fig.update_layout(
            xaxis_title=self.column_labels.get(x_column, x_column),
            yaxis_title=self.column_labels.get(y_column, y_column),
            legend_title=self.column_labels.get(group_by, group_by) if group_by else None,
            hovermode="x unified"
        )
        
        return fig
    
    def create_bar_chart(self, df: pd.DataFrame, 
                        x_column: str, 
                        y_column: Optional[str] = None,
                        group_by: Optional[str] = None,
                        orientation: str = 'v',
                        sort_by: Optional[str] = None) -> go.Figure:
        """
        Cria um gráfico de barras.
        
        Args:
            df: DataFrame processado
            x_column: Coluna para o eixo X
            y_column: Coluna para o eixo Y (se None, conta ocorrências de x_column)
            group_by: Coluna opcional para agrupar os dados
            orientation: Orientação do gráfico ('v' para vertical, 'h' para horizontal)
            sort_by: Coluna para ordenar os dados
            
        Returns:
            Figura Plotly com o gráfico de barras
        """
        if x_column not in df.columns:
            fig = go.Figure()
            fig.update_layout(title="Dados não disponíveis para gráfico de barras")
            return fig
        
        # Se y_column não for fornecido, usa contagem
        if y_column is None:
            if group_by and group_by in df.columns:
                chart_data = df.groupby([x_column, group_by]).size().reset_index(name='count')
                y_column = 'count'
            else:
                chart_data = df.groupby(x_column).size().reset_index(name='count')
                y_column = 'count'
        else:
            if y_column not in df.columns:
                fig = go.Figure()
                fig.update_layout(title=f"Coluna {y_column} não disponível para gráfico de barras")
                return fig
            
            if group_by and group_by in df.columns:
                chart_data = df.groupby([x_column, group_by])[y_column].mean().reset_index()
            else:
                chart_data = df.copy()
        
        # Ordenar dados se necessário
        if sort_by:
            if sort_by in chart_data.columns:
                chart_data = chart_data.sort_values(by=sort_by)
        
        # Título com base nas colunas selecionadas
        if y_column == 'count':
            title = f'Contagem de {self.column_labels.get(x_column, x_column)}'
        else:
            title = f'{self.column_labels.get(y_column, y_column)} por {self.column_labels.get(x_column, x_column)}'
        
        # Criar gráfico com base na orientação
        if orientation == 'h':  # Horizontal
            if group_by and group_by in df.columns:
                fig = px.bar(chart_data, y=x_column, x=y_column, color=group_by, orientation='h',
                            title=title,
                            labels={
                                x_column: self.column_labels.get(x_column, x_column),
                                y_column: self.column_labels.get(y_column, y_column),
                                group_by: self.column_labels.get(group_by, group_by)
                            })
            else:
                fig = px.bar(chart_data, y=x_column, x=y_column, orientation='h',
                            title=title,
                            labels={
                                x_column: self.column_labels.get(x_column, x_column),
                                y_column: self.column_labels.get(y_column, y_column)
                            })
        else:  # Vertical
            if group_by and group_by in df.columns:
                fig = px.bar(chart_data, x=x_column, y=y_column, color=group_by,
                            title=title,
                            labels={
                                x_column: self.column_labels.get(x_column, x_column),
                                y_column: self.column_labels.get(y_column, y_column),
                                group_by: self.column_labels.get(group_by, group_by)
                            })
            else:
                fig = px.bar(chart_data, x=x_column, y=y_column,
                            title=title,
                            labels={
                                x_column: self.column_labels.get(x_column, x_column),
                                y_column: self.column_labels.get(y_column, y_column)
                            })
        
        return fig
    
    def create_pie_chart(self, df: pd.DataFrame, 
                        column: str, 
                        values: Optional[str] = None) -> go.Figure:
        """
        Cria um gráfico de pizza.
        
        Args:
            df: DataFrame processado
            column: Coluna para segmentar o gráfico
            values: Coluna com valores para cada segmento (se None, usa contagem)
            
        Returns:
            Figura Plotly com o gráfico de pizza
        """
        if column not in df.columns:
            fig = go.Figure()
            fig.update_layout(title="Dados não disponíveis para gráfico de pizza")
            return fig
        
        if values is not None and values not in df.columns:
            fig = go.Figure()
            fig.update_layout(title=f"Coluna {values} não disponível para gráfico de pizza")
            return fig
        
        # Prepara os dados para o gráfico
        if values is None:
            # Conta a frequência de cada categoria
            chart_data = df[column].value_counts().reset_index()
            chart_data.columns = [column, 'count']
            values = 'count'
            title = f'Distribuição de {self.column_labels.get(column, column)}'
        else:
            # Agrega os valores para cada categoria
            chart_data = df.groupby(column)[values].sum().reset_index()
            title = f'Soma de {self.column_labels.get(values, values)} por {self.column_labels.get(column, column)}'
        
        fig = px.pie(chart_data, names=column, values=values, 
                    title=title)
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig
    
    def create_histogram(self, df: pd.DataFrame, 
                        column: str, 
                        bins: Optional[int] = None,
                        group_by: Optional[str] = None) -> go.Figure:
        """
        Cria um histograma.
        
        Args:
            df: DataFrame processado
            column: Coluna para o histograma
            bins: Número de bins (caixas)
            group_by: Coluna opcional para agrupar os dados
            
        Returns:
            Figura Plotly com o histograma
        """
        if column not in df.columns:
            fig = go.Figure()
            fig.update_layout(title="Dados não disponíveis para histograma")
            return fig
        
        title = f'Distribuição de {self.column_labels.get(column, column)}'
        
        if group_by and group_by in df.columns:
            fig = px.histogram(df, x=column, color=group_by, 
                              nbins=bins if bins else 30,
                              title=title,
                              labels={
                                  column: self.column_labels.get(column, column),
                                  group_by: self.column_labels.get(group_by, group_by)
                              })
        else:
            fig = px.histogram(df, x=column, 
                              nbins=bins if bins else 30,
                              title=title,
                              labels={
                                  column: self.column_labels.get(column, column)
                              })
        
        fig.update_layout(
            xaxis_title=self.column_labels.get(column, column),
            yaxis_title="Frequência",
            bargap=0.1
        )
        
        return fig
    
    def create_boxplot(self, df: pd.DataFrame, 
                      y_column: str, 
                      x_column: Optional[str] = None) -> go.Figure:
        """
        Cria um gráfico de caixa (boxplot).
        
        Args:
            df: DataFrame processado
            y_column: Coluna para o eixo Y (valores numéricos)
            x_column: Coluna opcional para o eixo X (categorias)
            
        Returns:
            Figura Plotly com o boxplot
        """
        if y_column not in df.columns:
            fig = go.Figure()
            fig.update_layout(title="Dados não disponíveis para boxplot")
            return fig
        
        if x_column and x_column not in df.columns:
            x_column = None
        
        if x_column:
            title = f'Distribuição de {self.column_labels.get(y_column, y_column)} por {self.column_labels.get(x_column, x_column)}'
            fig = px.box(df, x=x_column, y=y_column, 
                        title=title,
                        labels={
                            x_column: self.column_labels.get(x_column, x_column),
                            y_column: self.column_labels.get(y_column, y_column)
                        })
        else:
            title = f'Distribuição de {self.column_labels.get(y_column, y_column)}'
            fig = px.box(df, y=y_column, 
                        title=title,
                        labels={
                            y_column: self.column_labels.get(y_column, y_column)
                        })
        
        return fig
    
    def create_heatmap(self, df: pd.DataFrame, 
                      columns: Optional[List[str]] = None) -> go.Figure:
        """
        Cria um mapa de calor de correlação entre variáveis numéricas.
        
        Args:
            df: DataFrame processado
            columns: Lista de colunas para incluir no mapa de calor
            
        Returns:
            Figura Plotly com o mapa de calor
        """
        # Seleciona apenas colunas numéricas
        numeric_df = df.select_dtypes(include=['int64', 'float64'])
        
        if columns:
            # Filtra para incluir apenas as colunas solicitadas que existem e são numéricas
            valid_columns = [col for col in columns if col in numeric_df.columns]
            if not valid_columns:
                fig = go.Figure()
                fig.update_layout(title="Nenhuma coluna numérica válida para mapa de calor")
                return fig
            numeric_df = numeric_df[valid_columns]
        
        if numeric_df.empty or numeric_df.shape[1] < 2:
            fig = go.Figure()
            fig.update_layout(title="Dados insuficientes para mapa de calor")
            return fig
        
        # Calcula a matriz de correlação
        corr_matrix = numeric_df.corr()
        
        # Cria rótulos mais descritivos
        labels = {col: self.column_labels.get(col, col) for col in corr_matrix.columns}
        
        # Cria o mapa de calor
        fig = px.imshow(
            corr_matrix,
            labels=dict(x="Variável", y="Variável", color="Correlação"),
            x=[labels.get(x, x) for x in corr_matrix.columns],
            y=[labels.get(y, y) for y in corr_matrix.columns],
            color_continuous_scale="RdBu_r",
            title="Matriz de Correlação"
        )
        
        # Adiciona anotações com os valores
        annotations = []
        for i, row in enumerate(corr_matrix.values):
            for j, value in enumerate(row):
                annotations.append(
                    dict(
                        x=j,
                        y=i,
                        text=f"{value:.2f}",
                        showarrow=False,
                        font=dict(
                            color="white" if abs(value) > 0.5 else "black"
                        )
                    )
                )
        
        fig.update_layout(annotations=annotations)
        
        return fig
    
    def create_scatter_plot(self, df: pd.DataFrame, 
                           x_column: str, 
                           y_column: str,
                           color_by: Optional[str] = None,
                           size_by: Optional[str] = None) -> go.Figure:
        """
        Cria um gráfico de dispersão.
        
        Args:
            df: DataFrame processado
            x_column: Coluna para o eixo X
            y_column: Coluna para o eixo Y
            color_by: Coluna opcional para colorir os pontos
            size_by: Coluna opcional para definir o tamanho dos pontos
            
        Returns:
            Figura Plotly com o gráfico de dispersão
        """
        if x_column not in df.columns or y_column not in df.columns:
            fig = go.Figure()
            fig.update_layout(title="Dados não disponíveis para gráfico de dispersão")
            return fig
        
        title = f'{self.column_labels.get(y_column, y_column)} vs {self.column_labels.get(x_column, x_column)}'
        
        # Configura os argumentos para o gráfico
        scatter_args = {
            "data_frame": df,
            "x": x_column,
            "y": y_column,
            "title": title,
            "labels": {
                x_column: self.column_labels.get(x_column, x_column),
                y_column: self.column_labels.get(y_column, y_column)
            }
        }
        
        # Adiciona coloração se especificado
        if color_by and color_by in df.columns:
            scatter_args["color"] = color_by
            scatter_args["labels"][color_by] = self.column_labels.get(color_by, color_by)
        
        # Adiciona tamanho se especificado
        if size_by and size_by in df.columns:
            scatter_args["size"] = size_by
            scatter_args["labels"][size_by] = self.column_labels.get(size_by, size_by)
        
        fig = px.scatter(**scatter_args)
        
        return fig
    
    @staticmethod
    def streamlit_display(fig: go.Figure, use_container_width: bool = True) -> None:
        """
        Exibe uma figura Plotly no Streamlit.
        
        Args:
            fig: Figura Plotly para exibir
            use_container_width: Se deve usar a largura total do container
        """
        st.plotly_chart(fig, use_container_width=use_container_width)
