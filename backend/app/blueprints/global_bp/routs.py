from . import global_bp
from flask import render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
import traceback

from io import BytesIO
import tempfile, os, re, fitz 

from app.utils import ler_pedidos_json, salvar_pedidos_json, limpar_texto, geocodificar_google
from app.utils.models_func import salvar_pedido_em_transacao

from app import db
from app.models import clientes, users



@global_bp.route('/cadastrar_pedido', methods = ['POST'])
@login_required
def root():
    if request.method == 'POST':
        #Verificando se o arquivo do pedido foi passado
        if 'pdf_pedido' in request.files:
            pdf_file = request.files['pdf_pedido']
            
            #Bloco de leitura e extração do PDF
            try:  
                #Leitura padrão do arquivo
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
                produtos_e_qtds = re.findall(r"(\d{6})\s+DG\s+--\s+(.+?)\s+--\s+CX 10L\s+CX 10L\s+(\d+,\d+)", text)

                #produtos_e_qtds = re.findall(r"\d+\s+DG\s+--\s+(.+?)\s+--\s+CX 10L\s+CX 10L\s+(\d+,\d+)", text)
                emissao_pedido_match = re.search(r"Emissão Pedido:\s*(\d{2}/\d{2}/\d{4})", text)
                
                # Limpeza dos dados
                codigo_pedido = codigo_pedido_match.group(1) if codigo_pedido_match else "Não encontrado"
                cliente = limpar_texto(cliente_match.group(1)) if cliente_match else "Não encontrado"
                cod_cliente = cod_cliente_match.group(1) if cod_cliente_match else "Não encontrado"
                endereco = limpar_texto(endereco_match.group(1)) if endereco_match else "Não encontrado"
                bairro = limpar_texto(bairro_match.group(1)) if bairro_match else "Não encontrado"
                cidade = limpar_texto(cidade_match.group(1)) if cidade_match else "Não encontrado"
                uf = uf_match.group(1) if uf_match else "Não encontrado"

                #Bloco de criação de cliente e pedido
                try:

                    # Junta o endereço completo
                    endereco_completo = f"{endereco}, {bairro}, {cidade} - {uf}"
                    # Geocodifica
                    lat, lng = geocodificar_google(endereco_completo)

                    #Transformando o cliente em um OBJETO DICT
                    cliente_data = {
                        "cod_cliente": cod_cliente,
                        "cliente": cliente,
                        "endereco": endereco,
                        "bairro": bairro,
                        "cidade": cidade,
                        "uf": uf,
                        "endereço_completo": endereco_completo,
                        "autor": current_user.id,
                        "latitude": lat,
                        "longitude": lng
                    }
                    #Transformando o PEDIDO em um OBJETO DICT
                    pedido_data = {
                        "cod_pedido": codigo_pedido,
                        "cod_cliente": cod_cliente,
                        "emissao_pedido": emissao_pedido_match.group(1) if emissao_pedido_match else None,
                        "produtos": [{"codigo": codigo.strip(), "nome": nome.strip(), "quantidade": qtd.strip()} for codigo, nome, qtd in produtos_e_qtds],
                        #"produtos": [{"nome": nome.strip(), "quantidade": qtd} for nome, qtd in produtos_e_qtds],
                        "nome_arquivo_original": pdf_file.filename
                    }

                    
                    pedidos = ler_pedidos_json()
                    pedidos.append(cliente_data)
                    salvar_pedidos_json(pedidos)
                    
                    #Inserindo no banco
                    sucesso_cliente, mensagem_cliente = salvar_pedido_em_transacao( cliente_data, pedido_data, current_user.id)
                    if not sucesso_cliente:
                        return mensagem_cliente, 500
                    db.session.commit()
                    return jsonify({"status": "success", "message": "Pedido cadastrado com sucesso!"})
               
                except Exception as e:
                    db.session.rollback()
                    # retornar uma mensagem de erro
                    traceback.print_exc()
                    return jsonify({"status": "error", "message": f"ERROR AO TENTAR SALVAR O CLIENTE: {str(e)}"})
        
        
            #Caso não tenha sido enviado o arquivo
            except Exception as e:
                return jsonify({"status": "error", "message": "Não foi possivel extrair os dados"})
        else:
            return jsonify({"status": "error", "message": "Nenhum arquivo PDF enviado"}), 400
            