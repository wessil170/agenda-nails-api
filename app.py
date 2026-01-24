from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import date, datetime
from typing import List
from urllib.parse import quote
from pathlib import Path

from database import criar_tabela, get_connection

# =====================
# CONFIGURAÇÕES
# =====================

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

# terça(1) a sábado(5)
DIAS_ATENDIMENTO = [1, 2, 3, 4, 5]

# =====================
# APP
# =====================

app = FastAPI(title="Agenda Nail Designer API")

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

criar_tabela()

# =====================
# MODELO
# =====================

class Agendamento(BaseModel):
    nome: str
    data: date
    horario: str
    servico: str

# =====================
# ROTAS
# =====================

@app.get("/", response_class=HTMLResponse)
def pagina_inicial(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/horarios")
def listar_horarios(data: str):
    data_obj = datetime.strptime(data, "%Y-%m-%d")
    dia_semana = data_obj.weekday()

    # Fora do horário de atendimento
    if dia_semana not in DIAS_ATENDIMENTO:
        return []

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT horario FROM agendamentos WHERE data = ?",
        (data,)
    )
    horarios_ocupados = {row[0] for row in cursor.fetchall()}
    conn.close()

    horarios_livres = [
        h for h in HORARIOS_FUNCIONAMENTO if h not in horarios_ocupados
    ]

    return horarios_livres

@app.post("/agendamentos")
def criar_agendamento(agendamento: Agendamento):

    if agendamento.horario not in HORARIOS_FUNCIONAMENTO:
        raise HTTPException(status_code=400, detail="Horário inválido")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM agendamentos WHERE data = ? AND horario = ?",
        (str(agendamento.data), agendamento.horario)
    )

    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Horário indisponível")

    cursor.execute(
        """
        INSERT INTO agendamentos (nome, data, horario, servico)
        VALUES (?, ?, ?, ?)
        """,
        (
            agendamento.nome,
            str(agendamento.data),
            agendamento.horario,
            agendamento.servico
        )
    )

    conn.commit()
    conn.close()

    mensagem = f"""
Olá! 😊
Me chamo {agendamento.nome} e gostaria de agendar um horário.

📅 Data: {agendamento.data}
⏰ Horário: {agendamento.horario}
💅 Serviço: {agendamento.servico}
""".strip()

    whatsapp_url = (
        "https://wa.me/5551991156840"
        f"?text={quote(mensagem)}"
    )

    return {
        "mensagem": "Agendamento criado com sucesso",
        "whatsapp_url": whatsapp_url
    }
