from flask import Flask, render_template, Blueprint,jsonify,request
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
                # Process successful login
                return render_template('pg1.html')
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


@routes.route('/pg1')
def pg1():
    return render_template('pg1.html')

@routes.route('/pg2')
def pg2():
    return render_template('pg2.html')

@routes.route('/pg3')
def pg3():
    return render_template('pg3.html')
