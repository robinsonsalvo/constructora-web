from flask import Flask, render_template

# Inicializa la aplicación Flask
app = Flask(__name__)

# --- INICIO: LISTA DE PROYECTOS PARA LA GALERÍA ---
proyectos_data = [
    {
        "id": 1,
        "titulo": "Remodelación de Baño Principal",
        "tipo": "Porcelanato",
        "descripcion": "Instalación de porcelanato tipo mármol de gran formato en piso y muros.",
        "imagen": "porcelanato_bano.jpg"
    },
    {
        "id": 2,
        "titulo": "Ampliación y Cocina Integral",
        "tipo": "Remodelación Integral",
        "descripcion": "Proyecto completo de ampliación de terraza y construcción de cocina americana.",
        "imagen": "remodelacion_cocina.jpg"
    },
    {
        "id": 3,
        "titulo": "Piso de Sala y Comedor",
        "tipo": "Cerámica",
        "descripcion": "Sustitución de piso flotante por cerámica rústica de alto tráfico.",
        "imagen": "ceramica_sala.jpg"
    }
]
# --- FIN: LISTA DE PROYECTOS ---


# Define la ruta principal (la página de inicio)
@app.route('/')
def index():
    return render_template('index.html')

# ESTA ES LA RUTA CRÍTICA QUE DEBE ESTAR BIEN ESCRITA
@app.route('/galeria')
def galeria():
    # Enviamos la lista de proyectos a la plantilla HTML
    return render_template('galeria.html', proyectos=proyectos_data)

# Ejecutar la aplicación (solo si se ejecuta directamente)
if __name__ == '__main__':
    app.run(debug=True)
