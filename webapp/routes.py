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
                "username": username,
                "password": password
            }
            
            # Make the POST request to your API
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("Login successful:", data)
                # Process successful login
                return jsonify({
                    'status': 'success',
                    'user_data': {
                        'id': data.get('id'),
                        'username': data.get('username'),
                        'email': data.get('email')
                    }
                })
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
    
        
@routes.route('/pg2')
def pg2():
    return render_template('pg2.html')

@routes.route('/pg3')
def pg3():
    return render_template('pg3.html')
