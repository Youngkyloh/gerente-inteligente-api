import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import re

# ==========================================
# 1. CONFIGURAÇÃO INICIAL E SESSÃO
# ==========================================
st.set_page_config(page_title="Gerente Inteligente", layout="wide")

if 'logado' not in st.session_state:
    st.session_state.update({
        'logado': False, 'usuario': '', 'perfil': '', 'id_loja': '', 
        'status_assinatura': '', 'form_key': 0, 'sucesso_cadastro': False
    })

def limpar_formulario_cadastro():
    for key in ['cad_user', 'cad_senha', 'cad_loja', 'cad_doc', 'cad_cod']:
        st.session_state[key] = ""

# ==========================================
# 2. FUNÇÕES DE VALIDAÇÃO
# ==========================================
def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, str(cpf)))
    if len(cpf) != 11 or len(set(cpf)) == 1: return False
    for i in range(9, 11):
        value = sum((int(cpf[num]) * ((i+1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != int(cpf[i]): return False
    return True

def validar_cnpj(cnpj):
    cnpj = ''.join(filter(str.isdigit, str(cnpj)))
    if len(cnpj) != 14 or len(set(cnpj)) == 1: return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    calc1 = sum(int(cnpj[i]) * pesos1[i] for i in range(12))
    dig1 = 11 - (calc1 % 11) if calc1 % 11 >= 2 else 0
    calc2 = sum(int(cnpj[i]) * pesos2[i] for i in range(13))
    dig2 = 11 - (calc2 % 11) if calc2 % 11 >= 2 else 0
    return int(cnpj[12]) == dig1 and int(cnpj[13]) == dig2

def validar_documento(doc):
    doc_limpo = ''.join(filter(str.isdigit, str(doc)))
    if len(doc_limpo) == 11: return validar_cpf(doc_limpo)
    elif len(doc_limpo) == 14: return validar_cnpj(doc_limpo)
    return False

def contem_sequencia(s):
    for i in range(len(s) - 2):
        if ord(s[i+1]) == ord(s[i]) + 1 and ord(s[i+2]) == ord(s[i]) + 2: return True
        if ord(s[i+1]) == ord(s[i]) - 1 and ord(s[i+2]) == ord(s[i]) - 2: return True
    return False

def verificar_forca_senha(senha):
    if len(senha) < 8: return False, "Mínimo 8 caracteres."
    if not re.search(r"[A-Z]", senha): return False, "Falta 1 letra maiúscula."
    if not re.search(r"[a-z]", senha): return False, "Falta 1 letra minúscula."
    if not re.search(r"[0-9]", senha): return False, "Falta 1 número."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha): return False, "Falta caractere especial."
    if re.search(r"(.)\1{2,}", senha): return False, "Evite repetições óbvias (ex: 111)."
    if contem_sequencia(senha): return False, "Evite sequências (ex: 123)."
    if re.search(r"(19|20)\d{2}", senha): return False, "Evite anos ou datas."
    return True, "Senha OK"

# ==========================================
# 3. BANCO DE DADOS
# ==========================================
def inicializar_tabelas():
    conexao = sqlite3.connect("gerente_inteligente.db")
    cursor = conexao.cursor()
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, senha TEXT NOT NULL, perfil TEXT NOT NULL, id_loja TEXT NOT NULL, documento TEXT, status_assinatura TEXT DEFAULT 'ATIVA')""")
    try: cursor.execute("ALTER TABLE usuarios ADD COLUMN documento TEXT DEFAULT ''")
    except: pass
    try: cursor.execute("ALTER TABLE usuarios ADD COLUMN status_assinatura TEXT DEFAULT 'ATIVA'")
    except: pass
    
    cursor.execute("SELECT id FROM usuarios WHERE perfil = 'DEV'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (username, senha, perfil, id_loja, documento, status_assinatura) VALUES ('Junior_Master', 'Gerente@2026', 'DEV', 'SISTEMA_CENTRAL', '00000000000', 'ATIVA')")

    cursor.execute("""CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, custo REAL NOT NULL, preco_venda REAL NOT NULL, estoque INTEGER NOT NULL, status TEXT DEFAULT 'ATIVO', id_loja TEXT NOT NULL DEFAULT 'SISTEMA_CENTRAL')""")
    try: cursor.execute("ALTER TABLE produtos ADD COLUMN id_loja TEXT DEFAULT 'SISTEMA_CENTRAL'")
    except: pass

    cursor.execute("""CREATE TABLE IF NOT EXISTS financeiro (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT NOT NULL, valor REAL NOT NULL, data TEXT NOT NULL, descricao TEXT, id_loja TEXT NOT NULL DEFAULT 'SISTEMA_CENTRAL')""")
    try: cursor.execute("ALTER TABLE financeiro ADD COLUMN id_loja TEXT DEFAULT 'SISTEMA_CENTRAL'")
    except: pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS insumos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        custo REAL NOT NULL,
        qtd_embalagem REAL NOT NULL,
        medida TEXT NOT NULL,
        id_loja TEXT NOT NULL
    )
    """)
    try: cursor.execute("ALTER TABLE insumos ADD COLUMN qtd_embalagem REAL DEFAULT 1")
    except: pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ficha_tecnica (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_produto INTEGER NOT NULL,
        id_insumo INTEGER NOT NULL,
        qtd_usada REAL NOT NULL,
        id_loja TEXT NOT NULL
    )
    """)

    conexao.commit()
    conexao.close()

inicializar_tabelas()

def executar_query(query, parametros=()):
    conexao = sqlite3.connect("gerente_inteligente.db")
    cursor = conexao.cursor()
    cursor.execute(query, parametros)
    conexao.commit()
    conexao.close()

def calcular_custo_produto(id_produto, id_loja):
    conexao = sqlite3.connect("gerente_inteligente.db")
    cursor = conexao.cursor()
    
    query = """
    SELECT SUM((i.custo / i.qtd_embalagem) * f.qtd_usada)
    FROM ficha_tecnica f
    JOIN insumos i ON f.id_insumo = i.id
    WHERE f.id_produto = ? AND f.id_loja = ?
    """
    cursor.execute(query, (id_produto, id_loja))
    resultado = cursor.fetchone()[0]
    conexao.close()
    
    novo_custo = resultado if resultado else 0.0
    executar_query("UPDATE produtos SET custo = ? WHERE id = ? AND id_loja = ?", (novo_custo, id_produto, id_loja))
    return novo_custo

# ==========================================
# 4. TELA DE LOGIN E CADASTRO (PÚBLICO)
# ==========================================
if not st.session_state['logado']:
    st.title("🔐 Acesso ao Sistema")
    tab_login, tab_cadastro = st.tabs(["Entrar", "Criar Conta Administrador"])
    
    with tab_login:
        st.subheader("Login")
        user_login = st.text_input("Usuário", key="log_user")
        senha_login = st.text_input("Senha", type="password", key="log_senha")
        if st.button("Entrar no Sistema", type="primary"):
            conexao = sqlite3.connect("gerente_inteligente.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT perfil, id_loja, status_assinatura FROM usuarios WHERE username = ? AND senha = ?", (user_login, senha_login))
            resultado = cursor.fetchone()
            conexao.close()
            if resultado:
                st.session_state.update({'logado': True, 'usuario': user_login, 'perfil': resultado[0], 'id_loja': resultado[1], 'status_assinatura': resultado[2]})
                st.rerun()
            else: st.error("Usuário ou senha incorretos.")

    with tab_cadastro:
        st.subheader("Cadastro de Matriz/Filial (ADM)")
        if st.session_state['sucesso_cadastro']:
            st.success("🎉 CONTA CRIADA COM SUCESSO! Vá na aba 'Entrar' para acessar.")
            st.session_state['sucesso_cadastro'] = False
            
        fk = st.session_state['form_key']
        novo_user_adm = st.text_input("Nome de Usuário", key=f"cad_user_{fk}")
        doc_adm = st.text_input("CPF ou CNPJ (Apenas números)", key=f"cad_doc_{fk}")
        loja_definida = st.text_input("Identificação da Loja (Ex: 01, Matriz)", key=f"cad_loja_{fk}")
        codigo_liberacao = st.text_input("Código Mestre de Instalação", type="password", key=f"cad_cod_{fk}")
        nova_senha_adm = st.text_input("Definir Senha", type="password", key=f"cad_senha_{fk}")
        
        req_len = len(nova_senha_adm) >= 8
        req_mai = bool(re.search(r"[A-Z]", nova_senha_adm))
        req_min = bool(re.search(r"[a-z]", nova_senha_adm))
        req_num = bool(re.search(r"[0-9]", nova_senha_adm))
        req_esp = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", nova_senha_adm))
        req_rep = not bool(re.search(r"(.)\1{2,}", nova_senha_adm))
        req_seq = not contem_sequencia(nova_senha_adm)
        req_dat = not bool(re.search(r"(19|20)\d{2}", nova_senha_adm))
        senha_forte = all([req_len, req_mai, req_min, req_num, req_esp, req_rep, req_seq, req_dat])
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown(f"{'✅' if req_len else '❌'} Mínimo 8 caracteres")
            st.markdown(f"{'✅' if req_mai else '❌'} 1 Letra Maiúscula")
            st.markdown(f"{'✅' if req_min else '❌'} 1 Letra Minúscula")
            st.markdown(f"{'✅' if req_num else '❌'} 1 Número")
        with col_c2:
            st.markdown(f"{'✅' if req_esp else '❌'} 1 Caractere Especial (@, #, !...)")
            st.markdown(f"{'✅' if req_rep and nova_senha_adm else '❌'} Sem repetições (Ex: 111)")
            st.markdown(f"{'✅' if req_seq and nova_senha_adm else '❌'} Sem sequências (Ex: 123)")
            st.markdown(f"{'✅' if req_dat and nova_senha_adm else '❌'} Sem datas óbvias")
        
        if st.button("Finalizar Cadastro ADM", type="primary"):
            if codigo_liberacao == "280825":
                if not validar_documento(doc_adm): st.error("⚠️ Documento INVÁLIDO.")
                elif not senha_forte: st.error("⚠️ A senha não atende aos requisitos de segurança.")
                elif novo_user_adm and loja_definida:
                    try:
                        executar_query("INSERT INTO usuarios (username, senha, perfil, id_loja, documento, status_assinatura) VALUES (?, ?, ?, ?, ?, ?)", 
                                       (novo_user_adm, nova_senha_adm, 'ADM', loja_definida, ''.join(filter(str.isdigit, doc_adm)), 'ATIVA'))
                        st.session_state['sucesso_cadastro'] = True
                        st.session_state['form_key'] += 1
                        st.rerun()
                    except sqlite3.IntegrityError: st.error("Este nome de usuário já existe.")
                else: st.warning("Preencha todos os campos.")
            else: st.error("Código Mestre inválido!")

# ==========================================
# 5. TELA DE BLOQUEIO (INADIMPLÊNCIA)
# ==========================================
elif st.session_state['status_assinatura'] == 'BLOQUEADA' and st.session_state['perfil'] != 'DEV':
    st.error("⛔ ACESSO BLOQUEADO")
    st.warning("Sua assinatura encontra-se pendente. Entre em contato com a consultoria para regularizar.")
    if st.button("Sair"):
        st.session_state.update({'logado': False, 'usuario': '', 'perfil': '', 'id_loja': '', 'status_assinatura': ''})
        st.rerun()

# ==========================================
# 6. PAINEL DIVINDADE (SÓ VOCÊ)
# ==========================================
elif st.session_state['perfil'] == 'DEV':
    st.title("👁️ Painel Divindade - Monitoramento de Consultoria")
    if st.sidebar.button("Deslogar Mestre"):
        st.session_state.update({'logado': False, 'usuario': '', 'perfil': '', 'id_loja': '', 'status_assinatura': ''})
        st.rerun()

    tab_contas, tab_dados, tab_novo_cliente = st.tabs(["⚙️ Gestão de Assinaturas", "📊 Raio-X das Lojas", "➕ Cadastrar Cliente"])
    
    with tab_contas:
        st.subheader("🏢 Status dos Clientes")
        conexao = sqlite3.connect("gerente_inteligente.db")
        df_usuarios = pd.read_sql("SELECT id, username, perfil, id_loja, documento, status_assinatura FROM usuarios WHERE perfil != 'DEV'", conexao)
        conexao.close()
        st.dataframe(df_usuarios, use_container_width=True, hide_index=True)
        col_div1, col_div2 = st.columns(2)
        with col_div1:
            st.markdown("🔒 **Cortar/Liberar Acesso**")
            loja_alvo = st.text_input("ID da Loja alvo")
            novo_status = st.selectbox("Status:", ["ATIVA", "BLOQUEADA"])
            if st.button("Aplicar Status"):
                executar_query("UPDATE usuarios SET status_assinatura = ? WHERE id_loja = ? AND perfil != 'DEV'", (novo_status, loja_alvo))
                st.rerun()
        with col_div2:
            st.markdown("☠️ **Exclusão Definitiva**")
            user_id_del = st.number_input("ID do Usuário", min_value=1, step=1)
            if st.button("Apagar Conta", type="primary"):
                executar_query("DELETE FROM usuarios WHERE id = ? AND perfil != 'DEV'", (user_id_del,))
                st.rerun()

    with tab_dados:
        st.subheader("🔍 Investigar Dados de um Cliente")
        if not df_usuarios.empty:
            lojas_existentes = df_usuarios['id_loja'].unique().tolist()
            loja_selecionada = st.selectbox("Selecione a Loja para analisar:", lojas_existentes)
            if loja_selecionada:
                conexao = sqlite3.connect("gerente_inteligente.db")
                df_prod_loja = pd.read_sql("SELECT * FROM produtos WHERE id_loja = ?", conexao, params=(loja_selecionada,))
                df_fin_loja = pd.read_sql("SELECT * FROM financeiro WHERE id_loja = ?", conexao, params=(loja_selecionada,))
                conexao.close()
                col_rx1, col_rx2 = st.columns(2)
                with col_rx1:
                    st.dataframe(df_prod_loja, use_container_width=True, hide_index=True)
                with col_rx2:
                    st.dataframe(df_fin_loja, use_container_width=True, hide_index=True)
                    st.metric(label="Faturamento Registrado", value=f"R$ {df_fin_loja['valor'].sum() if not df_fin_loja.empty else 0:.2f}")
                
                with st.expander("Excluir Item Específico desta loja"):
                    tipo_del_div = st.selectbox("Tipo de Item", ["Produto", "Insumo"], key="sel_tipo_div")
                    id_item_del = st.number_input(f"ID do {tipo_del_div}", min_value=1, step=1, key="del_item_rx")
                    if st.button("Deletar Item", key="btn_del_rx", type="primary"):
                        tabela_alvo = "produtos" if tipo_del_div == "Produto" else "insumos"
                        executar_query(f"DELETE FROM {tabela_alvo} WHERE id = ? AND id_loja = ?", (id_item_del, loja_selecionada))
                        st.success(f"{tipo_del_div} apagado com poderes mestres!")
                        st.rerun()
        else:
            st.info("Nenhuma loja cadastrada ainda.")

    with tab_novo_cliente:
        st.subheader("➕ Onboarding Manual de Consultoria")
        dev_novo_user = st.text_input("Usuário do Cliente")
        dev_doc = st.text_input("CPF ou CNPJ do Cliente")
        dev_loja = st.text_input("Identificação da Loja (Ex: Filial Sul)")
        dev_senha_temp = st.text_input("Senha Temporária Segura", type="password")
        if st.button("Criar Conta ADM"):
            senha_valida, msg_senha = verificar_forca_senha(dev_senha_temp)
            if not validar_documento(dev_doc): st.error("⚠️ Documento Inválido.")
            elif not senha_valida: st.error(f"⚠️ A senha temporária é fraca: {msg_senha}")
            elif dev_novo_user and dev_loja:
                executar_query("INSERT INTO usuarios (username, senha, perfil, id_loja, documento, status_assinatura) VALUES (?, ?, ?, ?, ?, ?)", 
                               (dev_novo_user, dev_senha_temp, 'ADM', dev_loja, ''.join(filter(str.isdigit, dev_doc)), 'ATIVA'))
                st.success("Criado!")

# ==========================================
# 7. TELA PRINCIPAL (CLIENTE NORMAL LOGADO)
# ==========================================
else:
    loja_atual = st.session_state['id_loja']
    user_logado = st.session_state['usuario']
    perfil_logado = st.session_state['perfil']
    
    st.title("📊 Gerente Inteligente - Painel de Controle")
    st.sidebar.header(f"👤 {user_logado}")
    st.sidebar.caption(f"Nível: {perfil_logado} | 🏬 Loja: {loja_atual}")
    if st.sidebar.button("Sair da Conta"):
        st.session_state.update({'logado': False, 'usuario': '', 'perfil': '', 'id_loja': '', 'status_assinatura': ''})
        st.rerun()

    st.sidebar.markdown("---")
    with st.sidebar.expander("🔐 Alterar Minha Senha"):
        senha_atual = st.text_input("Senha Atual", type="password")
        nova_senha_user = st.text_input("Nova Senha", type="password")
        if st.button("Atualizar Senha"):
            conexao = sqlite3.connect("gerente_inteligente.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT id FROM usuarios WHERE username = ? AND senha = ?", (user_logado, senha_atual))
            if cursor.fetchone():
                senha_valida, msg_senha = verificar_forca_senha(nova_senha_user)
                if senha_valida:
                    executar_query("UPDATE usuarios SET senha = ? WHERE username = ?", (nova_senha_user, user_logado))
                    st.success("Senha atualizada com sucesso!")
                else: st.error(f"Senha fraca: {msg_senha}")
            else: st.error("Senha atual incorreta.")
            conexao.close()
        
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Painel de Operações")

    st.sidebar.subheader("🛒 Registrar Venda")
    id_venda = st.sidebar.number_input("ID do Produto", min_value=1, step=1, key="venda_id")
    if st.sidebar.button("Finalizar Venda"):
        conexao = sqlite3.connect("gerente_inteligente.db")
        cursor = conexao.cursor()
        cursor.execute("SELECT nome, preco_venda, estoque FROM produtos WHERE id = ? AND id_loja = ?", (id_venda, loja_atual))
        produto = cursor.fetchone()
        if produto and produto[2] > 0:
            novo_estoque = produto[2] - 1
            status = 'PAUSADO' if novo_estoque <= 1 else 'ATIVO'
            executar_query("UPDATE produtos SET estoque = ?, status = ? WHERE id = ? AND id_loja = ?", (novo_estoque, status, id_venda, loja_atual))
            executar_query("INSERT INTO financeiro (tipo, valor, data, descricao, id_loja) VALUES (?, ?, ?, ?, ?)", 
                           ('ENTRADA', produto[1], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Venda: {produto[0]}", loja_atual))
            st.sidebar.success(f"Venda registrada!")
        else: st.sidebar.error("Esgotado ou ID inválido!")
        conexao.close()

    if perfil_logado in ['ADM', 'ASSISTENTE_ADM']:
        st.sidebar.markdown("---")
        st.sidebar.subheader("🍅 Novo Insumo (Matéria-Prima)")
        nome_insumo = st.text_input("Nome do Insumo (Ex: Carne, Pão)")
        custo_insumo = st.number_input("Preço da Embalagem Fechada (R$)", min_value=0.0, step=0.50)
        qtd_embalagem = st.number_input("Qtd na embalagem (Ex: 1000 se for 1Kg)", min_value=1.0, step=1.0)
        medida_insumo = st.selectbox("Unidade Comprada", ["Gramas", "Mililitros (ml)", "Unidade"])
        if st.sidebar.button("Cadastrar Insumo"):
            executar_query("INSERT INTO insumos (nome, custo, qtd_embalagem, medida, id_loja) VALUES (?, ?, ?, ?, ?)", 
                           (nome_insumo, custo_insumo, qtd_embalagem, medida_insumo, loja_atual))
            st.sidebar.success("Insumo cadastrado!")

    if perfil_logado in ['ADM', 'ASSISTENTE_ADM']:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📦 Novo Produto Final")
        novo_nome = st.sidebar.text_input("Nome do Produto Final")
        novo_preco = st.sidebar.number_input("Preço Venda Desejado (R$)", min_value=0.0, step=0.50)
        novo_estoque_inicial = st.sidebar.number_input("Estoque Inicial", min_value=0, step=1)
        if st.sidebar.button("Cadastrar Produto Vazio"):
            executar_query("INSERT INTO produtos (nome, custo, preco_venda, estoque, id_loja) VALUES (?, ?, ?, ?, ?)", 
                           (novo_nome, 0.0, novo_preco, novo_estoque_inicial, loja_atual))
            st.sidebar.success("Produto criado! Vá na aba de Crafting para colocar os ingredientes.")

    if perfil_logado in ['ADM', 'ASSISTENTE_ADM', 'AUXILIAR_ADM']:
        st.sidebar.markdown("---")
        st.sidebar.subheader("✏️ Atualizar Estoque")
        id_acao = st.sidebar.number_input("ID do Produto (Tabela)", min_value=1, step=1, key="id_acao")
        add_estoque = st.sidebar.number_input("Adicionar Estoque (+)", min_value=0, step=1)
        if st.sidebar.button("➕ Add Estoque"):
            conexao = sqlite3.connect("gerente_inteligente.db")
            cursor = conexao.cursor()
            cursor.execute("SELECT estoque FROM produtos WHERE id = ? AND id_loja = ?", (id_acao, loja_atual))
            resultado = cursor.fetchone()
            conexao.close()
            if resultado:
                estoque_final = resultado[0] + add_estoque
                status_novo = 'PAUSADO' if estoque_final <= 1 else 'ATIVO'
                executar_query("UPDATE produtos SET estoque = ?, status = ? WHERE id = ? AND id_loja = ?", (estoque_final, status_novo, id_acao, loja_atual))
                st.sidebar.success(f"Atualizado para {estoque_final}!")
            else: st.sidebar.error("ID não encontrado.")

    if perfil_logado in ['ADM', 'ASSISTENTE_ADM']:
        st.sidebar.markdown("---")
        st.sidebar.subheader("❌ Excluir Item")
        tipo_exclusao = st.selectbox("O que deseja excluir?", ["Produto", "Insumo"])
        id_del = st.number_input(f"ID do {tipo_exclusao}", min_value=1, step=1, key="id_del_item")
        if st.sidebar.button("Confirmar Exclusão", type="primary"):
            tabela = "produtos" if tipo_exclusao == "Produto" else "insumos"
            executar_query(f"DELETE FROM {tabela} WHERE id = ? AND id_loja = ?", (id_del, loja_atual))
            st.sidebar.warning(f"{tipo_exclusao} deletado!")

    if perfil_logado == 'ADM':
        st.sidebar.markdown("---")
        st.sidebar.subheader("👑 Controle de Acesso")
        with st.sidebar.expander(f"➕ Contratar Funcionário"):
            novo_func_nome = st.text_input("Nome do Funcionário")
            senha_func = st.text_input("Senha Inicial", type="password")
            nivel_func = st.selectbox("Nível de Acesso", ["ASSISTENTE_ADM", "AUXILIAR_ADM", "EDITOR"])
            if st.button("Cadastrar Funcionário"):
                senha_valida, msg_senha = verificar_forca_senha(senha_func)
                if senha_valida:
                    try:
                        executar_query("INSERT INTO usuarios (username, senha, perfil, id_loja, status_assinatura) VALUES (?, ?, ?, ?, ?)", 
                                       (novo_func_nome, senha_func, nivel_func, loja_atual, 'ATIVA'))
                        st.success(f"Funcionário ({nivel_func}) criado com sucesso!")
                    except sqlite3.IntegrityError:
                        st.error("Nome de usuário em uso.")
                else: st.error(f"Senha fraca: {msg_senha}")
        
        st.sidebar.subheader("🧹 Limpeza de Dados")
        if st.sidebar.button("Zerar Fluxo de Caixa", type="primary"):
            executar_query("DELETE FROM financeiro WHERE id_loja = ?", (loja_atual,))
            st.success("Histórico apagado!")
            st.rerun()

    # --- ABAS VISUAIS CENTRAIS COM OS ALERTAS DE MARGEM E CORREÇÃO DO ROUND ---
    tab_produtos, tab_crafting, tab_insumos, tab_caixa = st.tabs([
        "📦 Produtos", "🛠️ Ficha (Crafting)", "🍅 Insumos", "💰 Caixa"
    ])
    
    conexao = sqlite3.connect("gerente_inteligente.db")
    df_produtos = pd.read_sql("SELECT id, nome, custo, preco_venda, estoque, status FROM produtos WHERE id_loja = ?", conexao, params=(loja_atual,))
    df_insumos = pd.read_sql("SELECT id, nome, custo, qtd_embalagem, medida FROM insumos WHERE id_loja = ?", conexao, params=(loja_atual,))
    df_financeiro = pd.read_sql("SELECT id, tipo, valor, data, descricao FROM financeiro WHERE id_loja = ?", conexao, params=(loja_atual,))
    conexao.close()

    with tab_produtos:
        st.subheader("Catálogo de Produtos e Margens")
        if not df_produtos.empty: 
            df_produtos['lucro_bruto'] = df_produtos['preco_venda'] - df_produtos['custo']
            df_produtos['margem_%'] = df_produtos.apply(
                lambda row: round(((row['lucro_bruto'] / row['preco_venda']) * 100), 2) if row['preco_venda'] > 0 else 0.0, 
                axis=1
            )
            st.dataframe(df_produtos, use_container_width=True, hide_index=True)
            
            st.markdown("### 🚨 Alertas da Loja")
            produtos_pausados = df_produtos[df_produtos['status'] == 'PAUSADO']
            if not produtos_pausados.empty:
                for _, row in produtos_pausados.iterrows(): 
                    st.error(f"⚠️ **Estoque Crítico:** O produto '{row['nome']}' zerou ou está no limite!")
            
            produtos_margem_baixa = df_produtos[df_produtos['margem_%'] < 30.0]
            if not produtos_margem_baixa.empty:
                for _, row in produtos_margem_baixa.iterrows():
                    st.warning(f"📉 **Atenção Financeira:** O produto '{row['nome']}' está com margem perigosa de {row['margem_%']}%. O ideal é acima de 30%.")
            
            if produtos_pausados.empty and produtos_margem_baixa.empty:
                st.success("Tudo certo! Estoque saudável e margens dentro do esperado.")
        else: st.info("Nenhum produto cadastrado.")

    with tab_crafting:
        st.subheader("🛠️ Engenharia de Cardápio (Montar Produto)")
        st.info("Junte os insumos para o sistema calcular o custo real da sua mercadoria.")
        
        if not df_produtos.empty and not df_insumos.empty:
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                st.markdown("**1. Selecionar Peças**")
                lista_prod = df_produtos.to_dict('records')
                prod_selecionado = st.selectbox("Qual Produto você está montando?", lista_prod, format_func=lambda x: f"ID {x['id']} - {x['nome']}")
                
                lista_ins = df_insumos.to_dict('records')
                insumo_selecionado = st.selectbox("Adicionar Insumo/Ingrediente:", lista_ins, format_func=lambda x: f"ID {x['id']} - {x['nome']}")
                
                qtd_usada = st.number_input(f"Quantidade usada (em {insumo_selecionado['medida']}):", min_value=0.01, step=1.0)
                if st.button("➕ Adicionar à Receita", type="primary"):
                    executar_query("INSERT INTO ficha_tecnica (id_produto, id_insumo, qtd_usada, id_loja) VALUES (?, ?, ?, ?)",
                                   (prod_selecionado['id'], insumo_selecionado['id'], qtd_usada, loja_atual))
                    calcular_custo_produto(prod_selecionado['id'], loja_atual)
                    st.success("Ingrediente adicionado e custo recalculado!")
                    st.rerun()
            
            with col_c2:
                st.markdown(f"**2. Ficha Técnica do: {prod_selecionado['nome']}**")
                conexao = sqlite3.connect("gerente_inteligente.db")
                query_ficha = """
                SELECT f.id as ID_Ficha, i.nome AS Insumo, f.qtd_usada AS Quantidade, i.medida AS Unidade, 
                       ROUND((i.custo / i.qtd_embalagem) * f.qtd_usada, 2) AS Custo_Calculado
                FROM ficha_tecnica f
                JOIN insumos i ON f.id_insumo = i.id
                WHERE f.id_produto = ? AND f.id_loja = ?
                """
                df_ficha = pd.read_sql(query_ficha, conexao, params=(prod_selecionado['id'], loja_atual))
                conexao.close()
                
                if not df_ficha.empty:
                    st.dataframe(df_ficha, use_container_width=True, hide_index=True)
                    custo_total = df_ficha['Custo_Calculado'].sum()
                    st.metric("Custo Total de Produção", f"R$ {custo_total:.2f}")
                    
                    st.markdown("---")
                    with st.expander("❌ Remover ingrediente desta receita"):
                        id_ficha_del = st.number_input("Digite o 'ID_Ficha' que deseja remover:", min_value=1, step=1, key="del_ficha")
                        if st.button("Remover da Ficha", type="primary"):
                            executar_query("DELETE FROM ficha_tecnica WHERE id = ? AND id_loja = ?", (id_ficha_del, loja_atual))
                            calcular_custo_produto(prod_selecionado['id'], loja_atual)
                            st.success("Ingrediente removido com sucesso!")
                            st.rerun()
                else:
                    st.warning("Este produto ainda não tem insumos vinculados. Custo atual: R$ 0,00.")
        else:
            st.warning("Você precisa ter pelo menos 1 Produto e 1 Insumo cadastrados para usar o Crafting.")

    with tab_insumos:
        st.subheader("Estoque Bruto (Insumos Comprados)")
        if not df_insumos.empty: st.dataframe(df_insumos, use_container_width=True, hide_index=True)
        else: st.info("Nenhum insumo.")

    with tab_caixa:
        st.subheader("Movimentações Financeiras")
        if not df_financeiro.empty:
            st.dataframe(df_financeiro, use_container_width=True, hide_index=True)
            st.metric(label="Faturamento Total", value=f"R$ {df_financeiro['valor'].sum():.2f}")
        else: st.info("Caixa vazio.")