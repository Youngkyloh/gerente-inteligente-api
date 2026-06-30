import sqlite3
from datetime import datetime

def inicializar_banco():
    # Conecta ao arquivo do banco (se não existir, ele cria automaticamente)
    conexao = sqlite3.connect("gerente_inteligente.db")
    cursor = conexao.cursor()
    
    # 1. Criação da Tabela de Produtos (Estoque e CMV)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        custo REAL NOT NULL,
        preco_venda REAL NOT NULL,
        estoque INTEGER NOT NULL,
        status TEXT DEFAULT 'ATIVO'
    )
    """)
    
    # 2. Criação da Tabela de Movimentações Financeiras (Contas a Pagar/Receber)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL, -- 'ENTRADA' ou 'SAIDA'
        valor REAL NOT NULL,
        data TEXT NOT NULL,
        descricao TEXT
    )
    """)
    
    # 3. Criação da Tabela de Controle de Licença Local
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS controle_licenca (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chave_licenca TEXT NOT NULL,
        status_assinatura TEXT DEFAULT 'ATIVA',
        data_validade TEXT NOT NULL
    )
    """)
    
    conexao.commit()
    conexao.close()
    print("Banco de dados local estruturado com sucesso!")

if __name__ == "__main__":
    inicializar_banco()