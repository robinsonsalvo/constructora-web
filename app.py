from flask import Flask, render_template, request, jsonify
from google import genai
from flask_mail import Mail, Message
import os 
import threading # Necesario para la operación asíncrona de correo

# Inicializa la aplicación Flask
app = Flask(__name__)

# --- CONFIGURACIÓN DE GEMINI ---
api_key = os.getenv("GEMINI_API_KEY")
client = None 

if api_key:
    try:
        # Usamos os.environ.get('GEMINI_API_KEY') en caso de que os.getenv falle en Render
        client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
    except Exception as e:
        print(f"Error al inicializar el cliente Gemini: {e}")

# --- CONFIGURACIÓN DE CORREO (Flask-Mail) ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com' 
app.config['MAIL_PORT'] = 587             
app.config['MAIL_USE_TLS'] = True         
app.config['MAIL_USE_SSL'] = False         # Evita conflictos de doble seguridad
app.config['MAIL_TIMEOUT'] = 120           # Aumenta el tiempo de espera a 120s (crítico para Render)
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD') 
mail = Mail(app) # Inicializa la extensión de correo

# --- FUNCIONES DE ENVÍO ASÍNCRONO ---
# Función que es ejecutada por el hilo. Recibe la app para crear el contexto.
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
            print("Email de cotización enviado con éxito en hilo de fondo.")
        except Exception as e:
            # Render mostrará esto si la autenticación falla por timeout o credenciales
            print(f"ERROR CRÍTICO AL ENVIAR EMAIL ASÍNCRONO: {e}")

# --- INICIO: LISTA DE PROYECTOS ---
proyectos_data = [
    {"id": 1, "titulo": "Remodelación de Baño Principal", "tipo": "Porcelanato", "descripcion": "Instalación de porcelanato tipo mármol de gran formato en piso y muros.", "imagen": "porcelanato_bano.jpg"},
    {"id": 2, "titulo": "Ampliación y Cocina Integral", "tipo": "Remodelación Integral", "descripcion": "Proyecto completo de ampliación de terraza y construcción de cocina americana.", "imagen": "remodelacion_cocina.jpg"},
    {"id": 3, "titulo": "Piso de Sala y Comedor", "tipo": "Cerámica", "descripcion": "Sustitución de piso flotante por cerámica rústica de alto tráfico y antideslizante.", "imagen": "ceramica_sala.jpg"}
]
# --- FIN: LISTA DE PROYECTOS ---


# -------------------------------------
# DEFINICIÓN DE TODAS LAS RUTAS 
# -------------------------------------

# 1. Ruta de Inicio
@app.route('/')
def index():
    return render_template('index.html')

# 2. Ruta de Galería
@app.route('/galeria')
def galeria():
    return render_template('galeria.html', proyectos=proyectos_data)

# 3. Ruta de Interfaz del Asesor
@app.route('/asesor')
def asesor_page():
    return render_template('asesor_ia.html')

# 4. Ruta de la API del Asesor
@app.route('/api/asesor', methods=['POST'])
def asesor_ia():
    if not client:
        return jsonify({"respuesta": "Error: El Asesor de IA no pudo inicializarse. Revisa tu clave API."}), 500

    data = request.get_json()
    pregunta_cliente = data.get('pregunta', 'Hola')

    system_instruction = (
        "Eres un asesor experto en materiales de la constructora Robinson Salvo, "
        "especializada en porcelanato y cerámica de alta gama. Responde preguntas "
        "de forma profesional y concisa."
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=pregunta_cliente,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        return jsonify({"respuesta": response.text})
    except Exception as e:
        return jsonify({"respuesta": f"Lo siento, hubo un error en el servicio de IA: {e}"}), 500

# 5. Ruta del Formulario de Contacto (AHORA CON HILO CORREGIDO)
@app.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        # 1. Recoger datos del formulario
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        tipo_proyecto = request.form.get('tipo_proyecto')
        mensaje = request.form.get('mensaje')

        # 2. Crear el Contenido del Email
        cuerpo_email = f"""
        ¡NUEVA SOLICITUD DE COTIZACIÓN WEB!

        Nombre: {nombre}
        Email de Contacto: {email}
        Tipo de Proyecto: {tipo_proyecto}

        Mensaje:
        {mensaje}
        """

        # 3. Crear el mensaje de correo
        msg = Message(
            subject=f'NUEVA COTIZACIÓN WEB: {tipo_proyecto}',
            sender=app.config['MAIL_USERNAME'],
            recipients=['robinsonceramista@gmail.com'], 
            body=cuerpo_email
        )

        # 4. INICIAR EL ENVÍO EN UN HILO DE FONDO (PASAMOS EL OBJETO app)
        thread = threading.Thread(target=send_async_email, args=[app, msg]) # <--- CORRECCIÓN CRÍTICA
        thread.start()

        # 5. Mostrar página de agradecimiento INMEDIATAMENTE
        return render_template('gracias.html', nombre=nombre)

    # Si es un método GET, simplemente muestra el formulario
    return render_template('contacto.html')

# -------------------------------------
# EJECUCIÓN DEL SERVIDOR 
# -------------------------------------
if __name__ == '__main__':
    app.run(debug=True)