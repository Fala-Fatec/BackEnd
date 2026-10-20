# Guia Completo de Setup e Documentação: Backend Flask + Supabase + Docker

Este documento contém todo o código-fonte, configurações e documentação do ambiente backend Flask integrado ao banco de dados Supabase (PostgreSQL) usando Docker e Docker Compose.

---

## 1. Visão Geral da Arquitetura

O projeto é uma API RESTful desacoplada rodando em um container Docker isolado. A persistência de dados é feita via protocolo PostgreSQL direto para o banco Supabase em nuvem.

| Componente | Tecnologia | Função / Justificativa |
| :--- | :--- | :--- |
| **Runtime** | Python 3.11 (slim) | Imagem leve, estável e otimizada. |
| **Framework** | Flask 3.0.x | Microframework RESTful rápido e flexível. |
| **ORM** | Flask-SQLAlchemy 3.1.x | Mapeamento objeto-relacional e gerenciamento de sessões do banco. |
| **Driver BD** | `psycopg2-binary` | Conector nativo de alta performance para PostgreSQL. |
| **CORS** | `flask-cors` | Liberação de acessos Cross-Origin para integração com frontends. |
| **Variáveis de Env** | `python-dotenv` | Gestão segura de credenciais via `.env`. |
| **Banco de Dados** | Supabase (PostgreSQL) | Instância gerenciada PostgreSQL em nuvem. |
| **Conteinerização** | Docker & Docker Compose | Padronização e orquestração do ambiente. |

---

## 2. Estrutura de Arquivos

```text
meu-projeto/
├── app.py              # Aplicação principal, rotas e configuração do Flask
├── requirements.txt    # Dependências do projeto Python
├── Dockerfile          # Receita de build da imagem Docker
├── docker-compose.yml  # Orquestração do serviço e mapeamento de portas
├── .env                # Variáveis de ambiente e credenciais do Supabase
└── README.md           # Esta documentação
```

## 3. Passo a Passo de Execução

1. **Criar a pasta e salvar os arquivos:**
   Crie os 5 arquivos (`requirements.txt`, `.env`, `app.py`, `Dockerfile`, `docker-compose.yml`) na mesma pasta do seu projeto.

2. **Configurar o banco:**
   Insira a URL de conexão do Supabase dentro do arquivo `.env`.

3. **Subir o ambiente:**
   No terminal, execute:
   ```bash
   docker compose up --build
   ```

4. **Validar:**
   Acesse `http://localhost:5000` no navegador. A resposta deve ser:
   ```json
   {
     "message": "Conectado ao Supabase com sucesso!",
     "status": "sucesso"
   }
   ```

---

## 4. Endpoints Atuais

| Método | Rota | Descrição | Resposta (200) |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Healthcheck da API e validação da conexão com o banco. | `{"status": "sucesso", "message": "Conectado ao Supabase com sucesso!"}` |

---

## 5. Comandos Úteis do Docker

* **Subir em segundo plano:**
  ```bash
  docker compose up -d
  ```
* **Ver os logs da aplicação:**
  ```bash
  docker compose logs -f web
  ```
* **Parar os containers:**
  ```bash
  docker compose down
  ```
* **Reconstruir após alterar dependências:**
  ```bash
  docker compose up --build
  ```