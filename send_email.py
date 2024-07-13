import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st 

def send(email, nombre, fecha, hora, servicio):

    #credentials
    user = st.secrets["emails"]["smtp_user"]
    password = st.secrets["emails"]["smtp_pass"]

    sender_email = "New Rulay Barbershop"
    # config server
    msg = MIMEMultipart()

    smtp_server = "smtp.gmail.com"
    smtp_port = 587 

    #Parametros del mensaje
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Reserva de Barbería"

    #cuerpo del mensaje
    message = f"""
    Hola {nombre}
    Su reserva ha sido realizada con éxito.
    Fecha: {fecha}
    Hora: {hora }
    Servicio: {servicio }

    Gracias por confiar en nosotros
    Saludos.
    """

    msg.attach(MIMEText(message, 'plain'))

    #Conexión al servidor
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(user, password)
        server.sendmail(sender_email, email,msg.as_string())
        server.quit()
    except smtplib.SMTPException as e:
        st.exception(f"Error al enviar email: {e}")

