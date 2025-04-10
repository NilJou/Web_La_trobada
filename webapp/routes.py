from flask import Flask, render_template, Blueprint, jsonify, request, session
import requests

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return render_template('login.html')


@routes.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            # Get data from form submission
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Prepare the API request
            url = "http://10.100.0.78:5000/api/login"
            headers = {'Content-Type': 'application/json'}
            payload = {
                "usuari": username,
                "contrasenya": password
            }
            
            # Make the POST request to your API
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("Login successful:", data)
                session['user'] = data.get('user')
                # Process successful login
                return render_template('foro.html')
            else:
                return jsonify({
                    'status': 'error',
                    'message': response.json().get('error', 'Login failed')
                }), response.status_code
            
        # For GET requests, just show the login form
        return render_template('login.html')
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': 'error occurred: {}'.format(str(e))
        }), 500
    
@routes.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            # Get data from form submission
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # Basic validation
            if password != confirm_password:
                return render_template('register.html', error="Las conrasenyas no coincideixen")
            
            if not all([username, email, password]):
                return render_template('register.html', error="Es requerit omplir tots els camps")
            
            # Prepare the API request
            url = "http://10.100.0.78:5000/api/register"  # Asegúrate de que esta ruta exista en tu API
            headers = {'Content-Type': 'application/json'}
            payload = {
                "nom_usuari": username,
                "correu": email,
                "contrasenya": password
            }
            
            # Make the POST request to your API
            response = requests.post(url, json=payload, headers=headers)
            print(response)
            if response.status_code == 201:  # 201 es el código típico para creación exitosa
                # Redirige al login después de registro exitoso
                return render_template('login.html', success="Usuari registrat correctament. Ara pot iniciar sessió.")
            elif response.status_code == 409:
                conflict_type = response.json().get('conflict_type')
                if conflict_type == 'username':
                    return render_template('register.html', error="L'usuari ja existeix")
                elif conflict_type == 'email':
                    return render_template('register.html', error="El correu ja existeix")
            else:
                error_msg = response.json().get('error', 'Ha ocurrit un error durant el registre')
                return render_template('register.html', error=error_msg)
        # For GET requests, show the registration form
        return render_template('register.html')
        
    except Exception as e:
        return render_template('register.html', error=f"An error occurred: {str(e)}")


@routes.route('/foro')
def foro():
    return render_template('foro.html')

@routes.route('/escaner')
def escaner():
    return render_template('escaner.html')

@routes.route('/carta/web', methods=['GET', 'POST'])
def carta_web():
    try:
        if request.method == 'POST':
            nom = request.form.get('nom')
            
            if not nom:
                return render_template('escaner.html', error="Si us plau, introdueix un nom de carta")
            
            api_url = "http://10.100.0.78:5000/api/carta/web"
            headers = {'Content-Type': 'application/json'}
            payload = {"nom": nom}
            
            response = requests.post(api_url, json=payload, headers=headers)
            print(f"[DEBUG] Resposta de l'API (status {response.status_code}):")
            print(f"Headers: {response.headers}")
            print(f"Contingut: {response.text}")
            if response.status_code == 200:
                cartes = response.json()  # Obtenim la llista de cartes
                if not cartes:
                    return render_template('escaner.html',
                                         nom_buscat=nom,
                                         error="No s'han trobat cartes amb aquest nom")
                
                return render_template('escaner.html',
                                    nom_buscat=nom,
                                    cartes=cartes)
                
            
            else:
                error_msg = response.json().get('error', 'Error en la cerca de cartes')
                return render_template('escaner.html',
                                    error=error_msg)
        
        return render_template('escaner.html')
        
    except requests.exceptions.RequestException as e:
        return render_template('escaner.html',
                             error="Error de connexió amb el servidor de cartes")
    except Exception as e:
        return render_template('escaner.html',
                             error=f"Error inesperat: {str(e)}")

@routes.route('/colleccio')
def colleccio():
    return render_template('colleccio.html')

@routes.route('/xat')
def xat():
    return render_template('xat.html')

@routes.route('/usuari')
def usuari():
    return render_template('usuari.html')
