from flask import Flask, request, jsonify
from flask_cors import CORS
from binance.client import Client
import os
from dotenv import load_dotenv
import openai

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configurar la API key de OpenAI desde la variable de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")

# Variable global para mantener el estado de la conexión y el cliente
client_instance = None

@app.route('/connect', methods=['POST'])
def connect():
    data = request.json
    api_key = data.get('api_key')
    secret_key = data.get('secret_key')
    print(f"Clave API recibida por el servidor: '{api_key}'") 
    global client_instance
    client_instance = Client(api_key, secret_key)
    try:
        client_instance.ping()
        cuenta = client_instance.get_account()
        saldos = {balance['asset']: float(balance['free']) for balance in cuenta['balances'] if float(balance['free']) > 0}
        print("Conexión exitosa a Binance con API Key:", api_key)
        return jsonify({'status': 'success', 'message': 'Connected successfully', 'saldos': saldos})
    except Exception as e:
        print("Error de conexión:", e)
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/disconnect', methods=['POST'])
def disconnect():
    global client_instance
    client_instance = None # Limpiamos la instancia al desconectar
    print("El usuario se ha desconectado desde la interfaz.")
    return jsonify({'status': 'success'})

@app.route('/chat', methods=['POST'])
def handle_chat():
    global client_instance
    data = request.json
    user_message = data.get('message', '').lower()
    ai_response = "Lo siento, no he entendido tu pregunta. Prueba a preguntar '¿cuál es mi saldo?'."

    # 1. Comando específico y rápido para el saldo
    if 'saldo' in user_message:
        if client_instance:
            try:
                cuenta = client_instance.get_account()
                saldos = {balance['asset']: float(balance['free']) for balance in cuenta['balances'] if float(balance['free']) > 0}
                
                if not saldos:
                    ai_response = "No tienes fondos visibles en tu cuenta spot."
                else:
                    response_text = "Tus saldos actuales son:<br>"
                    for asset, amount in saldos.items():
                        response_text += f"- {asset}: {amount:.8f}<br>"
                    ai_response = response_text

            except Exception as e:
                ai_response = f"Hubo un error al consultar tu saldo: {e}"
        else:
            ai_response = "Para ver tu saldo, primero debes conectarte a Binance desde el panel de la izquierda."
        
        return jsonify({'response': ai_response})

    # 2. Para todo lo demás, usamos el cerebro de OpenAI
    try:
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo", # Un modelo rápido y económico para empezar
            messages=[
                {"role": "system", "content": "Eres XioleniBot, un asistente experto en trading de criptomonedas. Eres servicial, directo y vas al grano. Tu objetivo es ayudar a tu dueño a gestionar su robot de trading. No das consejos financieros, solo operas con la información y herramientas que se te proporcionan."},
                {"role": "user", "content": user_message}
            ]
        )
        ai_response = completion.choices[0].message.content
    except Exception as e:
        print(f"Error al contactar con OpenAI: {e}")
        ai_response = "He tenido un problema para conectar con mi cerebro principal. Revisa la consola del servidor para ver el error."

    return jsonify({'response': ai_response})

if __name__ == '__main__':
    app.run(port=5000, debug=True)