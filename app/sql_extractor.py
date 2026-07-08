# app/sql_extractor.py
import pyodbc
import pandas as pd
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class SQLExtractor:
    """Extract data from SQL Server and convert it into chunks."""
    
    def __init__(self):
        self.connection_string = self._build_connection_string()
        self.conn = None
    
    def _build_connection_string(self) -> str:
        """Build the database connection string."""
        server = os.getenv('SQL_SERVER', 'localhost')
        database = os.getenv('SQL_DATABASE', '')
        username = os.getenv('SQL_USERNAME', '')
        password = os.getenv('SQL_PASSWORD', '')
        driver = os.getenv('SQL_DRIVER', 'ODBC Driver 18 for SQL Server')
        
        if username and password:
            # SQL Server Authentication
            return f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=no;TrustServerCertificate=yes'
        else:
            # Windows Authentication (Trusted Connection)
            return f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};Trusted_Connection=yes;Encrypt=no;TrustServerCertificate=yes'
    
    def connect(self):
        """Connect to the database."""
        try:
            self.conn = pyodbc.connect(self.connection_string)
            print("✅ Successfully connected to SQL Server")
            return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a query and return results as a DataFrame."""
        if not self.conn:
            if not self.connect():
                return pd.DataFrame()
        
        try:
            df = pd.read_sql(query, self.conn)
            print(f"✅ Retrieved {len(df)} rows from the database")
            return df
        except Exception as e:
            print(f"❌ Query execution error: {e}")
            return pd.DataFrame()
    
    def dataframe_to_chunks(self, df: pd.DataFrame, table_name: str = "sql_data") -> List[Dict[str, Any]]:
        """
        Convert DataFrame to text chunks.
        Each row becomes a chunk with table and column information.
        """
        chunks = []
        
        for idx, row in df.iterrows():
            # Convert the row to readable text
            row_text = f"Table: {table_name}\n"
            for col in df.columns:
                value = row[col]
                if pd.notna(value):
                    row_text += f"{col}: {value}\n"
            
            chunks.append({
                "chunk_id": f"sql_{table_name}_row_{idx}",
                "file_id": f"sql_{table_name}",
                "chunk_index": idx,
                "content": row_text.strip(),
                "chunk_size": len(row_text),
                "strategy": "sql_row",
                "metadata": {
                    "source_type": "sql_server",
                    "table_name": table_name,
                    "row_index": idx,
                    "columns": list(df.columns)
                }
            })
        
        return chunks
    
    def get_all_tables(self) -> List[str]:
        """Get a list of all tables in the database."""
        if not self.conn:
            if not self.connect():
                return []
        
        query = """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE'
        """
        
        try:
            df = pd.read_sql(query, self.conn)
            return df['TABLE_NAME'].tolist()
        except:
            return []
    
    def extract_table_data(self, table_name: str, limit: int = None) -> pd.DataFrame:
        """Extract data from a specific table."""
        query = f"SELECT * FROM [{table_name}]"
        if limit:
            query = f"SELECT TOP {limit} * FROM [{table_name}]"
        
        return self.execute_query(query)
    
    def extract_custom_query(self, query: str) -> pd.DataFrame:
        """Execute a custom query and extract data."""
        return self.execute_query(query)
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("🔌 SQL Server connection closed")