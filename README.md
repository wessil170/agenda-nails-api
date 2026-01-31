# Agenda Nails API

API REST para agendamento de serviços de nail designer, desenvolvida com **FastAPI**, simulando um sistema real de agenda profissional.

O projeto foi criado com foco em **boas práticas de backend**, **organização de código**, **validação de dados** e **regras de negócio**, sendo ideal para compor portfólio de desenvolvimento backend.

---

## Visão Geral

Esta API permite gerenciar agendamentos de clientes, controlando datas e horários disponíveis, evitando conflitos de agenda e possibilitando a administração dos horários marcados.

O sistema simula um cenário real utilizado por profissionais autônomos da área da beleza, como nail designers.

---

## Objetivos do Projeto

* Praticar o desenvolvimento de APIs REST com FastAPI
* Implementar operações CRUD completas
* Aplicar validação de dados com Pydantic
* Trabalhar regras de negócio reais (bloqueio de horários)
* Criar um projeto backend organizado para portfólio

---

## Tecnologias Utilizadas

* Python 3
* FastAPI
* Pydantic
* SQLite
* Uvicorn

---

## Funcionalidades

* Criar agendamentos
* Listar todos os agendamentos
* Atualizar agendamento por ID
* Remover agendamento por ID
* Bloqueio automático de horários já ocupados
* Validação automática dos dados enviados

---

## Regras de Negócio

* Não é permitido criar dois agendamentos no mesmo dia e horário
* Horários já ocupados são automaticamente bloqueados
* Agendamentos podem ser cancelados

---

## Estrutura do Projeto

```
agenda-nails-api/
├── app/
│   ├── app.py
├── requirements.txt
├── README.md
```

---

## Como Executar o Projeto

### 1. Clonar o repositório

```
git clone https://github.com/wessil170/agenda-nails-api.git
cd agenda-nails-api
```

### 2. Criar ambiente virtual

```
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar as dependências

```
pip install -r requirements.txt
```

### 4. Executar a aplicação

```
uvicorn app.app:app --reload
```

---

## Acessar a API

* Documentação interativa (Swagger):

  * [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* Documentação alternativa (ReDoc):

  * [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Exemplo de Requisição

### Criar um agendamento

**POST** `/appointments`

```json
{
  "nome": "Maria Silva",
  "data": "2026-02-10",
  "horario": "14:00",
  "telefone": "51999999999"
}
```

---

## Observações

Este projeto foi desenvolvido para fins de estudo e portfólio, simulando um sistema real de agendamento utilizado por profissionais autônomos.

---

## Licença

Este projeto é de uso livre para fins educacionais e de portfólio.
