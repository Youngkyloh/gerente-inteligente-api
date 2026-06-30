# 📊 Gerente Inteligente — API & Motor de Caixa SaaS
*Um ecossistema em Python voltado para automação de estoque, inteligência de compras e controle preditivo de CMV para operações de e-commerce e delivery.*

> ⚠️ **Status do Projeto:** Em Desenvolvimento (Fase 2 - Motor de CMV e Precificação)

## 🎯 O Problema que este software resolve
Muitos pequenos negócios perdem dinheiro por não calcularem a margem real de seus produtos e por deixarem o estoque de insumos zerar. O **Gerente Inteligente** atua como um backend em nuvem que previne rupturas de estoque e precifica produtos de forma dinâmica, operando em um modelo SaaS (Software as a Service) Multi-Tenant.

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.x
* **Banco de Dados:** SQLite (Arquitetura Multi-Tenant para múltiplas lojas)
* **Segurança:** RBAC (Controle de Acesso Baseado em Cargos) e validação de senhas fortes.
* **Interface:** Streamlit (Dark Mode nativo)

## 🚀 Módulos da Arquitetura

- [x] **Módulo 1: Fundação SaaS (Concluído)**
  - Banco de Dados Multi-Tenant (Separação de dados por Loja/Filial).
  - Autenticação Segura com motor de senhas fortes (Regex).
  - RBAC: Níveis hierárquicos (Dono, Assistente, Auxiliar, Editor).
  - Onboarding "White-Glove": Criação de contas gerida pela consultoria.
  - *Painel Divindade*: Visão global invisível para gestão de assinaturas, bloqueio de inadimplentes e Raio-X de clientes.
  
- [ ] **Módulo 2: Motor de cálculo de CMV e Margem de Lucro Bruto (Em andamento)**
  - Engenharia de Ficha Técnica (Insumos vs. Produto Final).
  - Precificação Dinâmica.

- [ ] **Módulo 3: Integrações Financeiras (Futuro)**
  - Baixa automática de assinaturas via Webhook (APIs de pagamento).

---
*Desenvolvido para unir Gestão Financeira, Controle Operacional e Tecnologia.*