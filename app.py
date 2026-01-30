from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from datetime import date, datetime, timedelta
from pathlib import Path
from collections import defaultdict
from urllib.parse import quote

from database import criar_tabela, get_connection

# =====================
# APP
# =====================

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Agenda Nail Designer")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

criar_tabela()

# =====================
# CONFIGURAÇÕES
# =====================

HORARIOS_BASE = [
    "10:00","11:00","12:00",
    "13:00","14:00","15:00",
    "16:00","17:00","18:00"
]

DIAS_ATENDIMENTO = [1,2,3,4,5]  # terça a sábado

SERVICOS = {
    "Pé": {"preco": 35, "duracao": 60},
    "Mão": {"preco": 30, "duracao": 60},
    "Pé e mão": {"preco": 55, "duracao": 120},
    "Esmaltação em gel pé": {"preco": 70, "duracao": 90},
    "Esmaltação em gel mão": {"preco": 65, "duracao": 90},
    "Alongamento soft gel": {"preco": 100, "duracao": 180},
    "Manutenção": {"preco": 70, "duracao": 120},
}

# =====================
# MODELO
# =====================

class Agendamento(BaseModel):
    nome: str
    data: date
    horario: str
    servico: str

# =====================
# UTIL
# =====================

def calcular_hora_fim(hora_inicio, duracao_min):
    h = datetime.strptime(hora_inicio, "%H:%M")
    return (h + timedelta(minutes=duracao_min)).strftime("%H:%M")

def intervalo_conflita(inicio1, fim1, inicio2, fim2):
    return not (fim1 <= inicio2 or inicio1 >= fim2)

# =====================
# CLIENTE
# =====================

@app.get("/", response_class=HTMLResponse)
def cliente(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "servicos": SERVICOS.keys()}
    )

@app.get("/horarios")
def horarios(data: str):
    data_obj = datetime.strptime(data, "%Y-%m-%d")
    if data_obj.weekday() not in DIAS_ATENDIMENTO:
        return {"horarios": []}

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT hora_inicio, hora_fim FROM agendamentos WHERE data = ?
    """, (data,))
    ocupados = cursor.fetchall()
    conn.close()

    livres = []
    for h in HORARIOS_BASE:
        inicio = h
        fim = (datetime.strptime(h,"%H:%M")+timedelta(minutes=30)).strftime("%H:%M")

        conflito = any(
            intervalo_conflita(inicio, fim, oi, of)
            for oi, of in ocupados
        )
        if not conflito:
            livres.append(h)

    return {"horarios": livres}

@app.post("/agendamentos")
def criar_cliente(a: Agendamento):
    if a.servico not in SERVICOS:
        raise HTTPException(400, "Serviço inválido")

    inicio = a.horario[:5]
    duracao = SERVICOS[a.servico]["duracao"]
    fim = calcular_hora_fim(inicio, duracao)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT hora_inicio, hora_fim FROM agendamentos WHERE data = ?
    """, (str(a.data),))
    existentes = cursor.fetchall()

    for oi, of in existentes:
        if intervalo_conflita(inicio, fim, oi, of):
            raise HTTPException(400, "Horário indisponível")

    cursor.execute("""
        INSERT INTO agendamentos (nome, data, hora_inicio, hora_fim, servico)
        VALUES (?,?,?,?,?)
    """, (a.nome, str(a.data), inicio, fim, a.servico))
    conn.commit()
    conn.close()

    msg = f"""
Olá 😊
Agendamento confirmado:

📅 {a.data}
⏰ {inicio}
💅 {a.servico}
"""

    return {
        "whatsapp_url":
        "https://wa.me/5551991156840?text="+quote(msg)
    }

# =====================
# ADMIN
# =====================

@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nome, data, hora_inicio, hora_fim, servico
        FROM agendamentos
        ORDER BY data, hora_inicio
    """)
    rows = cursor.fetchall()
    conn.close()

    dados = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    for id_, nome, data, hi, hf, servico in rows:
        d = datetime.strptime(data,"%Y-%m-%d")
        mes = d.strftime("%Y-%m")
        semana = f"Semana {d.isocalendar().week}"

        if data not in dados[mes][semana]:
            dados[mes][semana][data] = {"total":0,"agendamentos":[]}

        preco = SERVICOS[servico]["preco"]
        dados[mes][semana][data]["total"] += preco
        dados[mes][semana][data]["agendamentos"].append({
            "id": id_,
            "nome": nome,
            "hora": f"{hi}–{hf}",
            "servico": servico
        })

    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "dados": dados, "servicos": SERVICOS.keys()}
    )

@app.post("/admin/agendamentos")
def admin_add(a: Agendamento):
    return criar_cliente(a)

@app.post("/admin/cancelar/{id}")
def cancelar(id:int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agendamentos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"ok":True}
