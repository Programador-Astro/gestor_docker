import re, os, time, json
from flask import current_app
from app.models import clientes
from app import db


JSON_DATABASE = 'pedidos.json'
def ler_pedidos_json():
    """Lê os dados dos pedidos do arquivo JSON com codificação UTF-8."""
    try:
        with open(JSON_DATABASE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def salvar_pedidos_json(pedidos):
    """Salva a lista de pedidos no arquivo JSON, garantindo a codificação UTF-8."""
    with open(JSON_DATABASE, 'w', encoding='utf-8') as f:
        json.dump(pedidos, f, indent=4, ensure_ascii=False)

def limpar_texto(texto):
        if not texto:
            return ""
        texto = texto.strip()
        texto = re.sub(r'[\r\n]+', ' ', texto)  # Remove quebras de linha
        texto = re.sub(r'/[A-Za-z]?$', '', texto)  # Remove / ou /(letra) no final
        texto = re.sub(r'\s+', ' ', texto)  # Normaliza espaços
        return texto.strip()


   

import googlemaps
import time

# Sua chave da API
API_KEY = "AIzaSyAjyHz26Rhxzpc3uZt5IhWvFuzewQ_RBXA"

# Cria o cliente do Google Maps
gmaps = googlemaps.Client(key=API_KEY)

# Limite de queries por segundo (QPS)
QPS = 5
WAIT_TIME = 1 / QPS

def geocodificar_google(endereco):
    print(f"🔎 Geocodificando: {endereco}")
    try:
        resultado = gmaps.geocode(endereco)
        time.sleep(WAIT_TIME)  # Controla o rate limit
        if resultado:
            location = resultado[0]["geometry"]["location"]
            print(f"📍 Coordenadas: {location['lat']}, {location['lng']}")
            return location['lat'], location['lng']
        else:
            print("⚠️ Endereço não encontrado")
            return None, None
    except Exception as e:
        print(f"⛔ Erro na geocodificação: {e}")
        return None, None



"""ef salvar_pedido_em_transacao(pedido_data, usuario_id):

    try:
        with db.session.begin_nested():
            #Verificando se o cliente já existe
            cliente = db.session.query(clientes.Clientes).filter_by(codigo_cliente=cod_cliente).first()
            print("debug func",cliente.nome)
            
            if not cliente:
                #Criando um novo cliente
                cliente = clientes.Clientes(
                    codigo_cliente=pedido_data['cod_cliente'],
                    nome=pedido_data['cliente'],
                    endereco=pedido_data['endereco'],
                    bairro=pedido_data['bairro'],
                    cidade=pedido_data['cidade'],
                    uf=pedido_data['uf'],
                    latitude=pedido_data['latitude'],
                    longitude=pedido_data['Longitude'],
                    usuario_id=usuario_id
                )
                db.session.add(cliente)
                return True, "Pedido salvo com sucesso"
            #Inserindo no banco de dados
    except Exception as e:
        current_app.logger.error(f"Erro ao salvar pedido: {e}")
        return  f"Erro: {str(e)}"""