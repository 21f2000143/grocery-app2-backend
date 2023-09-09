from flask import render_template, request, redirect, url_for, flash, make_response, session
from flask import current_app as app
from application.database import db
from .models import *
from datetime import datetime
from functools import wraps
import numbers
from flask_security import current_user, roles_required, auth_required

# Helpful functions
def add_role(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user:
            roles=app.security.datastore.find_or_create_role(
                name="user", permissions=["user-read", "user-write"]
            )
            db.session.commit()
            app.security.datastore.add_role_to_user(current_user,roles)
            db.session.commit()
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
            db.session.add(new_category)
            db.session.commit()
            flash('Category added successfully!', 'success')
        except:
            db.session.rollback()
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
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        try:
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
        except:
            db.session.rollback()
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
            db.session.commit()
            flash('Product updated successfully!', 'success')
        except:
            db.session.rollback()
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
            db.delete(product)
            db.session.commit()
            flash('Product deleted successfully!', 'success')
        except:
            db.session.rollback()
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
            db.session.commit()
            flash('Category updated successfully!', 'success')
        except:
            db.session.rollback()
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
            db.delete(category)
            db.session.commit()
            flash('Category deleted successfully!', 'success')
        except:
            db.session.rollback()
            flash('An error occurred while deleting the category.', 'danger')

    return render_template('delete_category.html', category=category)
