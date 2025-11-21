from flask import Flask, render_template

# Inicializa la aplicación Flask
app = Flask(__name__)

# Define la ruta principal (la página de inicio)
@app.route('/')
def index():
    # Pide a Flask que cargue el archivo index.html
    return render_template('index.html')

# Ejecutar la aplicación (solo si se ejecuta directamente)
if __name__ == '__main__':
    # Usaremos el modo debug para que los cambios se refresquen automáticamente
    app.run(debug=True)