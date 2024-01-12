import os

# Générer une clé secrète aléatoire de 32 octets (256 bits)
jwt_secret_key = os.urandom(32).hex()

print(f"Votre JWT_SECRET_KEY générée : {jwt_secret_key}")