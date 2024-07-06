from flask import Flask, request, render_template, redirect, url_for, session
import logging
from logging.handlers import RotatingFileHandler
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Cambia esto a una clave secreta

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear un manejador de archivos rotativo
handler = RotatingFileHandler('app.log', maxBytes=2000, backupCount=10)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# Añadir el manejador al logger
logger.addHandler(handler)

# Ruta de inicio
@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('login'))

# Ruta de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        session['username'] = username
        logger.info(f'{username} logged in')
        return redirect(url_for('home'))
    return render_template('login.html')

# Ruta de logout
@app.route('/logout')
def logout():
    username = session.pop('username', None)
    if username:
        logger.info(f'{username} logged out')
    return redirect(url_for('login'))

# Ruta de contact us
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        send_email(email, subject, message)
        return 'Email sent!'
    return render_template('contact.html')

# Función para enviar correos
def send_email(email, subject, message):
    sender_email = "youremail@example.com"
    receiver_email = "receiver@example.com"
    password = "yourpassword"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    try:
        server = smtplib.SMTP('smtp.example.com', 587)
        server.starttls()
        server.login(sender_email, password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
    except Exception as e:
        logger.error(f'Failed to send email: {e}')

# Rutas protegidas por login
@app.route('/visor')
@app.route('/events')
@app.route('/gir')
@app.route('/ssis')
def protected():
    if 'username' not in session:
        return redirect(url_for('login'))
    endpoint = request.endpoint
    return render_template(f'{endpoint}.html', username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)
