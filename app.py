from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import date, datetime
from urllib.parse import quote
from database import criar_tabela, get_connection
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI(title="Agenda Nail Designer API")
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
criar_tabela()

HORARIOS_FUNCIONAMENTO = [
    "10:00", "11:00", "13:00",
    "14:00", "15:00", "16:00",
    "17:00", "18:00"
]

DIAS_ATENDIMENTO = [1, 2, 3, 4, 5]  # terça a sábado


class Agendamento(BaseModel):
    nome: str
    data: date
    horario: str
    servico: str


@app.get("/horarios")
def listar_horarios(data: str):
    data_obj = datetime.strptime(data, "%Y-%m-%d")
    dia_semana = data_obj.weekday()

    if dia_semana not in DIAS_ATENDIMENTO:
        return {"horarios": []}

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT horario FROM agendamentos WHERE data = ?",
        (data,)
    )

    ocupados = [row[0] for row in cursor.fetchall()]
    conn.close()

    disponiveis = [
        h for h in HORARIOS_FUNCIONAMENTO if h not in ocupados
    ]

    return {"horarios": disponiveis}


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

    mensagem = f"""Olá! 😊
Me chamo {agendamento.nome} e gostaria de agendar um horário.

📅 Data: {agendamento.data}
⏰ Horário: {agendamento.horario}
💅 Serviço: {agendamento.servico}
"""

    return {
        "whatsapp_url": (
            "https://wa.me/5551991156840"
            f"?text={quote(mensagem)}"
        )
    }


@app.get("/", response_class=HTMLResponse)
def pagina_inicial():
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()
# =====================
# PAINEL ADMIN
# =====================

@app.get("/admin", response_class=HTMLResponse)
def painel_admin(request: Request):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, data, horario, servico
        FROM agendamentos
        ORDER BY data, horario
    """)
    agendamentos = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "agendamentos": agendamentos
        }
    )


@app.post("/admin/cancelar/{id}")
def cancelar_agendamento(id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM agendamentos WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return {"mensagem": "Agendamento cancelado"}
@app.post("/admin/agendamentos")
def criar_agendamento_admin(agendamento: Agendamento):

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

    return {"mensagem": "Agendamento criado com sucesso"}
