## Projeto de Upload e Processamento de Arquivos JSON

Este projeto implementa uma solução que permite o upload de um arquivo JSON via API, persiste os dados no MongoDB, e processa-os de forma assíncrona utilizando RabbitMQ para enviá-los ao MySQL. A API foi desenvolvida com FastAPI e suporta o envio de JSON tanto via upload de arquivo quanto diretamente no corpo da requisição. O ambiente é configurado utilizando Docker Compose.

### Estrutura do Projeto

A estrutura do projeto pode ser organizada da seguinte forma:
```.
├── docker-compose.yml
├── api
│   ├── Dockerfile
│   ├── main.py
│   ├── models.py
│   ├── services.py
│   ├── consumers.py
│   ├── logs
│   │   └── app.log
│   └── tests
│       └── test_api.py
├── mongo
│   └── Dockerfile
├── rabbitmq
│   └── Dockerfile
├── mysql
│   └── Dockerfile
└── README.md
```

### Requisitos
Docker
Docker Compose

### Passo a Passo
1. Instalação do Docker e Docker Compose
Se você ainda não tem o Docker e o Docker Compose instalados, siga as instruções abaixo:

No Ubuntu/Debian:

## Atualize o sistema
```sudo apt update```

## Instale o Docker
```sudo apt install docker.io```

## Instale o Docker Compose
```sudo apt install docker-compose```

## Adicione seu usuário ao grupo docker (para evitar usar sudo)
```sudo usermod -aG docker $USER```

## Reinicie o sistema ou faça logout/login para aplicar as mudanças
No Windows ou macOS:
Baixe e instale o Docker Desktop. O Docker Compose já está incluído no Docker Desktop.

2. Clone o Repositório
Clone este repositório para o seu ambiente local:
```git clone https://github.com/eliabeferreira21/poc-api-json.git```
```cd poc-api-json```

3. Configuração do Ambiente
O ambiente é configurado utilizando Docker Compose. O arquivo docker-compose.yml já está preparado para subir todos os serviços necessários: FastAPI, MongoDB, RabbitMQ e MySQL.

4. Executando a Aplicação
Para subir a aplicação, execute o seguinte comando na raiz do projeto:


```docker-compose up --build```
Isso irá:

Construir as imagens Docker necessárias.

Subir os contêineres para a API, MongoDB, RabbitMQ e MySQL.

Expor a API no endereço http://localhost:8000.

5. Testando a API
A API estará disponível em http://localhost:8000. Você pode testá-la utilizando o Swagger UI, que é gerado automaticamente pelo FastAPI, acessando http://localhost:8000/docs.

Exemplo de Upload de Arquivo JSON
Crie um arquivo JSON com o seguinte formato:

```
[
    {
        "name": "João Silva",
        "email": "joao.silva@example.com",
        "age": 30
    },
    {
        "name": "Maria Oliveira",
        "email": "maria.oliveira@example.com",
        "age": 25
    }
]
```
No Swagger UI, utilize o endpoint /upload/ para fazer o upload do arquivo JSON.

Após o upload, os dados serão persistidos no MongoDB e uma mensagem será enviada para o RabbitMQ. O consumidor processará a mensagem e inserirá os dados no MySQL.

Exemplo de Envio de JSON via Body
Você também pode enviar o JSON diretamente no corpo da requisição:

```
curl -X POST "http://localhost:8000/upload/" \
     -H "accept: application/json" \
     -H "Content-Type: application/json" \
     -d '[
           {
             "name": "Carlos Souza",
             "email": "carlos.souza@example.com",
             "age": 40
           }
         ]'
```

Exemplos de Envio JSON via Arquivo (Multipart Form)

```
curl -X POST "http://localhost:8000/upload/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@path/to/your/file.json"
```
6. Testes Automatizados
Os testes automatizados cobrem toda a aplicação, incluindo a persistência dos dados no MongoDB e no MySQL. Para executar os testes, utilize o seguinte comando: ```docker-compose exec api pytest api/tests/test_integration.py -v```
O que os testes verificam?
Upload e Persistência no MongoDB:

Verifica se o arquivo JSON é corretamente enviado para a API.

Confirma se os dados são persistidos no MongoDB.

Envio de Mensagem para o RabbitMQ:

Verifica se uma mensagem contendo o ID do MongoDB é enviada para a fila do RabbitMQ.

Processamento Assíncrono e Persistência no MySQL:

Simula o consumo da mensagem pelo RabbitMQ.

Verifica se os dados são corretamente persistidos no MySQL.

Envio de JSON via Body:

Verifica se o JSON enviado diretamente no corpo da requisição é processado corretamente.

Erro quando nenhum JSON é fornecido:

Verifica se a API retorna um erro quando nenhum JSON é enviado.

7. Verificando os Logs
Os logs da aplicação são armazenados no diretório api/logs/app.log. Eles registram todas as operações, incluindo sucessos e falhas no upload, processamento do RabbitMQ e inserções no MySQL.

8. Parando a Aplicação
Para parar a aplicação e remover os contêineres, execute:


docker-compose down
9. Limpeza de Dados
Se desejar remover os volumes persistentes (dados do MongoDB e MySQL), utilize:


```docker-compose down -v```
Estrutura do Projeto
api/: Contém o código da API FastAPI, testes e logs.

mongo/: Configuração do MongoDB.

rabbitmq/: Configuração do RabbitMQ.

mysql/: Configuração do MySQL.

docker-compose.yml: Arquivo de configuração do Docker Compose.

Testes Automatizados
Os testes automatizados estão localizados no diretório api/tests/ e cobrem:

Persistência no MongoDB:

Verifica se os dados do arquivo JSON são corretamente armazenados no MongoDB.

Envio de Mensagens para o RabbitMQ:

Garante que as mensagens são enviadas corretamente para a fila do RabbitMQ.

Persistência no MySQL:

Verifica se os dados são corretamente processados e inseridos no MySQL após o consumo da mensagem do RabbitMQ.

Envio de JSON via Body:

Verifica se o JSON enviado diretamente no corpo da requisição é processado corretamente.

Validação de Erros:

Verifica se a API retorna erros adequados quando nenhum JSON é fornecido.