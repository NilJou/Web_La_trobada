# Importar la funció create_app del mòdul webapp
from webapp import create_app

# Crear una instància de l'aplicació Flask cridant a la funció create_app
app = create_app()

# Comprovació si s'executa aquest fitxer directament
if __name__ == '__main__':
    # Executar l'aplicació en mode debug
    app.run(debug=True)