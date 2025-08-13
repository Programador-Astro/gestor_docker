from . import logistica_bp
from flask_login import login_required
from flask import render_template, request, jsonify, redirect, url_for, flash, send_from_directory, current_app, render_template_string
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from app.models import *
from io import BytesIO
import tempfile, os, re, fitz 
from app.utils import ler_pedidos_json, salvar_pedidos_json, limpar_texto, geocodificar_google
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import dotenv
dotenv.load_dotenv()
from app import db
UPLOAD_FOLDER = os.path.abspath(os.getenv("UPLOAD_FOLDER", "uploads"))

@logistica_bp.route('/')
#@login_required
def root():
    usuario = Usuario.query.filter_by(email="davi@gmail.com").first()
    return f"{usuario.pwd}"
@logistica_bp.route('/cadastrar_pedido', methods = ['POST'])
@login_required
def rotas():
    if request.method == 'POST':
        if 'pdf_pedido' in request.files:
            pdf_file = request.files['pdf_pedido']
            try:
                pdf_bytes = pdf_file.read()
                pdf_stream = BytesIO(pdf_bytes)
                doc = fitz.open(stream=pdf_stream, filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()

                # Extração dos dados
                codigo_pedido_match = re.search(r"Nº Pedido:\s*(\d+)", text)
                cliente_match = re.search(r"\nCliente:\s*(.+)", text)
                cod_cliente_match = re.search(r"Cod\.Cliente:\s*(\d+)", text)
                endereco_match = re.search(r"Endereço:\s*(.+)", text)
                bairro_match = re.search(r"Bairro:\s*(.+)", text)
                cidade_match = re.search(r"Cidade:\s*(.+)", text)
                uf_match = re.search(r"UF:\s*([A-Z]{2})", text)
                produtos_e_qtds = re.findall(r"\d+\s+DG\s+--\s+(.+?)\s+--\s+CX 10L\s+CX 10L\s+(\d+,\d+)", text)

                # Limpeza dos dados
                codigo_pedido = codigo_pedido_match.group(1) if codigo_pedido_match else "Não encontrado"
                cliente = limpar_texto(cliente_match.group(1)) if cliente_match else "Não encontrado"
                cod_cliente = cod_cliente_match.group(1) if cod_cliente_match else "Não encontrado"
                endereco = limpar_texto(endereco_match.group(1)) if endereco_match else "Não encontrado"
                bairro = limpar_texto(bairro_match.group(1)) if bairro_match else "Não encontrado"
                cidade = limpar_texto(cidade_match.group(1)) if cidade_match else "Não encontrado"
                uf = uf_match.group(1) if uf_match else "Não encontrado"

                

                pedido_data = {
                    "codigo_pedido": codigo_pedido,
                    "cliente": cliente,
                    "cod_cliente": cod_cliente,
                    "endereco": endereco,
                    "bairro": bairro,
                    "cidade": cidade,
                    "uf": uf,
                    "produtos": [{"nome": nome.strip(), "quantidade": qtd} for nome, qtd in produtos_e_qtds],
                    "nome_arquivo_original": pdf_file.filename
                }

                pedidos = ler_pedidos_json()
                pedidos.append(pedido_data)
                salvar_pedidos_json(pedidos)

                # Junta o endereço completo
                endereco_completo = f"{endereco}, {bairro}, {cidade} - {uf}"

                # Geocodifica
                lat, lng = geocodificar_google(endereco_completo)
                print(f"Latitude: {lat}, Longitude: {lng}")
                
                return jsonify({"status": "success", "message": "Pedido cadastrado com sucesso!"})
            

            except Exception as e:
                # retornar uma mensagem de erro
                #flash(f"Erro ao processar o PDF: {e}", "danger")
                return jsonify({"status": "error", "message": f"Erro ao processar o PDF: {str(e)}"})
                # return f"Erro ao processar o PDF: {e}"
        else:
            # retornar uma mensagem de erro
            return jsonify({"status": "error", "message": "Nenhum arquivo PDF enviado."})
            #return "Nenhum arquivo PDF enviado."


@logistica_bp.route("/veiculos", methods=["GET", "POST"])
def get_veiculos():
    if request.method == "GET":
        # Exemplo: lista fixa (na prática você buscaria no banco)
        placas = []
        pl = Veiculos.query.all()
        for veiculo in pl:
            placas.append(veiculo.placa)
        # Retorna a lista de placas como JSON

        return jsonify(placas)

    #cadastro
    if request.method == "POST":
        data = request.get_json()
        placa = data.get("placa")
        modelo = data.get("modelo")
        ano = data.get("ano")
        capacidade = data.get("capacidade")
        novo_veiculo = Veiculos(placa=placa, modelo=modelo, ano=ano, capacidade=capacidade)
        db.session.add(novo_veiculo)
        db.session.commit()
        return jsonify({"message": "Veículo cadastrado com sucesso!"}), 201

@logistica_bp.route('/checklist', methods=['POST'])
def checklist():
    placa = request.form.get("placa")
    km = request.form.get("km")
    temperatura = request.form.get("temperatura")
    combustivel = request.form.get("combustivel")
    
    novo_checklist = Checklist(
        placa=placa,
        km=km,
        temperatura=temperatura,
        combustivel=combustivel)
    db.session.add(novo_checklist)
    db.session.flush()
    print(f"Checklist adicionado: {placa}, KM: {km}, Temperatura: {temperatura}, Combustível: {combustivel}")
    fotos = {}
    for campo in ["fotoFrontal", "fotoTraseira", "fotoLateral1", "fotoLateral2"]:
        arquivo = request.files.get(campo)
        if arquivo:
            ext = os.path.splitext(secure_filename(arquivo.filename))[1]  # pega extensão
            filename = f"{novo_checklist.id}_{placa}_{campo}{ext}"  # novo nome
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            arquivo.save(filepath)
            fotos[campo] = filepath
    db.session.commit()
    # Aqui você pode salvar as infos no banco
    return jsonify({"status": "ok", "fotos_salvas": fotos})

@logistica_bp.route('/checklist/<placa>', methods=['GET'])
def get_checklist(placa):
    checklists = Checklist.query.filter_by(placa=placa).all()
    print("UPLOAD_FOLDER =", UPLOAD_FOLDER)
    print("Arquivos disponíveis:", os.listdir(UPLOAD_FOLDER))

    if not checklists:
        return jsonify({"message": "Nenhum checklist encontrado para esta placa"}), 404

    checklist_data = []
    for c in checklists:
        fotos = []
        if os.path.exists(UPLOAD_FOLDER):
            for arquivo in os.listdir(UPLOAD_FOLDER):
                if arquivo.startswith(f"{c.id}_{c.placa}_"):
                    fotos.append({
                        "nome": arquivo,
                        "url": f"/uploads/{arquivo}"
                    })

        checklist_data.append({
            "id": c.id,
            "placa": c.placa,
            "km": c.km,
            "temperatura": c.temperatura,
            "combustivel": c.combustivel,
            "data": c.data.strftime("%Y-%m-%d %H:%M:%S"),
            "fotos": fotos
        })

    return jsonify(checklist_data)

@logistica_bp.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@logistica_bp.route('/teste')
def teste():
    UPLOAD_FOLDER = os.path.abspath(os.getenv("UPLOAD_FOLDER", "uploads"))
    return f"{UPLOAD_FOLDER}"
