# Raízes do Nordeste - API Backend

# Sobre o projeto
API REST para gestão da rede de restaurantes Raízes do Nordeste.

Fluxo crítico: um cliente se cadastra, aceita os termos de fidelização, monta um pedido a partir do cardápio de uma unidade, paga o pedido e recebe pontos de fidelização automaticamente quando o pagamento é aprovado. Em paralelo, funcionários (ADMIN, GERENTE, ATENDENTE, COZINHA) autenticam via JWT e operam o cardápio, estoque e avanço/cancelamento de pedidos.

# Links e evidências
- Repositório: https://github.com/WisterianWell/raizes_nordeste_backend
- Swagger local: http://localhost:8000/docs (Swagger)
- Coleção Postman: docs/postman/raizes-nordeste.postman_collection.json

# Requisitos
- Python 3.13
- PostgreSQL 16
- Docker e Docker Compose
- Dependências Python (requirements.txt): FastAPI, SQLAlchemy 2.0 (asyncpg), Pydantic v2, PyJWT, pwdlib/Argon2, Uvicorn

# Variáveis de ambiente
O arquivo .env é obrigatório. Crie-o a partir do exemplo:
```bash
cp .env.example .env
```

# Como iniciar o Docker
```bash
docker compose up -d --build
```

# Instalação das dependências
```bash
python -m venv .venv

.venv\Scripts\activate

pip install -r requirements.txt
```

# Como iniciar a API
```bash
uvicorn app.main:app --reload
```
A API fica disponível em http://localhost:8000/docs

# Como resetar o banco de dados
```bash
docker compose down -v
```

# Fluxo inicial da API (Swagger)
Reproduza essas etapas antes de testar o fluxo critico de pedidos e movimentaçóes de estoque:
- Autenticar-se no canto superior direito com as credenciais padrão de admin (admin@raizesnordeste.com) (senhaprovisoria).
- Criar uma unidade do restaurante.
- Criar Produtos globais.
- Adicionar esses produtos ao cardápio da unidade.

Fluxo de realização de pedidos:
- Cadastrar um cliente.
- Autenticar-se como cliente.
- Aceitar os termos de fidelização (opcional).
- Criar um pedido (id_cliente é opcional caso o cliente autenticado esteja criando o pedido).
- Realizar pagamento (preencha o campo force_status com APROVADO ou RECUSADO para testar os dois cenários).
- Consultar o saldo de pontos após o aprovamento do pagamento (opcional).
- Listar o pedido para conferir o status do pedido.
- Autenticar-se como funcionário (admin ou crie um funcionário nessa unidade).
- Avançar o status do pedido pelo endpoint em pedidos.


# Como rodar os testes Postman
Pré-requisitos:
- API no ar em http://localhost:8000.
- .env com valores padrão.
- importe docs/postman/raizes-nordeste.postman_collection.json para o postman.
- Ajuste a variável de coleção baseUrl se a API não estiver em http://localhost:8000.
- Rode manualmente pasta por pasta na ordem dos testes ou use Collection Runner.
- A coleção espera um banco vazio (os cadastros usam e-mails fixos). Para rodar novamente, recrie o banco de dados e suba a API de novo.


# Estrutura do projeto
app/
├── api/            # Routers do FastAPI
│   └── v1/routers/ 
├── core/           # Configuração e segurança
├── domain/         # Regras de negócio: enums, cargos e validações             
├── exceptions/     # Exceções customizadas, códigos de erro e handlers globais                  
├── gateways/       # Integração com gateway externo
├── models/         # Entidades SQLAlchemy
├── repositories/   # Repositórios
├── schemas/        # DTOs Pydantic de request/respons
├── services/       # Services (casos de uso)
├── database.py     # Gerenciador da sessão assíncrona do SQLAlchemy
├── dependencies.py # Autenticação (JWT) e autorização
└── main.py         # Factory da aplicação
docs/
└── postman/        # Coleção Postman com os cenários de teste
