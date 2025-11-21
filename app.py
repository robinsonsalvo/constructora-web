from flask import Flask, render_template, request, jsonify
from google import genai
import os 

# Inicializa la aplicación Flask
app = Flask(__name__)

# --- CONFIGURACIÓN DE GEMINI ---
api_key = os.getenv("GEMINI_API_KEY")
client = None # Inicializamos a None por si la clave falla

if api_key:
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Error al inicializar el cliente Gemini: {e}")
        
# --- INICIO: LISTA DE PROYECTOS ---
proyectos_data = [
    {"id": 1, "titulo": "Remodelación de Baño Principal", "tipo": "Porcelanato", "descripcion": "Instalación de porcelanato tipo mármol de gran formato en piso y muros.", "imagen": "porcelanato_bano.jpg"},
    {"id": 2, "titulo": "Ampliación y Cocina Integral", "tipo": "Remodelación Integral", "descripcion": "Proyecto completo de ampliación de terraza y construcción de cocina americana.", "imagen": "remodelacion_cocina.jpg"},
    {"id": 3, "titulo": "Piso de Sala y Comedor", "tipo": "Cerámica", "descripcion": "Sustitución de piso flotante por cerámica rústica de alto tráfico.", "imagen": "ceramica_sala.jpg"}
]
# --- FIN: LISTA DE PROYECTOS ---


# -------------------------------------
# DEFINICIÓN DE TODAS LAS RUTAS (DEBEN IR AQUÍ)
# -------------------------------------

# 1. Ruta de Inicio
@app.route('/')
def index():
    return render_template('index.html')

# 2. Ruta de Galería
@app.route('/galeria')
def galeria():
    return render_template('galeria.html', proyectos=proyectos_data)

# 3. Ruta de Interfaz del Asesor (La que da 404)
@app.route('/asesor')
def asesor_page():
    return render_template('asesor_ia.html')

# 4. Ruta de la API del Asesor (Donde ocurre la IA)
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


# -------------------------------------
# EJECUCIÓN DEL SERVIDOR (DEBE IR AL FINAL)
# -------------------------------------
if __name__ == '__main__':
    app.run(debug=True)