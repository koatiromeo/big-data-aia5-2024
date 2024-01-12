import mysql.connector
from mysql.connector import errorcode
import bcrypt

# Fonction pour créer les tables dans MySQL
def create_tables():
    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'database': 'projet-hadoop',
        'raise_on_warnings': True
    }

    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Création de la table 'cnis'
        cnis_table_query = """CREATE TABLE IF NOT EXISTS cnis (carte_id VARCHAR(255) PRIMARY KEY, nom VARCHAR(255), prenom VARCHAR(255), date_naissance DATE, lieu_naissance VARCHAR(255), profession VARCHAR(255), image_blob_1 BLOB, image_blob_2 BLOB NULL, image_blob_3 BLOB NULL, image_blob_4 BLOB NULL)"""


        cursor.execute(cnis_table_query)

        # Création de la table 'managers'
        managers_table_query = """CREATE TABLE IF NOT EXISTS users (ID INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(255), password VARCHAR(255), uroles VARCHAR(255))"""


        cursor.execute(managers_table_query)


        connection.commit()
        print("Tables créées avec succès.")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Accès refusé : Vérifiez votre nom d'utilisateur et votre mot de passe.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de données spécifiée n'existe pas.")
        else:
            print(err)

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()


# Fonction pour hasher le mot de passe
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Fonction pour insérer un utilisateur dans la base de données MySQL avec mot de passe hashé
def insert_user(username, password, uroles):

    hashed_password = hash_password(password)

    config = {
        'user': 'root',
        'password': '',
        'host': 'localhost',
        'database': 'projet-hadoop',
        'raise_on_warnings': True
    }

    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        query = "INSERT INTO users (username, password, uroles) VALUES (%s, %s, %s)"
        values = (username, hashed_password, uroles)

        cursor.execute(query, values)

        connection.commit()
        print(f"Administrateur inséré avec succès.")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Accès refusé : Vérifiez votre nom d'utilisateur et votre mot de passe.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de données spécifiée n'existe pas.")
        else:
            print(err)

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

# Exemple d'utilisation
if __name__ == "__main__":
    create_tables()
    username = "admin"
    password = "admin@2024"
    uroles = 'admin'
    insert_user(username, password, uroles)
    username = "manager"
    password = "manager@2024"
    uroles = 'manager'
    insert_user(username, password, uroles)
