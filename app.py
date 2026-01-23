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

app = FastAPI(title="Agenda Nail Designer API")
criar_tabela()


# 📌 Modelo de dados
class Agendamento(BaseModel):
    nome: str
    data: date
    horario: str
    servico: str


# 📌 Horários fixos (MVP)
HORARIOS_FIXOS = [
    "09:00", "10:00", "11:00",
    "13:00", "14:00", "15:00",
    "16:00"
]

agendamentos: List[Agendamento] = []


# 📌 Listar horários disponíveis
@app.get("/horarios")
def listar_horarios():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT horario FROM agendamentos")
    ocupados = {row[0] for row in cursor.fetchall()}

    conn.close()

    disponiveis = [h for h in HORARIOS_FIXOS if h not in ocupados]

    return {"horarios_disponiveis": disponiveis}


# 📌 Criar agendamento e gerar link do WhatsApp
@app.post("/agendamentos")
def criar_agendamento(agendamento: Agendamento):

    if agendamento.horario not in HORARIOS_FIXOS:
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
