# Manejo de calendario
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st
from datetime import datetime
class GoogleCalendar:
    def __init__(self, credentials, idcalendario):
        self.credentials = credentials
        self.idcalendar = idcalendario
        self.service = build('calendar', 'v3', credentials=service_account.Credentials.from_service_account_info(self.credentials, scopes=['https://www.googleapis.com/auth/calendar']))
        
    def create_event(self, name_event, start_time, end_time, timezone, attendes=None):
        event = {
            'summary': name_event,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
        }

        if attendes:
            event['attendees'] = [{"email": email} for email in attendes]

        try:
            created_event = self.service.events().insert(calendarId=self.idcalendar, body=event).execute()
            return created_event
        except HttpError as err:
            raise Exception(f"An error has occurred: {err}")
    
    def get_events(self, date = None):

        if not date:
            events = self.service.events().list(calendarId = self.idcalendar).execute
        else:
            start_date = f"{date}T00:00:00Z"
            end_date = f"{date}T23:59:00Z"
            events = self.service.events().list(calendarId=self.idcalendar, timeMin=start_date, timeMax=end_date).execute()
        return events.get('items', [])

 
        
    def get_events_start_time(self, date):
        events = self.get_events(date)
        start_times = []

        for event in events:
            start_time = event['start'].get('dateTime')
            if start_time:
                parsed_start = datetime.fromisoformat(start_time[:-6])
                hours_minutes = parsed_start.strftime("%H:%M")
                start_times.append(hours_minutes)

        return start_times

# Credenciales y configuración
# credentials = st.secrets["sheets"]["credentials_sheet"]
# idcalendar = "jablemlopra@gmail.com"

# # Instancia de GoogleCalendar
# google = GoogleCalendar(credentials, idcalendar)

# # # Datos del evento
# start_date = '2024-07-13T12:00:00-04:00'  # Asegúrate de que la zona horaria sea correcta
# end_date = '2024-07-13T13:00:00-04:00'
# time_zone = 'America/Santiago'
# attendes = []

# # # Crear el evento
# try:
#     # date = '2024-07-13'
#     # init_hours = google.get_events_start_time(date)
#     # print(init_hours)
#     event = google.create_event("Barberia New Rulay", start_date, end_date, time_zone, attendes)
#     # st.write("Evento creado exitosamente:", event['htmlLink'])
#     print(event)
# except Exception as e:
#     print(f"No se pudo crear el evento: {e}")
#     # st.error(f"No se pudo crear el evento: {e}")
