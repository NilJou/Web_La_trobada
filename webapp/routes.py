# Importació de mòduls necessaris
from flask import Flask, render_template, Blueprint, jsonify, request, session
import requests

# Creació d'un Blueprint anomenat 'routes' per organitzar les rutes
routes = Blueprint('routes', __name__)

# Ruta principal que redirigeix a la pàgina de login
@routes.route('/')
def home():
    """Renderitza la pàgina d'inici (login)"""
    return render_template('login.html')

# Ruta per gestionar el login d'usuaris
@routes.route('/login', methods=['GET', 'POST'])
def login():
    """
    Gestiona tant les sol·licituds GET com POST per al login.
    GET: Mostra el formulari de login
    POST: Processa les dades del formulari i autentica l'usuari
    """
    try:
        if request.method == 'POST':
            # Obtenir dades del formulari
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Configurar la petició a l'API
            url = "http://10.100.0.78:5000/api/login"
            headers = {'Content-Type': 'application/json'}
            payload = {
                "usuari": username,
                "contrasenya": password
            }
            
            # Fer la petició POST a l'API
            response = requests.post(url, json=payload, headers=headers)
            
            # Si la resposta és exitosa (codi 200)
            if response.status_code == 200:
                data = response.json()
                print("Login exitós:", data)
                # Emmagatzemar usuari en sessió
                session['user'] = data.get('user')
                # Redirigir al fòrum
                return render_template('foro.html')
            else:
                # Si falla el login, retornar error
                return jsonify({
                    'status': 'error',
                    'message': response.json().get('error', 'Error en el login')
                }), response.status_code
            
        # Per a sol·licituds GET, mostrar el formulari de login
        return render_template('login.html')
        
    except Exception as e:
        # Gestió d'errors generals
        return jsonify({
            'status': 'error',
            'message': f"S'ha produït un error: {str(e)}"
        }), 500
    
# Ruta per gestionar el registre de nous usuaris
@routes.route('/register', methods=['GET', 'POST'])
def register():
    """
    Gestiona el registre de nous usuaris.
    GET: Mostra el formulari de registre
    POST: Processa el formulari i crea un nou usuari
    """
    try:
        if request.method == 'POST':
            # Obtenir dades del formulari
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # Validacions bàsiques
            if password != confirm_password:
                return render_template('register.html', error="Les contrasenyes no coincideixen")
            
            if not all([username, email, password]):
                return render_template('register.html', error="Es requereix omplir tots els camps")
            
            # Configurar petició a l'API
            url = "http://10.100.0.78:5000/api/register"
            headers = {'Content-Type': 'application/json'}
            payload = {
                "nom_usuari": username,
                "correu": email,
                "contrasenya": password
            }
            
            # Fer petició a l'API
            response = requests.post(url, json=payload, headers=headers)
            print(response)
            
            # Gestionar diferents respostes de l'API
            if response.status_code == 201:  # Codi 201 per a creació exitosa
                return render_template('login.html', success="Usuari registrat correctament. Ara podeu iniciar sessió.")
            elif response.status_code == 409:  # Codi 409 per a conflictes
                conflict_type = response.json().get('conflict_type')
                if conflict_type == 'username':
                    return render_template('register.html', error="L'usuari ja existeix")
                elif conflict_type == 'email':
                    return render_template('register.html', error="El correu ja existeix")
            else:
                error_msg = response.json().get('error', "S'ha produït un error durant el registre")
                return render_template('register.html', error=error_msg)
        
        # Per a sol·licituds GET, mostrar formulari de registre
        return render_template('register.html')
        
    except Exception as e:
        return render_template('register.html', error=f"S'ha produït un error: {str(e)}")

# Ruta per mostrar el fòrum
@routes.route('/foro')
def foro():
    """Renderitza la pàgina del fòrum"""
    return render_template('foro.html')

# Ruta per mostrar l'escàner
@routes.route('/escaner')
def escaner():
    """Renderitza la pàgina de l'escàner de cartes"""
    return render_template('escaner.html')

# Ruta per buscar cartes
@routes.route('/carta/web', methods=['GET', 'POST'])
def carta_web():
    """
    Gestiona la cerca de cartes.
    GET: Mostra la pàgina de cerca
    POST: Processa la cerca i mostra resultats
    """
    try:
        if request.method == 'POST':
            # Obtenir nom de carta del formulari
            nom = request.form.get('nom')
            
            # Validar que s'hagi introduït un nom
            if not nom:
                return render_template('escaner.html', error="Si us plau, introduïu un nom de carta")
            
            # Configurar petició a l'API
            api_url = "http://10.100.0.78:5000/api/carta/web"
            headers = {'Content-Type': 'application/json'}
            payload = {"nom": nom}
            
            # Fer petició a l'API
            response = requests.post(api_url, json=payload, headers=headers)
            
            # Debug: mostrar resposta de l'API
            print(f"[DEBUG] Resposta de l'API (estat {response.status_code}):")
            print(f"Capçaleres: {response.headers}")
            print(f"Contingut: {response.text}")
            
            # Gestionar resposta exitosa
            if response.status_code == 200:
                cartes = response.json()  # Obtenir llista de cartes
                if not cartes:
                    return render_template('escaner.html',
                                         nom_buscat=nom,
                                         error="No s'han trobat cartes amb aquest nom")
                
                return render_template('escaner.html',
                                    nom_buscat=nom,
                                    cartes=cartes,
                                    id=id)
            
            else:
                # Gestionar errors de l'API
                error_msg = response.json().get('error', 'Error en la cerca de cartes')
                return render_template('escaner.html',
                                    error=error_msg)
        
        # Per a sol·licituds GET, mostrar pàgina de cerca
        return render_template('escaner.html')
        
    except requests.exceptions.RequestException as e:
        # Gestionar errors de connexió
        return render_template('escaner.html',
                             error="Error de connexió amb el servidor de cartes")
    except Exception as e:
        # Gestionar errors inesperats
        return render_template('escaner.html',
                             error=f"Error inesperat: {str(e)}")

# Ruta per crear una nova col·lecció
@routes.route('/crear_colleccio', methods=['POST'])
def crear_colleccio():
    """
    Gestiona la creació d'una nova col·lecció.
    POST: Crea una nova col·lecció amb el nom proporcionat
    """
    try:
        # Obtenir dades del formulari
        nom_colleccio = request.form.get('nom_colleccio')
        nom_buscat = request.form.get('nom_buscat')
        
        # Obtenir usuari de la sessió
        usuari_actual = session.get('user')
        if not usuari_actual:
            return render_template('escaner.html', error="No s'ha iniciat sessió")
        
        # Configurar petició a l'API
        url = "http://10.100.0.78:5000/api/colleccions"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "nom_usuari": usuari_actual,
            "nom_colleccio": nom_colleccio,
            "nom_carta": nom_buscat  # Opcional: afegir la carta buscada a la col·lecció
        }
        
        # Fer petició a l'API
        response = requests.post(url, json=payload, headers=headers)
        
        # Gestionar resposta
        if response.status_code == 201:
            return render_template('escaner.html', 
                                nom_buscat=nom_buscat,
                                success="Col·lecció creada correctament")
        else:
            error_msg = response.json().get('error', "Error en crear la col·lecció")
            return render_template('escaner.html',
                                nom_buscat=nom_buscat,
                                error=error_msg)
    
    except Exception as e:
        return render_template('escaner.html',
                            error=f"S'ha produït un error: {str(e)}")

# Ruta per mostrar la col·lecció
@routes.route('/colleccio')
def colleccio():
    """Renderitza la pàgina de col·lecció de cartes"""
    return render_template('colleccio.html')

# Ruta per mostrar el xat
@routes.route('/xat')
def xat():
    """Renderitza la pàgina del xat"""
    return render_template('xat.html')

# Ruta per mostrar el perfil d'usuari
@routes.route('/usuari')
def usuari():
    """Renderitza la pàgina de perfil d'usuari"""
    return render_template('usuari.html')