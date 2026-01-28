from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel
from datetime import date, datetime, timedelta
from urllib.parse import quote
from pathlib import Path

from database import criar_tabela, get_connection

app = FastAPI(title="Agenda Nail Designer")

BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")

criar_tabela()

# 🔹 Serviços com preço e duração (em minutos)
SERVICOS = {
    "Pé": {"preco": 35, "duracao": 60},
    "Mão": {"preco": 30, "duracao": 60},
    "Pé e mão": {"preco": 55, "duracao": 120},
    "Esmaltação em gel pé": {"preco": 70, "duracao": 90},
    "Esmaltação em gel mão": {"preco": 65, "duracao": 90},
    "Alongamento soft gel": {"preco": 100, "duracao": 180},
    "Manutenção": {"preco": 70, "duracao": 120},
}

HORARIOS_FUNCIONAMENTO = [
    "10:00","11:00","12:00",
    "13:00","14:00","15:00",
    "16:00","17:00","18:00"
]

DIAS_ATENDIMENTO = [1,2,3,4,5]  # terça a sábado

class Agendamento(BaseModel):
    nome: str
    data: date
    horario: str
    servico: str

# 🔹 Página cliente
@app.get("/", response_class=HTMLResponse)
def pagina_inicial():
    with open(BASE_DIR / "templates" / "index.html", encoding="utf-8") as f:
        return f.read()

# 🔹 Listar serviços
@app.get("/servicos")
def listar_servicos():
    return list(SERVICOS.keys())

# 🔹 Horários disponíveis considerando duração
@app.get("/horarios")
def listar_horarios(data: str):
    data_obj = datetime.strptime(data, "%Y-%m-%d")
    if data_obj.weekday() not in DIAS_ATENDIMENTO:
        return []

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT horario, servico FROM agendamentos WHERE data = ?",
        (data,)
    )
    agendados = cursor.fetchall()
    conn.close()

    ocupados = set()

    for horario, servico in agendados:
        duracao = SERVICOS[servico]["duracao"]
        inicio = datetime.strptime(horario, "%H:%M")
        blocos = duracao // 60

        for i in range(blocos):
            ocupados.add((inicio + timedelta(hours=i)).strftime("%H:%M"))

    return [h for h in HORARIOS_FUNCIONAMENTO if h not in ocupados]

# 🔹 Criar agendamento
@app.post("/agendamentos")
def criar_agendamento(a: Agendamento):
    if a.servico not in SERVICOS:
        raise HTTPException(400, "Serviço inválido")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM agendamentos WHERE data=? AND horario=?",
        (str(a.data), a.horario)
    )
    if cursor.fetchone():
        conn.close()
        raise HTTPException(400, "Horário indisponível")

    cursor.execute(
        "INSERT INTO agendamentos (nome, data, horario, servico) VALUES (?,?,?,?)",
        (a.nome, str(a.data), a.horario, a.servico)
    )

    conn.commit()
    conn.close()

    msg = f"""Olá 😊
Sou {a.nome} e gostaria de confirmar meu agendamento:

📅 Data: {a.data}
⏰ Horário: {a.horario}
💅 Serviço: {a.servico}
"""

    return {
        "whatsapp_url": "https://wa.me/5551991156840?text=" + quote(msg)
    }
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

    # 🔹 calcular total do dia
    total_dia = 0
    for _, _, _, _, servico in agendamentos:
        total_dia += SERVICOS[servico]["preco"]

    conn.close()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "agendamentos": agendamentos,
            "servicos": SERVICOS.keys(),
            "total_dia": total_dia
        }
    )


@app.post("/admin/agendamentos")
def criar_agendamento_admin(a: Agendamento):
    if a.servico not in SERVICOS:
        raise HTTPException(400, "Serviço inválido")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM agendamentos
        WHERE data = ? AND horario = ?
    """, (str(a.data), a.horario))

    if cursor.fetchone():
        conn.close()
        raise HTTPException(400, "Horário indisponível")

    cursor.execute("""
        INSERT INTO agendamentos (nome, data, horario, servico)
        VALUES (?, ?, ?, ?)
    """, (a.nome, str(a.data), a.horario, a.servico))

    conn.commit()
    conn.close()

    return {"ok": True}


@app.post("/admin/cancelar/{id}")
def cancelar_agendamento(id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM agendamentos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return {"ok": True}
