from flask import Blueprint, render_template, session, request
from application.models import shop

web = Blueprint('web', __name__)

@web.route('/login')
def login():
    username = request.args.get('username')
    password = request.args.get('password')
    if username == 'bkisc_admin' and password == 'super_secret_password':
        session['admin'] = True

@web.route('/')
def index():
    return render_template('index.html', products=shop.all_products())

@web.route('/view/<product_id>')
def product_details(product_id):
    product = shop.select_by_id(product_id)
    return render_template('item.html', product=product)

@web.route('/admin')
def admin():
    if session.get('admin'):
        return render_template('index.html', products=shop.admin_select_all())