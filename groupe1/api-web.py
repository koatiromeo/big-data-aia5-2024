from flask import Flask, request, jsonify, send_file, after_this_request
from flask_mysqldb import MySQL
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, verify_jwt_in_request
import bcrypt
from functools import wraps  # Add this line
import secrets
import os

app = Flask(__name__)

# Configuration de la base de données
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'projet-hadoop'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Session Secrets
app.secret_key = secrets.token_hex(16)

# Configuration de Flask-JWT-Extended
app.config['JWT_SECRET_KEY'] = '8e1188fd85028746c5d98e4a0afda00c7fb2dbdf593fd1d8233da75f29eebf9e'
jwt = JWTManager(app)

# Initialisation de l'extension MySQL
mysql = MySQL(app)

# Middleware pour vérifier le rôle de l'utilisateur
def require_role(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Verify that a valid JWT token is present in the request headers
                verify_jwt_in_request()
                
                # Get the identity (user information) from the JWT token
                current_user = get_jwt_identity()

                # Check if the required role is present in the user's roles
                if current_user and required_role in current_user.get('uroles', []):
                    return func(*args, **kwargs)
                else:
                    return jsonify({"error": "Permission denied"}), 403
            except Exception as e:
                # Handle any exception that might occur during JWT verification
                print(f"JWT Verification Error: {str(e)}")
                return jsonify({"error": "Invalid JWT token"}), 401

        return wrapper

    return decorator

# Fonction de hachage pour le mot de passe
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())





# Endpoint pour l'authentification (login)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data is None or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Both username and password are required"}), 400

    username = data['username']
    password = data['password']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()

   
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        access_token = create_access_token(identity=user)
        return jsonify(access_token=access_token, uroles= user['uroles'], ID=user['ID'], username=user['username']), 200
    else:
        return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect"}), 401
    

@app.route('/login_manager', methods=['POST'])
def login_as_manager():
    data = request.get_json()
    if data is None or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Both username and password are required"}), 400

    username = data['username']
    password = data['password']

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s and uroles='manager'", (username,))
    user = cursor.fetchone()
    cursor.close()

   
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        access_token = create_access_token(identity=user)
        return jsonify(access_token=access_token, uroles= user['uroles'], ID=user['ID'], username=user['username']), 200
    else:
        return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect"}), 401


# CRUD Operations for managing users (accessible only to administrators)
@app.route('/managers', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_all_users():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE uroles='manager'")
    users = cursor.fetchall()
    cursor.close()
    return jsonify(users)

@app.route('/managers', methods=['POST'])
@jwt_required()
@require_role('admin')
def register_user():
    data = request.get_json()
    if data is None or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Both username and password are required"}), 400

    username = data['username']
    password = data['password']
    uroles = 'manager'

    hashed_password = hash_password(password)

    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, password, uroles) VALUES (%s, %s, %s)",
                   (username, hashed_password, uroles))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Utilisateur enregistré avec succès"}), 201

@app.route('/manager/<int:user_id>', methods=['GET'])
@jwt_required()
@require_role('admin')
def get_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE ID = %s and uroles='manager'", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "Utilisateur non trouvé"}), 404




@app.route('/manager/<int:user_id>', methods=['PUT'])
@jwt_required()
@require_role('admin')
def update_user(user_id):
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    hashed_password = hash_password(password) if password else None

    cursor = mysql.connection.cursor()
    update_query = "UPDATE users SET username = %s, password = %s WHERE ID = %s and uroles='manager'"
    cursor.execute(update_query, (username, hashed_password, user_id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Utilisateur mis à jour avec succès"}), 200

@app.route('/manager/<int:user_id>', methods=['DELETE'])
@jwt_required()
@require_role('admin')
def delete_user(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE ID = %s", (user_id,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Utilisateur supprimé avec succès"}), 200



# CRUD Operations for managing cnis records (accessible only to managers)
@app.route('/cnis', methods=['GET'])
@jwt_required()
@require_role('manager')
def get_all_cnis():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM cnis")
    cnis_records = cursor.fetchall()
    cursor.close()
    return jsonify(cnis_records)

@app.route('/cnis/<carte_id>', methods=['GET'])
@jwt_required()
@require_role('manager')
def get_cnis(carte_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM cnis WHERE carte_id = %s", (carte_id,))
    cnis_record = cursor.fetchone()
    cursor.close()
    if cnis_record:
        return jsonify(cnis_record)
    else:
        return jsonify({"error": "Record not found"}), 404


@app.route('/cnis', methods=['POST'])
@jwt_required()
@require_role('manager')
def create_cnis():
    data = request.get_json()
    carte_id = data.get('carte_id')
    nom = data.get('nom')
    prenom = data.get('prenom')
    date_naissance = data.get('date_naissance')
    lieu_naissance = data.get('lieu_naissance')
    profession = data.get('profession')
    image_blob_1 = data.get('image_blob_1')
    image_blob_2 = data.get('image_blob_2')
    image_blob_3 = data.get('image_blob_3')
    image_blob_4 = data.get('image_blob_4')

    cursor = mysql.connection.cursor()

    # Adjust the INSERT query based on your specific table structure
    insert_query = """
    INSERT INTO cnis (
        carte_id, nom, prenom, date_naissance, lieu_naissance, profession, image_blob_1, image_blob_2, image_blob_3, image_blob_4
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        carte_id, nom, prenom, date_naissance, lieu_naissance, profession,
        image_blob_1, image_blob_2, image_blob_3, image_blob_4
    )

    cursor.execute(insert_query, values)
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": "Creating a new cnis record"})


@app.route('/cnis/<carte_id>', methods=['PUT'])
@jwt_required()
@require_role('manager')
def update_cnis(carte_id):
    data = request.get_json()
    nom = data.get('nom')
    prenom = data.get('prenom')
    date_naissance = data.get('date_naissance')
    lieu_naissance = data.get('lieu_naissance')
    profession = data.get('profession')
    image_blob_1 = data.get('image_blob_1')
    image_blob_2 = data.get('image_blob_2')
    image_blob_3 = data.get('image_blob_3')
    image_blob_4 = data.get('image_blob_4')

    cursor = mysql.connection.cursor()

    # Adjust the UPDATE query based on your specific table structure
    update_query = """
    UPDATE cnis SET 
        nom = %s, prenom = %s, date_naissance = %s, lieu_naissance = %s,profession = %s, image_blob_1 = %s, image_blob_2 = %s, image_blob_3 = %s, image_blob_4 = %s
    WHERE carte_id = %s
    """

    values = (
        nom, prenom, date_naissance, lieu_naissance,profession, image_blob_1, image_blob_2, image_blob_3, image_blob_4,
        carte_id
    )

    cursor.execute(update_query, values)
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": f"Updating cnis record with carte_id: {carte_id}"})



@app.route('/cnis/<carte_id>', methods=['DELETE'])
@jwt_required()
@require_role('manager')
def delete_cnis(carte_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM cnis WHERE carte_id = %s", (carte_id,))
    mysql.connection.commit()
    cursor.close()

    return jsonify({"message": f"Deleting cnis record with carte_id: {carte_id}"})



@app.route('/face-maching', methods=['POST'])
@jwt_required()
@require_role('manager')
def upload_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image part in the request"}), 400

        image_file = request.files['image']

        if image_file.filename == '':
            return jsonify({"error": "No selected image file"}), 400

        # Save the image to the current location
        image_path = os.path.join(os.getcwd(), image_file.filename)
        image_file.save(image_path)

        # Perform any additional processing here

        # Delete the image file after the response is sent
        @after_this_request
        def remove_file(response):
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Error deleting image file: {e}")
            return response

        return jsonify({"message": "Image uploaded and processed successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
