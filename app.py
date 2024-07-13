import streamlit as st 
from streamlit_option_menu import option_menu
from send_email import send 
from google_sheets import GoogleSheets 
import re
import uuid
from google_calendar import GoogleCalendar
import numpy as np
import datetime as dt
import pytz
import time

page_title = "New Rulay"
page_icon = "💈"
layout = "centered"

horas = ["09:00", "10:00", "11:00", "12:00", "13:00"]
servicio_lista = ["Corte - $ 10.000", "Corte y cejas - $12.000", "Cejas - $1.000"]

#google sheet
document = "gestion-barberia-rulay"
sheet = "reservas"
credentials = st.secrets["sheets"]["credentials_sheet"]
idcalendar = "jablemlopra@gmail.com"

time_zone = 'America/Santiago'
santiago_tz = pytz.timezone(time_zone)

# Funciones
def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    else:
        return False

def generate_uid():
    return str(uuid.uuid4())

def add_hour_and_half(time):
    parsed_time = dt.datetime.strptime(time, "%H:%M").time()
    new_time = (dt.datetime.combine(dt.date.today(), parsed_time) + dt.timedelta(hours=1, minutes=30)).time()
    return new_time.strftime("%H:%M")

def sort_hours(hours):
    return sorted(hours, key=lambda x: dt.datetime.strptime(x, "%H:%M"))

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.image("assets/barber.png")

st.title("New Rulay")
st.text("Valle del Sol #1106, La Florida")

selected = option_menu(menu_title=None, options=["Reservar","Precios","Detalles"], 
                       icons=["calendar-date","building", "clipboard-minus"], 
                       orientation="horizontal")

if selected == "Detalles":
    st.subheader("Ubicación")
    st.markdown("""
        <iframe src="https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d415.6067527995837!2d-70.5596603!3d-33.5571689!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x9662d1b69fc3c12b%3A0x322ab4a3be991442!2sNew%20Rulay%20Barbershop!5e0!3m2!1ses!2scl!4v1720761203803!5m2!1ses!2scl" width="100%" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
    """, unsafe_allow_html=True)

    st.subheader("Horarios")
    st.write("""
        | Día       | Horario       |
        |-----------|---------------|
        | Lunes     | 10:00 a 21:00 |
        | Martes    | 10:00 a 21:00 |
        | Miércoles | 10:00 a 21:00 |
        | Jueves    | 10:00 a 21:00 |
        | Viernes   | 10:00 a 21:00 |
        | Sábados   | 11:00 a 19:00 |
    """)

    st.subheader("Contacto")
    st.text("📞 +569 8856 7741")

    st.subheader("Instagram")
    st.markdown("Síguenos [aquí](https://www.instagram.com/barbershop.rulay/) en Instagram")

if selected == "Precios":
    st.subheader("Precios")
    st.write("""
        | Servicio             | Precio  |
        |----------------------|---------|
        | Degradado            | $10.000 |
        | Cejas                | $2.000  |
        | Full                 | $13.000 |
    """)

if selected == "Reservar":
    st.subheader("Reservar")
    c1, c2 = st.columns(2)

    # Inicializar estado de sesión si no existe
    if "result_hours" not in st.session_state:
        st.session_state.result_hours = horas

    nombre = c1.text_input("Tu nombre", placeholder="nombre")
    fecha = c1.date_input("Fecha")

    if fecha:
        calendar = GoogleCalendar(credentials, idcalendar)
        hours_block = calendar.get_events_start_time(str(fecha))
        result_hours = list(np.setdiff1d(horas, hours_block))
        result_hours = sort_hours(result_hours)  # Ordenar las horas disponibles
        st.session_state.result_hours = result_hours

    servicio = c1.selectbox("Servicio", servicio_lista)

    email = c2.text_input("Tu email")
    hora = c2.selectbox("Horas disponibles", st.session_state.result_hours)
    notas = c2.text_area("Notas")

    enviar = st.button("Reservar")

    if enviar:
        with st.spinner("Cargando..."):
            if nombre == "":
                st.warning("El campo nombre es obligatorio")
            elif email == "":
                st.warning("El campo email es obligatorio")
            elif not validate_email(email):
                st.warning("El email no es válido")
            else:
                # Crear evento en Google Calendar
                parsed_time = dt.datetime.strptime(hora, "%H:%M").time()
                start_time = santiago_tz.localize(dt.datetime.combine(fecha, parsed_time))

                end_hours = add_hour_and_half(hora)
                parsed_time2 = dt.datetime.strptime(end_hours, "%H:%M").time()
                end_time = santiago_tz.localize(dt.datetime.combine(fecha, parsed_time2))

                start_time_utc = start_time.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
                end_time_utc = end_time.astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

                calendar.create_event("Barberia New Rulay", start_time_utc, end_time_utc, time_zone)

                # Crear registro en Google Sheets
                uid = generate_uid()
                fecha_str = fecha.strftime('%d-%m-%Y')
                data = [[nombre, email, fecha_str, hora, notas, servicio, uid]]
                gs = GoogleSheets(credentials, document, sheet)
                range = gs.get_last_row_range()
                gs.write_data(range, data)

                # Enviar email al cliente
                send(email, nombre, fecha_str, hora, servicio)

                st.success("Su corte de pelo ha sido reservado de forma exitosa")

                
