# Agenda Nails API

API de agendamento para nail designer, com horários disponíveis e geração automática de mensagem para WhatsApp.

Projeto desenvolvido com FastAPI e SQLite, pensado tanto como portfólio quanto para uso real no dia a dia.

## Objetivo do Projeto

Criar um sistema simples de agendamento online para nail designer, permitindo que clientes escolham data, horário e serviço, gerando automaticamente uma mensagem pronta para envio via WhatsApp.

O projeto também demonstra habilidades em desenvolvimento backend com FastAPI.

## Tecnologias Utilizadas

- Python 3
- FastAPI
- SQLite
- Pydantic
- Uvicorn
- HTML

## Funcionalidades

- Página inicial com formulário de agendamento
- Listagem de horários disponíveis
- Criação de agendamentos
- Validação de conflitos de horário
- Geração automática de mensagem para WhatsApp
- Persistência de dados com SQLite

## Estrutura do Projeto

agenda-nails-api/
├── app.py
├── database.py
├── database.db
├── templates/
│   └── index.html
├── requirements.txt
└── README.md

## Como Executar o Projeto

### 1. Clonar o repositório

git clone https://github.com/wessil170/agenda-nails-api.git  
cd agenda-nails-api

### 2. Criar ambiente virtual

python3 -m venv venv  
source venv/bin/activate

### 3. Instalar dependências

pip install -r requirements.txt

### 4. Executar a aplicação

python -m uvicorn app:app --reload

### 5. Acessar no navegador

Página de agendamento:  
http://127.0.0.1:8000

Documentação Swagger:  
http://127.0.0.1:8000/docs

## Observação

Este projeto foi desenvolvido para uso real por uma nail designer, mas também serve como demonstração prática de um backend funcional com FastAPI para portfólio.

## Licença

Projeto de uso livre para fins educacionais e pequenos negócios.
