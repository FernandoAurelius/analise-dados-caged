import pandas as pd
import basedosdados as bd
from typing import Dict, Optional, List, Union
from dotenv import load_dotenv
import os


class DataLoader:
    """
    Classe responsável por carregar dados do CAGED usando a API da Base dos Dados.
    
    Esta classe implementa o princípio de responsabilidade única (S do SOLID),
    sendo responsável apenas por operações de carregamento de dados.
    """
    
    def __init__(self, project_id) -> None:
        """
        Inicializa o DataLoader com valores padrão.
        """
        self.project_id = project_id
    
    def load_caged_data(self, 
                        year: Union[int, List[int]], 
                        month: Optional[Union[int, List[int]]] = None,
                        location: Optional[Dict[str, str]] = None,
                        filters: Optional[Dict[str, Union[str, List[str]]]] = None,
                        limit: Optional[int] = 1000) -> pd.DataFrame:
        """
        Carrega dados do CAGED para o ano e mês especificados.
        
        Args:
            year: Ano ou lista de anos para filtrar os dados
            month: Mês ou lista de meses para filtrar os dados
            location: Dicionário com informações de localização (uf, municipio)
            filters: Filtros adicionais para aplicar na consulta
            limit: Limite de linhas para retornar
        
        Returns:
            DataFrame contendo os dados do CAGED
        """
        query_filters = {}
        
        # Adiciona filtro de ano
        if isinstance(year, int):
            query_filters["ano"] = year
        elif isinstance(year, list):
            query_filters["ano"] = year
        
        # Adiciona filtro de mês se fornecido
        if month is not None:
            if isinstance(month, int):
                query_filters["mes"] = month
            elif isinstance(month, list):
                query_filters["mes"] = month
        
        # Adiciona filtros de localização
        if location:
            query_filters.update(location)
        
        # Adiciona outros filtros
        if filters:
            query_filters.update(filters)
        
        try:
            # Consulta usando o basedosdados
            query = """
            SELECT *
            FROM `basedosdados.br_me_caged.microdados_movimentacao`
            """
            
            # Adiciona cláusulas WHERE para os filtros
            if query_filters:
                where_clauses = []
                for key, value in query_filters.items():
                    if isinstance(value, list):
                        formatted_values = ", ".join([f"'{v}'" if isinstance(v, str) else str(v) for v in value])
                        where_clauses.append(f"{key} IN ({formatted_values})")
                    else:
                        where_value = f"'{value}'" if isinstance(value, str) else value
                        where_clauses.append(f"{key} = {where_value}")
                
                query += " WHERE " + " AND ".join(where_clauses)
            
            # Adiciona limite
            if limit:
                query += f" LIMIT {limit}"
            
            df = bd.read_sql(query, billing_project_id=self.project_id)
            return df
        
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")
            # Retorna um DataFrame vazio em caso de erro
            return pd.DataFrame()
    
    def load_sample_data(self) -> pd.DataFrame:
        """
        Carrega uma amostra de dados do CAGED para demonstração.
        Útil quando não há acesso à API ou para testes rápidos.
        
        Returns:
            DataFrame com uma amostra de dados do CAGED
        """
        try:
            # Consulta simplificada para demonstração
            query = """
            SELECT *
            FROM `basedosdados.br_me_caged.microdados_movimentacao`
            WHERE ano = 2021 AND mes = 1
            LIMIT 1000
            """
            
            df = bd.read_sql(query, billing_project_id=self.project_id)
            return df
        
        except Exception as e:
            print(f"Erro ao carregar dados de amostra: {e}")
            # Cria um DataFrame de exemplo em caso de erro
            return self._create_mock_data()
    
    def _create_mock_data(self) -> pd.DataFrame:
        """
        Cria dados simulados para quando não há acesso à API.
        
        Returns:
            DataFrame com dados simulados do CAGED
        """
        # Dados de exemplo simulando o CAGED
        data = {
            'ano': [2021] * 50,
            'mes': [i % 12 + 1 for i in range(50)],
            'uf': ['SP', 'RJ', 'MG', 'RS', 'PR'] * 10,
            'idade': [20 + i % 40 for i in range(50)],
            'sexo': ['1', '2'] * 25,  # 1-Masculino, 2-Feminino
            'grau_instrucao': [i % 9 + 1 for i in range(50)],  # Códigos de 1 a 9
            'cbo_2002': [f"{(i % 10) * 1111}" for i in range(50)],
            'categoria': [i % 5 + 1 for i in range(50)],
            'subclasse_cnae_2': [f"{(i % 10) * 1111}" for i in range(50)],
            'salario': [1100 + (i * 100) for i in range(50)],
            'tipo_movimentacao': [i % 10 + 1 for i in range(50)],
            'tipo_estabelecimento': [i % 3 + 1 for i in range(50)]
        }
        return pd.DataFrame(data)
