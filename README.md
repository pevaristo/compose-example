# Exemplo Docker Compose: Flask + Redis

Este é um projeto de demonstração que utiliza **Docker**, **Docker Compose**, **Python (Flask)** e **Redis** para criar uma aplicação web simples com contagem de visualizações persistida em cache.

---

## Tecnologias Utilizadas

- **Flask**: Microframework web em Python responsável por renderizar as páginas.
- **Redis**: Banco de dados em memória utilizado como cache para armazenar o contador de visualizações (`views`).
- **Docker & Docker Compose**: Ferramentas para empacotar e gerenciar os containers da aplicação de forma isolada e integrada.

---

## Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:
1. **Docker**: Plataforma de containerização.
2. **Docker Compose**: Geralmente já vem integrado com o Docker Desktop (Windows/macOS) ou instalado junto ao Docker Engine (Linux).

Para verificar se estão instalados corretamente, execute no seu terminal:
```bash
docker --version
docker compose version
```

---

## Como Executar pela Primeira Vez

Siga os passos abaixo para rodar o projeto em seu ambiente local:

### 1. Configurar as variáveis de ambiente
O projeto possui um arquivo de exemplo `.env.example`. Crie uma cópia dele chamada `.env` (o arquivo `.env` padrão já vem configurado, mas você pode ajustá-lo se necessário):

No Linux / macOS:
```bash
cp .env.example .env
```

No Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```

O arquivo `.env` define configurações como a porta da aplicação (`APP_PORT=8000`).

### 2. Construir e iniciar os containers
Execute o comando do Docker Compose para construir a imagem da aplicação e subir todos os serviços definidos (`web` e `redis`):

```bash
docker compose up --build
```

*(Nota: O parâmetro `--build` força a criação da imagem da aplicação baseada no Dockerfile pela primeira vez).*

### 3. Acessar a aplicação
Abra seu navegador e acesse:
**http://localhost:8000** *(ou a porta definida na variável `APP_PORT` do seu `.env`)*

Cada vez que você inicia o jogo, você escolhe uma figura mentalmente e responde se ela aparece nos cartões binários. O sistema adivinha sua figura perfeitamente! Adicionalmente, a rota `/ola` demonstra um exemplo simples de contador de visualizações persistido no Redis.

---

## Comandos Úteis do Docker Compose

Aqui estão os principais comandos utilizados no dia a dia com este projeto:

- **Iniciar com modo Watch (Desenvolvimento):**
  ```bash
  docker compose up --build --watch
  ```
  *Monitora alterações nos arquivos locais (como `app.py` ou templates) e atualiza automaticamente o container.*

- **Visualizar os logs em tempo real:**
  ```bash
  docker compose logs -f
  ```

- **Consultar o valor do contador diretamente no Redis:**
  ```bash
  docker compose exec redis redis-cli GET views
  ```

- **Parar os containers:**
  ```bash
  docker compose down
  ```

- **Parar e remover volumes (limpa os dados salvos no Redis):**
  ```bash
  docker compose down -v
  ```
  
- **Executar os testes:**
  ```bash
  docker compose exec web pytest
  ```
  

- **Verificar a sintaxe e configuração do compose:**
  ```bash
  docker compose config
  ```

---

## Aprofundando os Conhecimentos

Para quem está utilizando Docker, Docker Compose e Redis pela primeira vez, este projeto traz conceitos essenciais da arquitetura de microsserviços e containers. Abaixo estão os principais pontos para entender como tudo se conecta:

### 1. Arquitetura da Aplicação
O Docker Compose cria uma rede privada isolada onde os containers conversam entre si usando os nomes dos serviços definidos no arquivo `docker-compose.yml`:

```text
[ Navegador ] 
      │
      ▼ (Porta 8000 mapeada para 5000)
┌────────────────────────────────────────┐
│ Container: web (Flask)                 │
│  - Executa app.py                      │
│  - Lê REDIS_HOST=redis                 │
└────────────────────────────────────────┘
      │
      │ (Rede interna Docker: porta 6379)
      ▼
┌────────────────────────────────────────┐
│ Container: redis (Redis Alpine)        │
│  - Armazena contador de visualizações  │
│  - Volume persistente (redis-data)     │
└────────────────────────────────────────┘
```

### 2. Conceitos-Chave no `docker-compose.yml`

- **Nomes de Serviço como Hostnames**: No código do Flask (`app.py`), a conexão com o Redis usa `host="redis"` (`os.getenv("REDIS_HOST", "redis")`). Como o serviço no Compose chama-se `redis`, o Docker resolve automaticamente esse nome para o IP interno do container do Redis, sem precisar de IPs fixos.
- **Healthcheck (`service_healthy`)**: O serviço `web` possui a diretiva `depends_on` configurada com `condition: service_healthy`. Isso garante que o Flask só inicialize após o container do Redis ter iniciado completamente e respondido com sucesso ao comando `redis-cli ping`. Isso evita erros de conexão (`ConnectionRefusedError`) durante o boot.
- **Modo Watch (`docker compose up --watch`)**: Configurado na seção `develop.watch`, o Docker monitora alterações nos arquivos locais. Se você editar o código Python ou o HTML, o Docker atualiza ou reinicia o container automaticamente, agilizando o desenvolvimento.
- **Volumes Persistentes (`redis-data`)**: O Redis salva seus dados no volume `redis-data`. Isso significa que mesmo se você derrubar os containers (`docker compose down`), o contador de visualizações não será perdido. Para apagar os dados e zerar o contador, é necessário remover os volumes explicitamente (`docker compose down -v`).

### 3. Solução de Problemas Comuns (Troubleshooting)

- **Erro de Porta em Uso (`Bind for 0.0.0.0:8000 failed`)**:
  Se a porta 8000 já estiver ocupada no seu computador, abra o arquivo `.env` e altere a variável `APP_PORT` para outra porta livre (ex: `APP_PORT=5050`).
- **Como resetar tudo (Zerar o contador e reconstruir)**:
  Se quiser reiniciar o ambiente completamente limpo (apagando o cache do Redis e recriando as imagens):
  ```bash
  docker compose down -v --rmi local
  ```
- **Permissões no Linux**:
  Caso receba erros de permissão ao rodar comandos `docker`, verifique se seu usuário está no grupo docker ou utilize `sudo docker compose ...` (conforme as configurações da sua distribuição).
