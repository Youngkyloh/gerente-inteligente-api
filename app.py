import streamlit as st
import sqlite3
import pandas as pd

# 1. Configuração inicial da página (Aba do navegador)
st.set_page_config(page_title="Gerente Inteligente", layout="wide")

# 2. Título principal do sistema
st.title("📊 Gerente Inteligente - Painel de Controle")

# 3. Função para buscar os dados no SQLite e converter para visualização
def carregar_dados(tabela):
    conexao = sqlite3.connect("gerente_inteligente.db")
    # O Pandas lê a tabela do banco e organiza as colunas automaticamente
    df = pd.read_sql(f"SELECT * FROM {tabela}", conexao)
    conexao.close()
    return df

# 4. Criando a Seção de Estoque na tela
st.header("📦 Posição de Estoque")
df_produtos = carregar_dados("produtos")

# Regra visual: Destacar na tela se o anúncio foi pausado
if not df_produtos.empty:
    st.dataframe(df_produtos, use_container_width=True)
else:
    st.info("Nenhum produto cadastrado ainda.")

# 5. Criando a Seção de Fluxo de Caixa na tela
st.header("💰 Fluxo de Caixa Diário")
df_financeiro = carregar_dados("financeiro")

if not df_financeiro.empty:
    st.dataframe(df_financeiro, use_container_width=True)
    
    # Calculando o faturamento total e exibindo como um indicador financeiro
    faturamento = df_financeiro['valor'].sum()
    st.metric(label="Faturamento Total", value=f"R$ {faturamento:.2f}")
else:
    st.info("Nenhuma movimentação financeira registrada.")