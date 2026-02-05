# 🌟 Star Wars API — PowerOfData

Uma API RESTful que permite explorar dados da saga Star Wars de forma rica e interativa. Construída com Python e hospedada no Google Cloud Functions.

---

## 📐 Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                        Cliente                              │
│         (Navegador / Postman / Aplicação Mobile)            │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   GCP API Gateway                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  • Rate Limiting                                    │   │
│  │  • Autenticação (API Key / JWT)                     │   │
│  │  • Logging & Monitoring                             │   │
│  │  • OpenAPI Documentation                            │   │
│  └─────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              GCP Cloud Functions (Python)                    │
│                                                             │
│  ┌──────────┐  ┌─────────────────────────────────────────┐ │
│  │  main.py │  │            Services Layer                 │ │
│  │ (Router) │─▶│  ┌──────────┐  ┌──────────┐            │ │
│  │          │  │  │Character │  │  Planet  │            │ │
│  │  • Auth  │  │  │ Service  │  │ Service  │            │ │
│  │  • CORS  │  │  └──────────┘  └──────────┘            │ │
│  │  • Erros │  │  ┌──────────┐  ┌──────────┐            │ │
│  └──────────┘  │  │Starship  │  │  Film    │            │ │
│                │  │ Service  │  │ Service  │            │ │
│  ┌──────────┐  │  └──────────┘  └──────────┘            │ │
│  │ Utils    │  └─────────────────┬───────────────────────┘ │
│  │ • Cache  │                    │                         │
│  │ • Auth   │  ┌─────────────────▼───────────────────────┐ │
│  │ • Valid. │  │         SWAPI Service (HTTP Client)      │ │
│  └──────────┘  │  • Cache (TTLCache)                      │ │
│                │  • Retry com Backoff Exponencial          │ │
│                │  • Tratamento de Erros                    │ │
│                └─────────────────┬───────────────────────┘ │
└──────────────────────────────────┼──────────────────────────┘
                                   │ HTTPS
                                   ▼
                    ┌───────────────────────────┐
                    │   SWAPI (swapi.dev/api)   │
                    │   Star Wars API Externa   │
                    └───────────────────────────┘
```

### Padrões e Princípios Utilizados

- **Clean Architecture** — separação clara entre camadas (Router → Services → HTTP Client)
- **Single Responsibility** — cada classe tem uma única responsabilidade
- **Dependency Injection** — serviços recebem suas dependências pelo construtor (facilita testes)
- **Repository Pattern** — `SWAPIService` é o único ponto de contato com a API externa
- **Decorator Pattern** — autenticação implementada como decorators (como `@PreAuthorize` no Spring)
- **Cache-Aside** — dados são buscados da fonte e cacheados automaticamente

---

## 📁 Estrutura do Projeto

```
starwars-api/
├── src/
│   ├── main.py                    # Entry point + Router
│   ├── config.py                  # Configurações centralizadas
│   ├── models/
│   │   └── schemas.py             # Modelos de dados (Pydantic)
│   ├── services/
│   |   ├── swapi/                 # Cliente HTTP do SWAPI, suas excessões e utils
|   |       ├── exceptions.py
|   |       ├── swapi_manager
|   |       ├── utils.py  
│   │   ├── character_service.py   # Lógica de personagens
│   │   ├── planet_service.py      # Lógica de planetas
│   │   ├── starship_service.py    # Lógica de naves
│   │   └── film_service.py        # Lógica de filmes
│   └── utils/
|       ├── auth/                  # Autenticação (JWT + API Key)
|           ├── api_key_manager.py # Gerenciador principal da API KEY
|           ├── decorators.py      # Decorators de validação
|           ├── exceptions.py      # Excessões personalizadas
|           ├── jwt_manager.py     # Gerenciador do Token JWT
|       ├── validators/            # Validadores de entrada
|           ├── character_validator.py 
|           ├── film_validator.py
|           ├── planet_validator.py
|           ├── starship_validator.py
|           ├── validator_manager.py
│       ├── cache.py               # Sistema de cache
├── deployment/
│   ├── cloud-function.yaml        # Config da Cloud Function
│   ├── api-gateway.yaml           # Config do API Gateway (OpenAPI)
│   └── deploy.sh                  # Script de deploy automático
├── docs/
│   └── architecture.md            # Documentação técnica detalhada
├── requirements.txt               # Dependências Python
├── .env                           # Variáveis de ambiente (não faz commit!)
├── .gitignore
└── README.md                      # Este arquivo
```

---

## 🚀 Como Rodar Localmente

### Pré-requisitos
- Python 3.9+
- pip

### Instalação

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd starwars-api

# 2. Crie ambiente virtual
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente (opcional — já tem valores padrão)
# Edite o arquivo .env se quiser mudar algo
```

### Rodando a API localmente

```bash
cd src
functions-framework --target=starwars_api --debug
```

A API estará em: **http://localhost:8080**

---

## 🔐 Autenticação

A API suporta dois métodos:

### 1. API Key (mais simples)
```bash
curl -H "X-API-Key: powerofdata-starwars-2025" http://localhost:8080/characters
```

### 2. JWT Token

**Passo 1 — Login:**
```bash
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

**Resposta:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 86400,
  "message": "Login bem-sucedido"
}
```

**Passo 2 — Usar o token:**
```bash
curl -H "Authorization: Bearer eyJ0eXAi..." http://localhost:8080/characters
```

**Passo 3 — Renovar token (antes de expirar):**
```bash
curl -X POST http://localhost:8080/auth/refresh \
  -H "Authorization: Bearer eyJ0eXAi..."
```

**Usuários de demo:**
| Usuário | Senha    |
|---------|----------|
| admin   | admin123 |
| user    | user123  |

---

## 📘 Endpoints

### Health Check
| Método | Endpoint | Auth | Descrição |
|--------|----------|------|-----------|
| GET | `/health` | ❌ | Verifica se a API está online |

### Personagens
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/characters` | Lista todos (com filtros) |
| GET | `/characters/{id}` | Busca por ID |
| GET | `/characters/{id}/films` | Filmes do personagem |
| GET | `/characters/{id}/starships` | Naves do personagem |
| GET | `/characters/{id}/homeworld` | Planeta natal |

### Planetas
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/planets` | Lista todos (com filtros) |
| GET | `/planets/{id}` | Busca por ID |
| GET | `/planets/{id}/residents` | Habitantes do planeta |
| GET | `/planets/{id}/films` | Filmes do planeta |

### Naves Espaciais
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/starships` | Lista todas (com filtros) |
| GET | `/starships/{id}` | Busca por ID |
| GET | `/starships/{id}/pilots` | Pilotos da nave |
| GET | `/starships/{id}/films` | Filmes da nave |

### Filmes
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/films` | Lista todos (com filtros) |
| GET | `/films/{id}` | Busca por ID |
| GET | `/films/{id}/characters` | Personagens do filme |
| GET | `/films/{id}/planets` | Planetas do filme |
| GET | `/films/{id}/starships` | Naves do filme |

### Busca Global
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/search?q=<termo>` | Busca em todos os recursos |

---

## 🔍 Parâmetros de Filtro e Ordenação

Todos os endpoints de lista suportam:

| Parâmetro | Tipo | Descrição | Exemplo |
|-----------|------|-----------|---------|
| `search` | string | Busca livre | `?search=Luke` |
| `sort_by` | string | Campo de ordenação | `?sort_by=name` |
| `order` | string | Direção: `asc` ou `desc` | `?order=desc` |
| `page` | int | Número da página (padrão: 1) | `?page=2` |
| `limit` | int | Itens por página (padrão: 10, máx: 100) | `?limit=20` |

**Campos de ordenação por recurso:**
- Personagens: `name`, `height`, `mass`, `birth_year`
- Planetas: `name`, `population`, `diameter`
- Naves: `name`, `model`, `cost_in_credits`, `length`, `crew`
- Filmes: `title`, `episode_id`, `release_date`

---

## 📋 Exemplos de Uso (curl)

```bash
# --- BÁSICOS ---
# Listar personagens
curl -H "X-API-Key: powerofdata-starwars-2025" http://localhost:8080/characters

# Buscar por nome
curl -H "X-API-Key: powerofdata-starwars-2025" "http://localhost:8080/characters?search=Luke"

# Busca por ID
curl -H "X-API-Key: powerofdata-starwars-2025" http://localhost:8080/characters/1

# --- FILTROS E ORDENAÇÃO ---
# Personagens do gênero masculino, ordenados por nome
curl -H "X-API-Key: powerofdata-starwars-2025" \
  "http://localhost:8080/characters?gender=male&sort_by=name&order=asc"

# Planetas com clima árido
curl -H "X-API-Key: powerofdata-starwars-2025" \
  "http://localhost:8080/planets?climate=arid"

# Naves ordenadas por custo (mais caras primeiro)
curl -H "X-API-Key: powerofdata-starwars-2025" \
  "http://localhost:8080/starships?sort_by=cost_in_credits&order=desc"

# Filmes ordenados por episódio
curl -H "X-API-Key: powerofdata-starwars-2025" \
  "http://localhost:8080/films?sort_by=episode_id&order=asc"

# --- CONSULTAS CORRELACIONADAS ---
# Filmes em que Luke aparece
curl -H "X-API-Key: powerofdata-starwars-2025" http://localhost:8080/characters/1/films

# Planeta natal do Luke
curl -H "X-API-Key: powerofdata-starwars-2025" http://localhost:8080/characters/1/homeworld

# Personagens do filme Episode IV
curl -H "X-API-Key: powerofdata-starwars-2025" http://localhost:8080/films/1/characters

# Habitantes de Tatooine
curl -H "X-API-Key: powerofdata-starwars-2025" http://localhost:8080/planets/1/residents

# Pilotos da X-wing
curl -H "X-API-Key: powerofdata-starwars-2025" http://localhost:8080/starships/12/pilots

# --- BUSCA GLOBAL ---
# Busca "Luke" em tudo
curl -H "X-API-Key: powerofdata-starwars-2025" "http://localhost:8080/search?q=Luke"

# Busca "Tatooine" só em planetas
curl -H "X-API-Key: powerofdata-starwars-2025" "http://localhost:8080/search?q=Tatooine&type=planets"

# --- PAGINAÇÃO ---
# Página 2 com 5 itens por página
curl -H "X-API-Key: powerofdata-starwars-2025" \
  "http://localhost:8080/characters?page=2&limit=5"
```

---

## ☁️ Deploy no GCP

### Opção 1 — Script automático
```bash
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

### Opção 2 — Manual
```bash
gcloud functions deploy starwars-api \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point starwars_api \
  --source ./src \
  --region us-central1 \
  --set-env-vars JWT_SECRET="sua-chave",API_KEY="sua-key"
```

### API Gateway
Após o deploy da Cloud Function, configure o API Gateway usando o arquivo `deployment/api-gateway.yaml` no console do GCP.

---

## 🔧 Tecnologias

| Tecnologia | Propósito |
|------------|-----------|
| Python 3.11 | Linguagem principal |
| Flask | Framework web (usado pelo Cloud Functions) |
| Pydantic | Validação e serialização de dados |
| PyJWT | Autenticação JWT |
| cachetools | Cache em memória com TTL |
| requests | Cliente HTTP |
| Google Cloud Functions | Hosting serverless |
| GCP API Gateway | Gateway de entrada |



---

## 🚀 Melhorias Futuras

Com mais tempo, implementaria:

1. **Banco de dados** — PostgreSQL no Cloud SQL para persistir dados e reduzir dependência da SWAPI
2. **Redis** — Cache distribuído com Cloud Memorystore em vez de cache em memória
3. **Rate Limiting** — limitar número de requisições por usuário/minuto
4. **Webhook/WebSocket** — notificações em tempo real
5. **GraphQL** — permitir queries mais flexíveis do cliente
6. **CI/CD** — pipeline automático de testes e deploy com Cloud Build
7. **Monitoring** — dashboards com Cloud Monitoring e alertas automáticos
8. **Versionamento de API** — `/v1/`, `/v2/` para evoluir sem quebrar clientes
9. **Documentação interativa** — Swagger UI hospedada junto com a API
10. **Autenticação OAuth2** — integração com Google OAuth para login mais seguro
11. **Adição de testes** - realizar a criação de testes para os services e demais funções com pytest
---

*Desenvolvido como parte do processo seletivo da PowerOfData — Desenvolvedor Back End Python*
