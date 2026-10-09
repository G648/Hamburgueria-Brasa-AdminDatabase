import streamlit as st
import pandas as pd
import re

from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

SERVIDOR = r"brasa-guilherme.database.windows.net"
BANCO = "hamburgueriaBrasa"
DRIVER = "ODBC Driver 18 for SQL Server"

#OUTRO MÉTODO LOGIN
# USUARIO = "sa"
# SENHA = "Senai@134"

def ler_segredos():
    try:
        return st.secrets["banco"]
    except Exception:
        return None

@st.cache_resource
def conectar():
    # Autenticação via windows utilizando ODBC
    banco = ler_segredos()
    if banco :
        driver = banco.get("driver", "ODBC Driver 17 for SQL Server")
        odbc = (
            f"DRIVER={{{driver}}};SERVER={banco['servidor']};DATABASE={banco['nome']};"
            f"UID={banco['usuario']};PWD={banco['senha']};"
            "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=60"
        )
    else:  # SQL Server local, autenticação do Windows
        odbc = (
            f"DRIVER={{{DRIVER}}};SERVER={SERVIDOR};DATABASE={BANCO};"
            "Trusted_Connection=yes;TrustServerCertificate=yes"
        )
        
    return create_engine("mssql+pyodbc:///?odbc_connect="+ quote_plus(odbc), pool_pre_ping=True)


def consultar(sql):
    """Executa a consulta no sql server e devolve o resultado como tabela"""
    with conectar().connect() as conexao:
        return pd.read_sql(text(sql), conexao)
    
    
    
def mensagem_erro(erro):
    """Tira só a mensagem do SQL Server do meio do texto do erro."""
    achou = re.search(r"\[SQL Server\](.+?)\s*\(\d+\)", str(erro))
    return achou.group(1) if achou else str(erro)
