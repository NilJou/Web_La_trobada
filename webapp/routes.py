# Imports necessaris
from flask import Flask, render_template, Blueprint, jsonify, request, session, redirect, url_for
import requests

# Definició de l'adreça IP de l'API
IP_API = "10.100.3.25:5000"

# Creació d'un Blueprint
routes = Blueprint('routes', __name__)

# Ruta principal
@routes.route('/')
def home():
    return render_template('login.html')

# Ruta per el login
@routes.route('/login', methods=['GET', 'POST'])
def login():
    try:
        # Si la sol·licitud és POST (enviament de formulari)
        if request.method == 'POST':
            # Obtenir usuari i contrasenya del formulari
            username = request.form.get('username')
            password = request.form.get('password')

            # Paràmetres per a l'API
            url = f"http://{IP_API}/api/login"
            headers = {'Content-Type': 'application/json'}
            payload = {"usuari": username, "contrasenya": password}

            # Fer la petició a l'API
            response = requests.post(url, json=payload, headers=headers)

            # Si el login és exitós retona 200 i guardar l'usuari a la sessió
            if response.status_code == 200:
                # Guardar usuari a la sessió i redirigir al fòrum
                session['user'] = username
                return render_template('foro.html')
            else:
                # Si hi ha error, mostrar missatge d'error
                return jsonify({
                    'status': 'error',
                    'message': response.json().get('error', 'Error en el login')
                }), response.status_code

        # Si és GET, mostrar la pàgina de login
        return render_template('login.html')
    except Exception as e:
        # Gestió d'errors inesperats
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
            
            url = f"http://{IP_API}/api/register"
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

# Ruta per mostrar el fòrum
@routes.route('/foro')
def foro():
    return render_template('foro.html')

# Ruta per mostrar l'escàner
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
            
            api_url = f"http://{IP_API}/api/carta/web"
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

@routes.route('/afegir_carta_colleccio', methods=['POST'])
def afegir_carta_colleccio():
    try:
        usuari_actual = session.get("user")
        if not usuari_actual:
            return jsonify({'status': 'error', 'message': "No s'ha iniciat sessió"}), 401
        
        data = request.get_json()
        carta_id = data.get('carta_id')
        colleccio_id = data.get('colleccio_id')
        
        if not carta_id or not colleccio_id:
            return jsonify({'status': 'error', 'message': "Falten dades necessàries"}), 400
        
        url = f"http://{IP_API}/api/carta/coleccio"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "usr": usuari_actual,
            "id_col": colleccio_id,
            "id_carta": carta_id
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'Carta afegida correctament'})
        else:
            error_msg = response.json().get('error', "Error en afegir la carta a la col·lecció")
            return jsonify({'status': 'error', 'message': error_msg}), response.status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': f"S'ha produït un error: {str(e)}"}), 500

@routes.route('/obtenir_colleccions')
def obtenir_colleccions():
    try:
        usuari_actual = session.get("user")
        if not usuari_actual:
            return jsonify({'status': 'error', 'message': "No s'ha iniciat sessió"}), 401
        
        url = f"http://{IP_API}/api/coleccio/mostrar"
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
            
            return jsonify(processed_collections)
        else:
            error_msg = response.json().get('error', "Error en obtenir les col·leccions")
            return jsonify({'status': 'error', 'message': error_msg}), response.status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': f"S'ha produït un error: {str(e)}"}), 500

# Ruta per mostrar les col·leccions
@routes.route('/colleccio')
def colleccio():
    try:
        # Obtenir la sessió de l'usuari
        usuari_actual = session["user"]
        if not usuari_actual:
            return render_template('colleccio.html', error="No s'ha iniciat sessió")

        # Paràmetres per a l'API
        url = f"http://{IP_API}/api/coleccio/mostrar"
        headers = {'Content-Type': 'application/json'}
        payload = {"usr": usuari_actual}

        response = requests.get(url, headers=headers, json=payload)

        # Si la resposta és exitosa (codi 200)
        if response.status_code == 200:
            colleccions = response.json()
            # Assegurar-se que colleccions sigui una llista
            if not isinstance(colleccions, list):
                colleccions = [colleccions] if isinstance(colleccions, dict) else []

            # Processar les col·leccions per a la vista
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
            # Gestió d'error
            error_msg = response.json().get('error', "Error en obtenir les col·leccions")
            return render_template('colleccio.html', error=error_msg)
    except Exception as e:
        # Gestió d'errors inesperats
        return render_template('colleccio.html', error=f"S'ha produït un error: {str(e)}")

# Ruta per crear una nova col·lecció
@routes.route('/crear_colleccio', methods=['POST'])
def crear_colleccio():
    try:
        # Obtenir dades pel formulari
        nom_colleccio = request.form.get('nom_colleccio')
        usuari_actual = session['user']

        if not usuari_actual:
            return render_template('escaner.html', error="No s'ha iniciat sessió")

        # Enviar sol·licitud a l'API per crear la col·lecció
        url = f"http://{IP_API}/api/coleccio"
        headers = {'Content-Type': 'application/json'}
        payload = {
                    "usr": usuari_actual, 
                    "nom_col": nom_colleccio
        }

        response = requests.post(url, json=payload, headers=headers)

        # Si la creació va ser exitosa (codi 201)
        if response.status_code == 201:
            return redirect(url_for('routes.colleccio'))
        else:
            # Gestionar error en crear la col·lecció
            error_msg = response.json().get('error', "Error en crear la col·lecció")
            return render_template('escaner.html', error=error_msg)
    except Exception as e:
        # Gestió d'errors inesperats
        return render_template('escaner.html', error=f"S'ha produït un error: {str(e)}")

# Ruta per eliminar una col·lecció
@routes.route('/eliminar_colleccio/<int:colleccio_id>', methods=['POST'])
def eliminar_colleccio(colleccio_id):
    try:
        # Verificar usuari a la sessió
        usuari_actual = session.get("user")
        if not usuari_actual:
            return jsonify({'status': 'error', 'message': "No s'ha iniciat sessió"}), 401

        # Enviar sol·licitud a l'API per eliminar la col·lecció
        url = f"http://{IP_API}/api/coleccio/eliminar"
        headers = {'Content-Type': 'application/json'}
        payload = {"usr": usuari_actual, "id": colleccio_id}

        response = requests.post(url, json=payload, headers=headers)

        # Si l'eliminació va ser exitosa (codi 200)
        if response.status_code == 200:
            return jsonify({'status': 'success', 'message': 'Col·lecció eliminada'})
        else:
            # Gestionar error en eliminar la col·lecció
            error_msg = response.json().get('error', "Error en eliminar la col·lecció")
            return jsonify({'status': 'error', 'message': error_msg}), response.status_code
    except Exception as e:
        # Gestió d'errors inesperats
        return jsonify({'status': 'error', 'message': f"S'ha produït un error: {str(e)}"}), 500

# Ruta per veure els detalls d'una col·lecció específica
@routes.route('/colleccio/<int:colleccio_id>')
def veure_colleccio(colleccio_id):
    try:
        # Verificar si hi ha un usuari a la sessió
        usuari_actual = session.get("user")
        if not usuari_actual:
            return redirect(url_for('routes.login'))

        headers = {'Content-Type': 'application/json'}

        # Obtenir les cartes de la col·lecció des de l'API
        url_cartes = f"http://{IP_API}/api/carta/coleccio/mostrar"
        payload_cartes = {
            "usr": usuari_actual,
            "id_col": colleccio_id
        }

        response_cartes = requests.get(url_cartes, headers=headers, json=payload_cartes)

        # Si la resposta és exitosa
        if response_cartes.status_code == 200:
            cartes = response_cartes.json()
            # Assegurar-se que cartes sigui una llista
            if not isinstance(cartes, list):
                cartes = [cartes] if isinstance(cartes, dict) else []

            # Processar les cartes per a la vista
            processed_cartes = []
            for carta in cartes:
                processed = {
                    'id': carta.get('id'),
                    'nom': carta.get('nom', "Sense nom"),
                    'imatge_url': carta.get('imatge_url')
                }
                processed_cartes.append(processed)

            # Crear objecte de col·lecció processada per a la vista
            colleccio_procesada = {
                'id': colleccio_id,
                'nom': f"Col·lecció {colleccio_id}",
                'quantitat': len(processed_cartes)
            }

            return render_template('colleccio_detall.html', colleccio=colleccio_procesada, cartes=processed_cartes)
        else:
            # Gestionar error en obtenir les cartes
            error_msg = response_cartes.json().get('error', "Error en obtenir les cartes de la col·lecció")
            return render_template('colleccio_detall.html', error=error_msg, colleccio=None, cartes=[])
    except Exception as e:
        # Gestió d'errors inesperats
        return render_template('colleccio_detall.html', error=f"Error inesperat: {str(e)}", colleccio=None, cartes=[])

# Ruta per al xat
@routes.route('/xat')
def xat():
    return render_template('xat.html')

@routes.route('/api/xat/contactes')
def obtener_contactes():
    try:
        if 'user' not in session:
            return jsonify({'status': 'error', 'message': "No s'ha iniciat sessió"}), 401

        url = f"http://{IP_API}/api/chat/conversaciones/{session['user']}"
        response = requests.get(url)

        if response.status_code == 200:
            conversaciones = response.json()
            processed_conversations = []
            for conv in conversaciones:
                processed = {
                    'nom': conv['nombre_contacto']
                }
                processed_conversations.append(processed)
            
            return processed_conversations
        else:
            error_msg = response.json().get('error', "Error en obtenir les conversacions")
            return jsonify({'status': 'error', 'message': error_msg}), response.status_code
            
    except Exception as e:
        print(f"Error: {str(e)}")

@routes.route('/buscar_usuarios', methods=['GET'])
def buscar_usuarios():
    try:
        search_term = request.args.get('q', '').lower()
        if not search_term:
            return jsonify([])
        
        url = f"http://{IP_API}/api/usuarios/buscar?q={search_term}"
        response = requests.get(url)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'status': 'error', 'message': 'Error en la búsqueda'}), response.status_code
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 

@routes.route('/crear_conversacion', methods=['POST'])
def crear_conversacion():
    try:
        if 'user' not in session:
            return jsonify({'status': 'error', 'message': "No s'ha iniciat sessió"}), 401

        data = request.get_json()
        id_usuario2 = data.get('id_usuario2')
                
        if not id_usuario2:
            return jsonify({'status': 'error', 'message': "Falta l'usuari destí"}), 400

        url = f"http://{IP_API}/api/chat/nuevo"
        headers = {'Content-Type': 'application/json'}
        payload = {
            'id_usuario1': session['user'],
            'id_usuario2': id_usuario2
        }
        
        response = requests.post(url, json=payload, headers=headers)
        print(response)
        if response.status_code in [200, 201]:
            return jsonify(response.json())
        else:
            error_msg = response.json().get('error', 'Error en crear conversació')
            return jsonify({'status': 'error', 'message': error_msg}), response.status_code
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@routes.route('/obtener_conversacion/<string:conversacion_id>', methods=['GET'])
def obtener_conversacion(conversacion_id):
    try:
        if 'user' not in session:
            return jsonify({'status': 'error', 'message': "No s'ha iniciat sessió"}), 401
        # Obtener el nombre del usuario si se envía
        user = session['user']
        url = f"http://{IP_API}/api/chat/mensajes/{conversacion_id}/{user}"
        response = requests.get(url)

        if response.status_code == 200:
            mensajes = response.json()
            processed_messages = []
            for msg in mensajes:
                processed = {
                    'id_remitente': msg['id_remitente'],
                    'mensaje': msg['mensaje'],
                    'fecha_envio': msg['fecha_envio']
                }
                processed_messages.append(processed)
            id = get_user_id(user)
            return jsonify({'messages': processed_messages, 'currentUserId': id})
        else:
            error_msg = response.json().get('error', 'Error en obtenir conversació')
            return jsonify({'status': 'error', 'message': error_msg}), response.status_code
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500




@routes.route('/enviar_mensaje', methods=['POST'])
def enviar_mensaje():
    try:
        if 'user' not in session:
            return jsonify({'status': 'error', 'message': "No s'ha iniciat sessió"}), 401

        data = request.get_json()
        
        url = f"http://{IP_API}/api/chat/mensaje"
        headers = {'Content-Type': 'application/json'}
        payload = {
            'usuario': session['user'],
            'conversacion_id': data.get('id_conversacion'),
            'contenido': data.get('mensaje')
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            return jsonify(response.json())
        else:
            error_msg = response.json().get('error', 'Error en enviar missatge')
            return jsonify({'status': 'error', 'message': error_msg}), response.status_code
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
# Ruta per a la informació de l'usuari
@routes.route('/usuari')
def usuari():
    return render_template('usuari.html')

def get_user_id(user):
    try:
        url = f"http://{IP_API}/api/usuario/id/{user}"
        response = requests.get(url)
        
        if response.status_code == 200:
            id = response.json().get('id')
            return id
        else:
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None