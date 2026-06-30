# 📊 Gerente Inteligente — Plataforma SaaS Multi-Tenant & Engenharia de CMV
*Um ecossistema completo em Python voltado para automação de estoque, inteligência de compras e controle preditivo de CMV para operações de e-commerce e delivery.*

> 📌 **Status do Projeto:** Fase 1 - Módulo 2 Concluído (Iniciando Módulo 3)

---

## 🎯 O Problema que este software resolve
Muitos pequenos negócios operam no "escuro" por não calcularem a margem real de seus produtos e por deixarem o estoque de insumos zerar, gerando rupturas. O **Gerente Inteligente** funciona como um sistema de gestão centralizado (SaaS) onde consultores e lojistas conseguem blindar a operação através de controle de acessos por cargos, precificação inteligente por engenharia de insumos (Ficha Técnica) e gestão contínua de fluxo de caixa.

## 🛠️ Tecnologias Utilizadas
* **Linguagem:** Python 3.x
* **Banco de Dados:** SQLite (Arquitetura Multi-Tenant com isolamento de dados por Loja/Filial)
* **Interface:** Streamlit (Layout responsivo em Dark Mode nativo)
* **Segurança:** Validação robusta de senhas (Regex contra engenharia social), motor matemático de CPF/CNPJ reais e controle de acesso baseado em regras (RBAC).

---

## 🗺️ Roadmap de Desenvolvimento do Sistema

A arquitetura do software foi dividida estrategicamente em **3 Fases**, contendo **3 Módulos** cada, visando escalabilidade e segurança de nível empresarial:

### 🧱 FASE 1: O Coração do SaaS & Motor Local
* **Módulo 1: Fundação & Segurança Multi-Tenant** `[CONCLUÍDO]`
  * Isolamento completo de tabelas por ID de Loja/Filial.
  * Hierarquia de cargos (Dono/ADM, Assistente ADM, Auxiliar ADM e Editor).
  * Onboarding manual "White-Glove" para consultoria.
  * *Painel Divindade*: Interface central invisível para controle de inadimplência (bloqueio de acesso) e Raio-X de dados dos clientes.
* **Módulo 2: Engenharia de Cardápio & CMV** `[CONCLUÍDO]`
  * Banco de dados e interface para gerenciamento de Insumos (Matérias-Primas).
  * Sistema de *Crafting* (Ficha Técnica) cruzando custo de embalagem fracionada com quantidade usada no produto final.
  * Alertas visuais automáticos de margem de lucro perigosa (abaixo de 30%).
* **Módulo 3: Visualização Avançada & Fechamento de Ciclo** `[EM DEFINIÇÃO]`
  * Estruturação de Dashboards visuais ou Relatórios gerenciais locais.

### ☁️ FASE 2: Hospedagem, Nuvem & Produção Real
* **Módulo 1: Migração de Banco de Dados** `[FUTURO]`
  * Preparação do banco para ambiente multi-usuário simultâneo.
* **Módulo 2: Deploy & Infraestrutura em Nuvem** `[FUTURO]`
  * Hospedagem do sistema em servidor real (Render/AWS/Google Cloud) para acesso externo via link.
* **Módulo 3: Otimização de Performance** `[FUTURO]`
  * Ajustes de velocidade de requisições e cache em nuvem.

### ⚡ FASE 3: Automações de Alto Nível & Ecossistema SaaS
* **Módulo 1: Integração de Gateways de Pagamento** `[FUTURO]`
  * Geração automática de PIX Copia e Cola para assinaturas da consultoria.
* **Módulo 2: Webhooks & Cobrança Automática** `[FUTURO]`
  * Comunicação direta com a API bancária para liberação e bloqueio automático de inadimplentes sem intervenção humana.
* **Módulo 3: Inteligência Preditiva** `[FUTURO]`
  * Relatórios consolidados e analytics avançados para tomada de decisão.

---
*Desenvolvido com foco na união entre Gestão Financeira Prática, Tecnologia Escalável e Consultoria de Alta Performance.*

---

## 👤 Desenvolvido por Adson Jr

```text
      / \__/\_
     /  _    _\
    |  / \  / \ |
    |  | o||o | |
    |  \__  _/  |
     \    V    /
      \  ___  /
       \/   \/
