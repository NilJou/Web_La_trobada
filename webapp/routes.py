from flask import Flask, render_template, Blueprint

routes = Blueprint('routes', __name__)

@routes.route('/')
def home():
    return render_template('pg1.html')

@routes.route('/pg2')
def pg2():
    return render_template('pg2.html')

@routes.route('/pg3')
def pg3():
    return render_template('pg3.html')
