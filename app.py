from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request

import sqlite3
from database import criar_tabela, get_connection

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import date
from urllib.parse import quote

from datetime import datetime

HORARIOS_FUNCIONAMENTO = [
    "10:00",
    "11:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00"
]

DIAS_ATENDIMENTO = [1, 2, 3, 4, 5]  # terça(1) a sábado(5)

app = FastAPI(title="Agenda Nail Designer API")
criar_tabela()


# 📌 Modelo de dados
class Agendamento(BaseModel):
    nome: str
    data: date
    horario: str
    servico: str


# 📌 Listar horários disponíveis
@app.get("/horarios")
def listar_horarios(data: str):
    data_obj = datetime.strptime(data, "%Y-%m-%d")
    dia_semana = data_obj.weekday()

    # Se não for dia de atendimento, retorna vazio
    if dia_semana not in DIAS_ATENDIMENTO:
        return []

    # Por enquanto, retorna todos os horários do salão
    return HORARIOS_FUNCIONAMENTO


# 📌 Criar agendamento e gerar link do WhatsApp
@app.post("/agendamentos")
def criar_agendamento(agendamento: Agendamento):
     if agendamento.horario not in HORARIOS_FUNCIONAMENTO:
       raise HTTPException(status_code=400, detail="Horário inválido")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM agendamentos
        WHERE data = ? AND horario = ?
    """, (str(agendamento.data), agendamento.horario))

    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Horário indisponível")

    cursor.execute("""
        INSERT INTO agendamentos (nome, data, horario, servico)
        VALUES (?, ?, ?, ?)
    """, (
        agendamento.nome,
        str(agendamento.data),
        agendamento.horario,
        agendamento.servico
    ))

    conn.commit()
    conn.close()

    mensagem = f"""
Olá! 😊
Me chamo {agendamento.nome} e gostaria de agendar um horário.

📅 Data: {agendamento.data}
⏰ Horário: {agendamento.horario}
💅 Serviço: {agendamento.servico}
""".strip()

    mensagem_codificada = quote(mensagem)

    whatsapp_url = (
        "https://wa.me/5551991156840"
        f"?text={mensagem_codificada}"
    )

    return {
        "mensagem": "Agendamento criado com sucesso",
        "whatsapp_url": whatsapp_url
    }

@app.get("/", response_class=HTMLResponse)
def pagina_inicial():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return f.read()
