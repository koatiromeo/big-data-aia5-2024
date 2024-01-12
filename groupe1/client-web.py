from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length
from functools import wraps
import requests
import os
import base64
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key for secure session management
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Set session lifetime to 7 days
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, user_id, username, uroles):
        self.id = user_id
        self.username = username
        self.uroles = uroles


@login_manager.user_loader
def load_user(user_id):
    print(user_id, session.get('username'), session.get('uroles'))
    # This function is called to load a user from the ID stored in the session
    return User(user_id, session.get('username'), session.get('uroles'))


def redirect_authenticated_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            # Redirect to the appropriate panel based on user roles
            if 'admin' in current_user.uroles:
                return redirect(url_for('admin_panel'))
            elif 'manager' in current_user.uroles:
                return redirect(url_for('manager_panel'))
            # Add more conditions as needed for other roles

        return f(*args, **kwargs)

    return decorated_function

def roles_required(*roles):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if current_user.is_authenticated and any(role in current_user.uroles for role in roles):
                return func(*args, **kwargs)
            else:
                flash('Permission denied. You do not have the required roles.', 'error')
                return redirect(url_for('login'))

        return decorated_view

    return wrapper

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET', 'POST'])
@redirect_authenticated_user
def login():
    error = None  # Initialize error to None
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Make a request to the API to authenticate the user
        api_url = 'http://127.0.0.1:5000/login'
        data = {'username': username, 'password': password}
        response = requests.post(api_url, json=data)

        if response.status_code == 200:
            user_info = response.json()
            user = User(user_info['ID'], user_info['username'], user_info['uroles'])
            login_user(user)

            session['access_token'] = user_info['access_token']
            session['username'] = user_info['username']
            session['uroles'] = user_info['uroles']
            flash('Login successful!', 'success')

            # Redirect to the appropriate panel based on user roles
            if 'admin' in user.uroles:
                return redirect(url_for('admin_panel'))
            elif 'manager' in user.uroles:
                return redirect(url_for('manager_panel'))

        error = 'Invalid username or password'

    return render_template('login.html', form=form, error=error)



# User creation form
class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Create User')

# User update form
class UpdateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password')
    submit = SubmitField('Update User')

# User deletion form
class DeleteUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    submit = SubmitField('Delete User')




@app.route('/admin_panel')
@login_required
@roles_required('admin')
def admin_panel():
    return render_template('admin_panel.html')


@app.route('/admin/create_user', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        access_token = session.get('access_token')
        api_url = 'http://127.0.0.1:5000/managers'
        headers = {'Authorization': f'Bearer {access_token}'}
        data = {'username': username, 'password': password}
        response = requests.post(api_url, json=data, headers=headers)
        if response.status_code == 200:
            print(response)
            flash('User created successfully!', 'success')
            return redirect(url_for('admin_panel'))
    return render_template('admin_create_user.html', form=form)


@app.route('/admin/list_users')
@login_required
@roles_required('admin')
def admin_list_users():
    try:
        # Make a GET request to the API to retrieve all users
        api_url = 'http://127.0.0.1:5000/managers'
        access_token = session.get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            users_data = response.json()
            return render_template('admin_list_users.html', users=users_data)
        else:
            return render_template('error.html', error=f"Failed to retrieve users. Status code: {response.status_code}")

    except Exception as e:
        # Handle any exception that might occur during the request
        return render_template('error.html', error=str(e))


@app.route('/admin/update_user', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_update_user():
    form = UpdateUserForm()
    if form.validate_on_submit():
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_panel'))
    return render_template('admin_update_user.html', form=form)


@app.route('/admin/delete_user', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_delete_user():
    form = DeleteUserForm()
    if form.validate_on_submit():
        flash('User deleted successfully!', 'success')
        return redirect(url_for('admin_panel'))
    return render_template('admin_delete_user.html', form=form)



@app.route('/manager_panel')
@login_required
@roles_required('manager')
def manager_panel():
    return render_template('manager_panel.html')

@app.route('/list/cnis')
@login_required
@roles_required('manager')
def list_cnis():
    try:
        # Make a GET request to the API to retrieve all users
        api_url = 'http://127.0.0.1:5000/cnis'
        access_token = session.get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            cnis_data = response.json()
            data_json = {'data':[{"DT_RowId":f"row_{p.carte_id}", "ID":p.carte_id, "nom":p.nom, "prenom":p.prenom, "lieu_naissance":p.lieu_naissance, "date_naissance":p.date_naissance, "sexe":p.sexe, "actions":p.button_actions()} for p in cnis_data]}
            return jsonify(data_json)
        else:
            return render_template('error.html', error=f"Failed to retrieve users. Status code: {response.status_code}")

    except Exception as e:
        # Handle any exception that might occur during the request
        return render_template('error.html', error=str(e))


@app.route('/cni/create', methods=['POST'])
@login_required
@roles_required('manager')
def manger_create_cni():
    carte_id = int(request.form['carte_id'])
    nom = request.form['nom']
    prenom = request.form['prenom']
    date_naissance = request.form['date_naissance']
    lieu_naissance = request.form['lieu_naissance']
    profession = request.form['profession']
    image_blob_1 = request.files['image_blob_1']
    image_blob_2 = request.files['image_blob_2']
    image_blob_3 = request.files['image_blob_3']
    image_blob_4 = request.files['image_blob_4']
    print(image_blob_4)
    try:
        # Make a GET request to the API to retrieve all users
        access_token = session.get('access_token')
        api_url = 'http://127.0.0.1:5000/cnis'
        headers = {'Authorization': f'Bearer {access_token}'}
        data = {
                'carte_id': carte_id, 
                'nom': nom, 
                'prenom': prenom, 
                'date_naissance': date_naissance, 
                'lieu_naissance': lieu_naissance,
                'profession': profession,
                'image_blob_1': image_blob_1,
                'image_blob_2': image_blob_2,
                'image_blob_3': image_blob_3,
                'image_blob_4': image_blob_4,
                
                }
        response = requests.post(api_url, json=data, headers=headers)
        if response.status_code == 200:
            return  {'status':'success','mensagem':'cni supprimer avec sucess!'}
        else:
            return  {'status':'error','mensagem':'Une erreur est survenir lors de la suppression de cni veuillez essai plus tard!'}

    except Exception as e:
        # Handle any exception that might occur during the request
        return{'status':'error','mensagem':'Une erreur est survenir lors de la suppression de cni veuillez essai plus tard!'}


       

@app.route('/cnis/delete', methods=['POST'])
@login_required
@roles_required('manager')
def manager_delete_cnis():
    carte_id = int(request.form['id'])
    try:
        # Make a GET request to the API to retrieve all users
        api_url = f'http://127.0.0.1:5000/cnis/{carte_id}'
        access_token = session.get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.delete(api_url, headers=headers)

        if response.status_code == 200:
            users_data = response.json()
            return  {'status':'success','mensagem':'cni supprimer avec sucess!'}
        else:
            return  {'status':'error','mensagem':'Une erreur est survenir lors de la suppression de cni veuillez essai plus tard!'}

    except Exception as e:
        # Handle any exception that might occur during the request
        return{'status':'error','mensagem':'Une erreur est survenir lors de la suppression de cni veuillez essai plus tard!'}




@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('access_token', None)
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
