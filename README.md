# FastAPI do Zero 4.0
Repositório com o código que está sendo feito para o [Curso de FastAPI 4.0](https://fastapidozero.dunossauro.com/4.0/).

## Como rodar o projeto:
Este projeto usa a versão `3.12.*` do Python. Você pode instalar a versão correta com o [UV](https://docs.astral.sh/uv/):
```bash
uv python install 3.12
uv python pin 3.12
```

O projeto usa o [UV](https://docs.astral.sh/uv/) para gerenciar as dependências. Para instalar as dependências, execute:
```bash
uv sync
```

### Sobre os comandos:
Os comandos para executar funções do projeto são feitos com o [taskipy](https://github.com/taskipy/taskipy):
```bash
uv run task --list            # Lista os comandos disponíveis
uv run task migrate_generate  # Gera arquivos de migração do banco de dados
uv run task migrate_upgrade   # Executa as migrações do banco de dados
uv run task migrate <message> # Gera e executa uma migração do banco de dados
uv run task dev               # Roda o servidor de desenvolvimento
uv run task test              # Roda os testes
uv run task clean             # Limpa os arquivos temporários
uv run task lint              # Roda o linter
uv run task lint --fix        # Roda o linter e tenta corrigir os problemas
uv run task format            # Formata o código
```

### Setup para rodar o projeto:
Crie um arquivo `.env` na raiz do projeto.

Você pode copiar o conteúdo do arquivo `.env.example` e ajustar as variáveis de ambiente:
```bash
DATABASE_URL="postgresql+psycopg://app_user:app_password@localhost:5432/app_db"
SECRET_KEY="super-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### Para rodar o projeto:
```bash
docker compose up fastzero_database -d  # Inicia o banco de dados
uv sync                                 # Instala as dependências
uv run task migrate_upgrade             # Executa as migrações do banco de dados
uv run task dev                         # Roda o servidor de desenvolvimento
```
