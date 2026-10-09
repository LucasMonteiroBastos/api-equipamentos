# API de Equipamentos

API REST (CRUD) para cadastro de equipamentos industriais, feita com **FastAPI + SQLAlchemy + SQLite** e testada com **pytest**, com front-end em HTML/CSS/JavaScript puro.

## Telas

| Rota | Tela |
|---|---|
| `/` | **Cadastro**: formulário e tabela para cadastrar, editar, filtrar e excluir equipamentos |
| `/simulador` | **Simulador da API**: monta requisições do CRUD e mostra lado a lado o input (requisição) e o output (resposta), com histórico e cenários de erro (404, 409, 422) |
| `/docs` | Documentação interativa gerada pelo FastAPI (Swagger) |

## Stack

- **Back-end:** Python 3.12, FastAPI, SQLAlchemy 2, Pydantic 2
- **Banco:** SQLite (troca para PostgreSQL alterando `DATABASE_URL`)
- **Front-end:** HTML, CSS e JavaScript sem frameworks, servido pela própria API
- **Testes:** pytest + TestClient, com banco em memória isolado por teste

## Estrutura

```
app/
  database.py      # conexão com o banco
  models.py        # tabela equipamentos (SQLAlchemy)
  schemas.py       # validação de entrada e saída (Pydantic)
  main.py          # rotas do CRUD e das telas
  static/
    index.html     # tela de cadastro
    simulador.html # tela de input/output
tests/
  test_equipamentos.py
```

## Endpoints

| Método | Rota | Ação |
|---|---|---|
| POST | `/equipamentos` | Cadastra um equipamento |
| GET | `/equipamentos?status=&skip=&limit=` | Lista (com filtro e paginação) |
| GET | `/equipamentos/{id}` | Busca um equipamento |
| PATCH | `/equipamentos/{id}` | Atualiza parcialmente |
| DELETE | `/equipamentos/{id}` | Remove |

Regras: `tag` é única (409 se repetir), `status` aceita só `operando`, `manutencao` ou `parado` (422 se inválido), id inexistente retorna 404.

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abra http://127.0.0.1:8000 (cadastro) ou http://127.0.0.1:8000/simulador.

## Testes

```bash
pytest -v
```
