from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()

# Подключаем папку для хранения статических файлов (например, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем шаблонизатор Jinja2
templates = Jinja2Templates(directory="templates")

# Создаем соединение с базой данных SQLite
conn = sqlite3.connect('hospital.db')
cursor = conn.cursor()

# Команда SQL для создания таблицы Doctors
create_doctors_table = """
CREATE TABLE IF NOT EXISTS Doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    email TEXT,
    phone TEXT
);
"""

# Команда SQL для создания таблицы Patients
create_patients_table = """
CREATE TABLE IF NOT EXISTS Patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    birth_date DATE,
    gender TEXT,
    email TEXT,
    phone TEXT
);
"""

# Команда SQL для создания таблицы Appointments
create_appointments_table = """
CREATE TABLE IF NOT EXISTS Appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    appointment_date DATETIME NOT NULL,
    reason TEXT,
    FOREIGN KEY (doctor_id) REFERENCES Doctors(id),
    FOREIGN KEY (patient_id) REFERENCES Patients(id)
);
"""

# Создаем таблицы в базе данных
cursor.execute(create_doctors_table)
cursor.execute(create_patients_table)
cursor.execute(create_appointments_table)
conn.commit()

# Определение маршрута для отображения главной страницы
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Определение маршрута для отображения страницы добавления врача
@app.get("/add-doctor", response_class=HTMLResponse)
async def add_doctor(request: Request):
    return templates.TemplateResponse("add_doctor.html", {"request": request})

# Определение маршрута для обработки POST-запросов на добавление врача
@app.post("/add-doctor", response_class=HTMLResponse)
async def add_doctor_post(request: Request, name: str = Form(...), specialization: str = Form(...), email: str = Form(None), phone: str = Form(None)):
    try:
        cursor.execute("INSERT INTO Doctors (name, specialization, email, phone) VALUES (?, ?, ?, ?)", (name, specialization, email, phone))
        conn.commit()
        # После успешного добавления врача выполняем перенаправление на главную страницу
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return {"error": f"Error adding doctor: {e}"}

# Определение маршрута для отображения страницы добавления пациента
@app.get("/add-patient", response_class=HTMLResponse)
async def add_patient(request: Request):
    return templates.TemplateResponse("add_patient.html", {"request": request})

# Определение маршрута для обработки POST-запросов на добавление пациента
@app.post("/add-patient", response_class=HTMLResponse)
async def add_patient_post(request: Request, name: str = Form(...), birth_date: str = Form(...), gender: str = Form(...), email: str = Form(None), phone: str = Form(None)):
    try:
        cursor.execute("INSERT INTO Patients (name, birth_date, gender, email, phone) VALUES (?, ?, ?, ?, ?)", (name, birth_date, gender, email, phone))
        conn.commit()
        # После успешного добавления пациента выполняем перенаправление на главную страницу
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return {"error": f"Error adding patient: {e}"}


# Определение маршрута для обработки добавления записи на прием
# Определение маршрута для отображения страницы добавления записи на прием
@app.get("/add-appointment", response_class=HTMLResponse)
async def show_add_appointment_form(request: Request):
    return templates.TemplateResponse("add_appointment.html", {"request": request})

# Определение маршрута для обработки POST-запросов на добавление записи на прием
@app.post("/add-appointment", response_class=HTMLResponse)
async def add_appointment_post(request: Request, doctor_id: int = Form(...), patient_id: int = Form(...), appointment_date: str = Form(...), reason: str = Form(None)):
    try:
        cursor.execute("INSERT INTO Appointments (doctor_id, patient_id, appointment_date, reason) VALUES (?, ?, ?, ?)", (doctor_id, patient_id, appointment_date, reason))
        conn.commit()
        # После успешного добавления записи на прием выполняем перенаправление на главную страницу
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        return {"error": f"Error adding appointment: {e}"}


# Определение маршрута для выполнения SQL-запросов
@app.post("/query/", response_class=HTMLResponse)
async def execute_query(request: Request, query: str = Form(...)):
    try:
        cursor.execute(query)
        conn.commit()
        result = cursor.fetchall()
        column_names = []
        if cursor.description is not None:
            column_names = [description[0] for description in cursor.description]
        return templates.TemplateResponse("result.html", {"query": query, "result": result, "column_names": column_names, "request": request})
    except Exception as e:
        error_message = f"Error executing query: {e}"
        return templates.TemplateResponse("error.html", {"error_message": error_message})

# Определение маршрута для отображения страницы с ошибкой
@app.get("/error/", response_class=HTMLResponse)
async def error():
    return templates.TemplateResponse("error.html", {"error_message": "An error occurred."})
