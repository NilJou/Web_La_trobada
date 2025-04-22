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
            username = request.form.get('username')
            password = request.form.get('password')
            
            url = "http://10.100.0.78:5000/api/login"
            headers = {'Content-Type': 'application/json'}
            payload = {"usuari": username, "contrasenya": password}
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                session['user'] = username
                return render_template('foro.html')
            else:
                return jsonify({
                    'status': 'error',
                    'message': response.json().get('error', 'Error en el login')
                }), response.status_code
            
        return render_template('login.html')
    except Exception as e:
        return jsonify({'status': 'error', 'message': f"S'ha produït un error: {str(e)}"}), 500

@routes.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if password != confirm_password:
                return render_template('register.html', error="Les contrasenyes no coincideixen")
            
            if not all([username, email, password]):
                return render_template('register.html', error="Es requereix omplir tots els camps")
            
            url = "http://10.100.0.78:5000/api/register"
            headers = {'Content-Type': 'application/json'}
            payload = {"nom_usuari": username, "correu": email, "contrasenya": password}
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 201:
                return render_template('login.html', success="Usuari registrat correctament")
            elif response.status_code == 409:
                conflict_type = response.json().get('conflict_type')
                if conflict_type == 'username':
                    return render_template('register.html', error="L'usuari ja existeix")
                elif conflict_type == 'email':
                    return render_template('register.html', error="El correu ja existeix")
            else:
                error_msg = response.json().get('error', "S'ha produït un error durant el registre")
                return render_template('register.html', error=error_msg)
        
        return render_template('register.html')
    except Exception as e:
        return render_template('register.html', error=f"S'ha produït un error: {str(e)}")

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
                return render_template('escaner.html', error="Si us plau, introduïu un nom de carta")
            
            api_url = "http://10.100.0.78:5000/api/carta/web"
            headers = {'Content-Type': 'application/json'}
            payload = {"nom": nom}
            
            response = requests.post(api_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                cartes = response.json()
                if not cartes:
                    return render_template('escaner.html', nom_buscat=nom, error="No s'han trobat cartes")
                
                return render_template('escaner.html', nom_buscat=nom, cartes=cartes)
            else:
                error_msg = response.json().get('error', 'Error en la cerca de cartes')
                return render_template('escaner.html', error=error_msg)
        
        return render_template('escaner.html')
    except requests.exceptions.RequestException as e:
        return render_template('escaner.html', error="Error de connexió amb el servidor")
    except Exception as e:
        return render_template('escaner.html', error=f"Error inesperat: {str(e)}")

@routes.route('/crear_colleccio', methods=['POST'])
def crear_colleccio():
    try:
        nom_colleccio = request.form.get('nom_colleccio')
        nom_buscat = request.form.get('nom_buscat')
        usuari_actual = session['user']
        
        if not usuari_actual:
            return render_template('escaner.html', error="No s'ha iniciat sessió")
        
        url = "http://10.100.0.78:5000/api/coleccio"
        headers = {'Content-Type': 'application/json'}
        payload = {"usr": usuari_actual, "nom_col": nom_colleccio}
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            return render_template('escaner.html', nom_buscat=nom_buscat, success="Col·lecció creada")
        else:
            error_msg = response.json().get('error', "Error en crear la col·lecció")
            return render_template('escaner.html', nom_buscat=nom_buscat, error=error_msg)
    except Exception as e:
        return render_template('escaner.html', error=f"S'ha produït un error: {str(e)}")

@routes.route('/colleccio')
def colleccio():
    try:
        usuari_actual = session["user"]
        if not usuari_actual:
            return render_template('colleccio.html', error="No s'ha iniciat sessió")
        
        url = "http://10.100.0.78:5000/api/coleccio/mostrar"
        headers = {'Content-Type': 'application/json'}
        payload = {"usr": usuari_actual}
        
        response = requests.get(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            colleccions = response.json()
            
            if not isinstance(colleccions, list):
                colleccions = [colleccions] if isinstance(colleccions, dict) else []
            
            processed_collections = []
            for col in colleccions:
                processed = {
                    'id': col.get('id', 0),
                    'nom': col.get('nombre', "Sense nom"),
                    'quantitat': col.get('quantitat', 0)
                }
                processed_collections.append(processed)
            
            return render_template('colleccio.html', colleccions=processed_collections)
        else:
            error_msg = response.json().get('error', "Error en obtenir les col·leccions")
            return render_template('colleccio.html', error=error_msg)
    except Exception as e:
        return render_template('colleccio.html', error=f"S'ha produït un error: {str(e)}")

@routes.route('/eliminar_colleccio/<int:colleccio_id>', methods=['POST'])
def eliminar_colleccio(colleccio_id):
    try:
        usuari_actual = session.get("user")
        if not usuari_actual:
            return jsonify({'status': 'error', 'message': "No s'ha iniciat sessió"}), 401
        
        url = "http://10.100.0.78:5000/api/coleccio/eliminar"
        headers = {'Content-Type': 'application/json'}
        payload = {
                    "usr": usuari_actual, 
                    "nom_col": colleccio_id
                    }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'Col·lecció eliminada'})
        else:
            error_msg = response.json().get('error', "Error en eliminar la col·lecció")
            return jsonify({'status': 'error', 'message': error_msg}), response.status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': f"S'ha produït un error: {str(e)}"}), 500

@routes.route('/xat')
def xat():
    return render_template('xat.html')

@routes.route('/usuari')
def usuari():
    return render_template('usuari.html')
