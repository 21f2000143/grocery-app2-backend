import os
from flask import Flask, redirect, url_for, render_template, request, flash, session, make_response
from flask_security import Security, current_user, auth_required, hash_password, \
     SQLAlchemySessionUserDatastore, permissions_accepted, roles_required
from application.database import db_session, init_db
from application.models import *
from functools import wraps
from datetime import datetime

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True

# Generate a nice key using secrets.token_urlsafe()
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
# Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
# Generate a good salt using: secrets.SystemRandom().getrandbits(128)
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')
# Don't worry if email has findable domain
app.config["SECURITY_EMAIL_VALIDATOR_ARGS"] = {"check_deliverability": False}
# Enabling new registration.
app.config["SECURITY_REGISTERABLE"] = True
# app.config["WTF_CSRF_ENABLED"] = False
# Setting password length 5
app.config["SECURITY_PASSWORD_LENGTH_MIN"] = 5
# Disabling the auto email sent feature on registration.
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
app.config["SECURITY_POST_LOGIN_VIEW"] = '/authorizing'
app.config["SECURITY_POST_LOGOUT_VIEW"] = '/'
# Assigning the role to users.
app.config["SECURITY_POST_REGISTER_VIEW"] = '/authorizing'

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
app.security = Security(app, user_datastore)

# one time setup
with app.app_context():
    init_db()
    # Create a user and role to test with
    app.security.datastore.find_or_create_role(
        name="admin", permissions=["user-read", "user-write", "user-delete", "user-update"]
    )
    db_session.commit()
    if not app.security.datastore.find_user(email="test@me.com"):
        app.security.datastore.create_user(email="test@me.com",
        password=hash_password("password"), roles=["admin"])
    db_session.commit()

# Helpful functions
def add_role(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user:
            roles=app.security.datastore.find_or_create_role(
                name="user", permissions=["user-read", "user-write"]
            )
            db_session.commit()
            app.security.datastore.add_role_to_user(current_user,roles)
            db_session.commit()
        return func(*args, **kwargs)

    return wrapper
    

# Views
@app.route("/")
def home():
    search_query=None
    search_query = request.args.get('search_query')
    if search_query:
        # Query the database for products matching the search query
        products = Product.query.filter(
            (Product.name.like(f'%{search_query}%')) |
            (Product.category.has(Category.name.like(f'%{search_query}%'))) |
            (Product.manufacture_date.like(f'%{search_query}%')) |
            (Product.rate_per_unit == search_query)
        ).all()
        
        return render_template('base.html', products=products, search_query=search_query)
    
    categories=Category.query.all()
    products=Product.query.all()
    return render_template('base.html', categories=categories,products=products, search_query=search_query)

@auth_required()
@app.route("/authorizing")
def authorize():
    if current_user.roles[0].name=='admin':
        return redirect(url_for('admin_home'))
    else:
        return redirect(url_for('user_home'))

# Views: Manager
@app.route("/admin", methods=['GET', 'POST'])
@auth_required()
@add_role
@roles_required('admin')
def admin_home():
    search_query=None
    search_query = request.args.get('search_query')
    if search_query:
        # Query the database for products matching the search query
        products = Product.query.filter(
            (Product.name.like(f'%{search_query}%')) |
            (Product.category.has(Category.name.like(f'%{search_query}%'))) |
            (Product.manufacture_date.like(f'%{search_query}%')) |
            (Product.rate_per_unit == search_query)
        ).all()
        
        return render_template('manager.html', products=products, search_query=search_query)
    
    categories=Category.query.all()
    products=Product.query.all()
    return render_template('manager.html', categories=categories,products=products, search_query=search_query)

@app.route("/admin/products/under/<string:cat_name>")
@auth_required()
@add_role
@roles_required('admin')
def cat_products(cat_name):
    categories=Category.query.filter_by(name=cat_name).first()
    return render_template('cat_for_man.html', categories=categories)

@app.route("/add_category", methods=['GET', 'POST'])
@auth_required()  # Replace with your authentication decorator
@roles_required('admin')
def add_category():
    if request.method == 'POST':
        name = request.form['name']
        new_category = Category(name=name)

        try:
            db_session.add(new_category)
            db_session.commit()
            flash('Category added successfully!', 'success')
        except:
            db_session.rollback()
            flash('Category with the same name already exists!', 'danger')

    return render_template('add_category.html')

@app.route("/add_product", methods=['GET', 'POST'])
@auth_required()  # Replace with your authentication decorator
@roles_required('admin')
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        manufacture_date = request.form['manufacture_date']
        date_format="%Y-%m-%dT%H:%M"
        manufacture_date=datetime.strptime(manufacture_date, date_format)
        expiry_date = request.form['expiry_date']
        expiry_date=datetime.strptime(expiry_date, date_format)
        rate_per_unit = request.form['rate_per_unit']
        stock = request.form['stock']
        unit = request.form['unit']
        category_id = request.form['category_id']

        new_product = Product(
            name=name,
            manufacture_date=manufacture_date,
            expiry_date=expiry_date,
            rate_per_unit=rate_per_unit,
            unit=unit,
            category_id=category_id,
            stock=stock
        )
        db_session.add(new_product)
        db_session.commit()
        flash('Product added successfully!', 'success')
        try:
            db_session.add(new_product)
            db_session.commit()
            flash('Product added successfully!', 'success')
        except:
            db_session.rollback()
            flash('An error occurred while adding the product.', 'danger')
    categories=Category.query.all()
    return render_template('add_product.html', categories=categories)

# View for updating a product
@app.route("/update_product/<int:product_id>", methods=['GET', 'POST'])
@auth_required()  # Replace with your authentication decorator
@roles_required('admin')
def update_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        flash('Product not found!', 'danger')
        return redirect(url_for('home'))  # Redirect to the home page or another appropriate page

    if request.method == 'POST':
        product.name = request.form['name']
        date_format="%Y-%m-%dT%H:%M"
        product.manufacture_date = datetime.strptime(request.form['manufacture_date'], date_format)
        product.expiry_date = datetime.strptime(request.form['expiry_date'], date_format)
        product.rate_per_unit = request.form['rate_per_unit']
        product.unit = request.form['unit']
        product.category_id = request.form['category_id']
        product.stock = request.form['stock']

        try:
            db_session.commit()
            flash('Product updated successfully!', 'success')
        except:
            db_session.rollback()
            flash('An error occurred while updating the product.', 'danger')

    return render_template('update_product.html', product=product)

# View for deleting a product
@app.route("/delete_product/<int:product_id>", methods=['GET', 'POST'])
@auth_required()  # Replace with your authentication decorator
@roles_required('admin')
def delete_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        flash('Product not found!', 'danger')
        return redirect(url_for('home'))  # Redirect to the home page or another appropriate page

    if request.method == 'POST':
        try:
            db_session.delete(product)
            db_session.commit()
            flash('Product deleted successfully!', 'success')
        except:
            db_session.rollback()
            flash('An error occurred while deleting the product.', 'danger')

    return render_template('delete_product.html', product=product)

# View for updating a category
@app.route("/update_category/<int:category_id>", methods=['GET', 'POST'])
@auth_required()  # Replace with your authentication decorator
def update_category(category_id):
    category = Category.query.get(category_id)

    if not category:
        flash('Category not found!', 'danger')
        return redirect(url_for('home'))  # Redirect to the home page or another appropriate page

    if request.method == 'POST':
        category.name = request.form['name']

        try:
            db_session.commit()
            flash('Category updated successfully!', 'success')
        except:
            db_session.rollback()
            flash('An error occurred while updating the category.', 'danger')

    return render_template('update_category.html', category=category)
# View for deleting a category
@app.route("/delete_category/<int:category_id>", methods=['GET', 'POST'])
@auth_required()  # Replace with your authentication decorator
def delete_category(category_id):
    category = Category.query.get(category_id)

    if not category:
        flash('Category not found!', 'danger')
        return redirect(url_for('home'))  # Redirect to the home page or another appropriate page

    if request.method == 'POST':
        try:
            db_session.delete(category)
            db_session.commit()
            flash('Category deleted successfully!', 'success')
        except:
            db_session.rollback()
            flash('An error occurred while deleting the category.', 'danger')

    return render_template('delete_category.html', category=category)


# Views: User
@app.route("/user")
@auth_required()
@add_role
@roles_required('user')
def user_home():
    (request.cookies)
    search_query=None
    search_query = request.args.get('search_query')
    if search_query:
        # Query the database for products matching the search query
        products = Product.query.filter(
            (Product.name.like(f'%{search_query}%')) |
            (Product.category.has(Category.name.like(f'%{search_query}%'))) |
            (Product.manufacture_date.like(f'%{search_query}%')) |
            (Product.rate_per_unit == search_query)
        ).all()
        
        return render_template('user.html', products=products, search_query=search_query)
    
    categories=Category.query.all()
    products=Product.query.all()
    response=make_response(render_template('user.html', categories=categories,products=products, search_query=search_query))
    response.set_cookie('cart','',expires=0)
    (response)
    return response

@app.route('/mycart')
@auth_required()
@add_role
@roles_required('user')
def mycart():
    product_ids=request.cookies.get('cart', None)
    if product_ids:
        product_ids = list(map(int, product_ids.split(',')))
        products = db_session.query(Product).filter(Product.id.in_(product_ids)).all()
        products_dic={}
        products_dic['product']=[]
        products_dic['quantity']=[]
        products_dic['total_price']=0
        for product in products:
            products_dic['product'].append(product)
            available_qty=(product_ids.count(product.id), 'available') if product.stock> product_ids.count(product.id) else (product.stock, 'max')
            products_dic['quantity'].append(available_qty)
            products_dic['total_price']+=available_qty[0]*product.rate_per_unit
        flash('Thank you for your purchase!', 'success')
        session['product_ids']=product_ids
        return render_template('mycart.html',products_dic=products_dic)
    else:
        flash('Please add altlest one item into your cart!')
        return redirect(url_for('user_home'))
    
@app.route('/pay', methods=['GET', 'POST'])
@auth_required()
@add_role
@roles_required('user')
def pay():
    product_ids=session['product_ids']
    if product_ids:
        products = db_session.query(Product).filter(Product.id.in_(product_ids)).all()
        products_dic={}
        products_dic['product']=[]
        products_dic['quantity']=[]
        products_dic['total_price']=0
        for product in products:
            products_dic['product'].append(product)
            products_dic['quantity'].append(product_ids.count(product.id))
            products_dic['total_price']+=product_ids.count(product.id)*product.rate_per_unit
        # try:
        for i in range(len(products_dic['product'])):
            amount_paid=products_dic['product'][i].rate_per_unit* products_dic['quantity'][i]
            product_name = products_dic['product'][i].name
            quantity = products_dic['quantity'][i]
            order_date = datetime.now()
            user_id = current_user.id
            order=Order(amount_paid=amount_paid,quantity=quantity,product_name=product_name,order_date=order_date,user_id=user_id)
            db_session.add(order)
            db_session.commit()
            products_dic['product'][i].stock-=products_dic['quantity'][i]
            db_session.commit()
            ('commiting orders in the database')
        session.pop('product_ids')
        flash('Thank you for your purchase!', 'success')
        return redirect(url_for('user_home'))
        # except:
        #     db_session.rollback()
    flash('Something went wrong!', 'failure')
    return redirect(url_for('user_home'))



if __name__ == '__main__':
    # run application (can also use flask run)
    app.run(debug=True)
