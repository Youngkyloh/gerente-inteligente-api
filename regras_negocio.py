import sqlite3
from datetime import datetime

# Função auxiliar para conectar ao banco
def conectar():
    return sqlite3.connect("gerente_inteligente.db")

# 1. Função para alimentar o estoque
def cadastrar_produto(nome, custo, preco_venda, estoque):
    conexao = conectar()
    cursor = conexao.cursor()
    
    cursor.execute("""
    INSERT INTO produtos (nome, custo, preco_venda, estoque) 
    VALUES (?, ?, ?, ?)
    """, (nome, custo, preco_venda, estoque))
    
    conexao.commit()
    conexao.close()
    print(f"📦 Produto '{nome}' cadastrado com sucesso! Estoque inicial: {estoque}")

# 2. O Motor Principal: Venda e Efeito Dominó
def registrar_venda(produto_id):
    conexao = conectar()
    cursor = conexao.cursor()
    
    # Busca o produto pelo ID
    cursor.execute("SELECT nome, preco_venda, estoque FROM produtos WHERE id = ?", (produto_id,))
    produto = cursor.fetchone()
    
    if produto:
        nome, preco_venda, estoque = produto
        
        if estoque > 0:
            novo_estoque = estoque - 1
            status = 'ATIVO'
            
            # Regra de Estoque Crítico
            if novo_estoque <= 1:
                status = 'PAUSADO'
                print(f"⚠️ ALERTA: O estoque de '{nome}' chegou a {novo_estoque}. Anúncio PAUSADO automaticamente para evitar ruptura.")
            
            # Atualiza o banco com o novo estoque e status
            cursor.execute("UPDATE produtos SET estoque = ?, status = ? WHERE id = ?", (novo_estoque, status, produto_id))
            
            # Registra o dinheiro entrando no Fluxo de Caixa
            data_hoje = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
            INSERT INTO financeiro (tipo, valor, data, descricao) 
            VALUES ('ENTRADA', ?, ?, ?)
            """, (preco_venda, data_hoje, f"Venda do produto: {nome}"))
            
            conexao.commit()
            print(f"✅ Venda registrada! R$ {preco_venda:.2f} adicionados ao caixa.")
        else:
            print(f"❌ Venda negada: O produto '{nome}' está esgotado.")
    
    conexao.close()

# Área de Testes (Rodando o programa na prática)
if __name__ == "__main__":
    print("--- INICIANDO SISTEMA ---")
    
    # Teste 1: Cadastrando um produto (Descomente se quiser cadastrar mais)
    cadastrar_produto("Açaí Bora Clássico 330ml", custo=5.00, preco_venda=15.90, estoque=3)
    
    # Teste 2: Simulando as vendas para testar o gatilho de pausa
    print("\n--- SIMULANDO VENDAS ---")
    registrar_venda(1) # Primeira venda (Estoque cai para 2)
    registrar_venda(1) # Segunda venda (Estoque cai para 1 -> GATILHO DE ALERTA DEVE DISPARAR)