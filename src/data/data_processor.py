import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Tuple


class DataProcessor:
    """
    Classe responsável pelo processamento e transformação dos dados do CAGED.
    
    Segue o princípio de responsabilidade única (S do SOLID),
    focando apenas em operações de tratamento e transformação dos dados.
    """
    
    def __init__(self) -> None:
        """
        Inicializa o processador de dados com dicionários de mapeamento.
        """
        # Dicionários para decodificar os campos categóricos
        self.sexo_mapping = {
            '1': 'Masculino',
            '2': 'Feminino'
        }
        
        self.grau_instrucao_mapping = {
            1: 'Analfabeto',
            2: 'Até 5ª Incompleto',
            3: '5ª Completo Fundamental',
            4: '6ª a 9ª Fundamental',
            5: 'Fundamental Completo',
            6: 'Médio Incompleto',
            7: 'Médio Completo',
            8: 'Superior Incompleto',
            9: 'Superior Completo'
        }
        
        self.tipo_movimentacao_mapping = {
            1: 'Admissão',
            2: 'Desligamento',
            3: 'Transferência'
        }
    
    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processa o DataFrame do CAGED, realizando limpeza e transformações.
        
        Args:
            df: DataFrame contendo os dados do CAGED
            
        Returns:
            DataFrame processado
        """
        # Cria uma cópia para não modificar o original
        processed_df = df.copy()
        
        # Trata valores nulos
        processed_df = self._handle_missing_values(processed_df)
        
        # Converte campos categóricos
        processed_df = self._decode_categorical(processed_df)
        
        # Cria campos derivados
        processed_df = self._create_derived_fields(processed_df)
        
        return processed_df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Trata valores ausentes no DataFrame.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame com valores ausentes tratados
        """
        # Cria uma cópia para não modificar o original
        clean_df = df.copy()
        
        # Campos numéricos - preenche com a mediana
        numeric_cols = clean_df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            if clean_df[col].isnull().sum() > 0:
                clean_df[col] = clean_df[col].fillna(clean_df[col].median())
        
        # Campos categóricos - preenche com o valor mais frequente
        categorical_cols = clean_df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            if clean_df[col].isnull().sum() > 0:
                clean_df[col] = clean_df[col].fillna(clean_df[col].mode()[0])
        
        return clean_df
    
    def _decode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Decodifica campos categóricos para valores legíveis.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame com campos categóricos decodificados
        """
        # Cria uma cópia para não modificar o original
        decoded_df = df.copy()
        
        # Aplica mapeamentos se as colunas existirem
        if 'sexo' in decoded_df.columns:
            decoded_df['sexo_desc'] = decoded_df['sexo'].map(self.sexo_mapping)
        
        if 'grau_instrucao' in decoded_df.columns:
            decoded_df['grau_instrucao_desc'] = decoded_df['grau_instrucao'].map(self.grau_instrucao_mapping)
        
        if 'tipo_movimentacao' in decoded_df.columns:
            decoded_df['tipo_movimentacao_desc'] = decoded_df['tipo_movimentacao'].map(self.tipo_movimentacao_mapping)
        
        return decoded_df
    
    def _create_derived_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria campos derivados para análise.
        
        Args:
            df: DataFrame original
            
        Returns:
            DataFrame com campos derivados adicionados
        """
        # Cria uma cópia para não modificar o original
        derived_df = df.copy()
        
        # Cria campo de data completa se ano e mês estiverem presentes
        if 'ano' in derived_df.columns and 'mes' in derived_df.columns:
            derived_df['data'] = pd.to_datetime(derived_df['ano'].astype(str) + '-' + 
                                              derived_df['mes'].astype(str) + '-01')
        
        # Cria faixas etárias se idade estiver presente
        if 'idade' in derived_df.columns:
            bins = [0, 18, 25, 35, 45, 55, 65, 100]
            labels = ['<18', '18-24', '25-34', '35-44', '45-54', '55-64', '65+']
            derived_df['faixa_etaria'] = pd.cut(derived_df['idade'], bins=bins, labels=labels, right=False)
        
        # Cria faixas salariais se salário estiver presente
        if 'salario' in derived_df.columns:
            bins = [0, 1100, 2200, 3300, 5000, 10000, float('inf')]
            labels = ['Até 1 SM', '1-2 SM', '2-3 SM', '3-5 SM', '5-10 SM', '10+ SM']
            derived_df['faixa_salarial'] = pd.cut(derived_df['salario'], bins=bins, labels=labels, right=False)
        
        return derived_df
    
    def get_summary_statistics(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Calcula estatísticas resumidas do DataFrame.
        
        Args:
            df: DataFrame processado
            
        Returns:
            Dicionário com diferentes estatísticas resumidas
        """
        summary = {}
        
        # Estatísticas descritivas para campos numéricos
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        summary['numeric'] = df[numeric_cols].describe()
        
        # Contagens para campos categóricos
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        summary['categorical'] = {col: df[col].value_counts() for col in categorical_cols}
        
        return summary
    
    def aggregate_by_period(self, df: pd.DataFrame, 
                            group_by: List[str] = ['ano', 'mes'], 
                            metrics: List[str] = ['salario']) -> pd.DataFrame:
        """
        Agrega dados por período (ano/mês).
        
        Args:
            df: DataFrame processado
            group_by: Lista de colunas para agrupar
            metrics: Lista de métricas para calcular
            
        Returns:
            DataFrame agregado por período
        """
        # Verifica se as colunas existem
        valid_group_by = [col for col in group_by if col in df.columns]
        valid_metrics = [col for col in metrics if col in df.columns]
        
        if not valid_group_by or not valid_metrics:
            return pd.DataFrame()
        
        # Realiza a agregação
        agg_dict = {metric: ['mean', 'median', 'min', 'max', 'count'] for metric in valid_metrics}
        result = df.groupby(valid_group_by).agg(agg_dict)
        
        # Nivela o índice de múltiplos níveis para facilitar o uso
        result.columns = ['_'.join(col).strip() for col in result.columns.values]
        result = result.reset_index()
        
        return result
    
    def filter_data(self, df: pd.DataFrame, 
                   filters: Dict[str, Union[str, List[str], Tuple[float, float]]]) -> pd.DataFrame:
        """
        Filtra o DataFrame com base nos critérios fornecidos.
        
        Args:
            df: DataFrame processado
            filters: Dicionário com filtros a serem aplicados
            
        Returns:
            DataFrame filtrado
        """
        # Cria uma cópia para não modificar o original
        filtered_df = df.copy()
        
        for column, value in filters.items():
            if column not in filtered_df.columns:
                continue
                
            if isinstance(value, (list, tuple)) and len(value) == 2 and all(isinstance(v, (int, float)) for v in value):
                # Intervalo numérico
                filtered_df = filtered_df[(filtered_df[column] >= value[0]) & (filtered_df[column] <= value[1])]
            
            elif isinstance(value, list):
                # Lista de valores
                filtered_df = filtered_df[filtered_df[column].isin(value)]
                
            else:
                # Valor único
                filtered_df = filtered_df[filtered_df[column] == value]
        
        return filtered_df
