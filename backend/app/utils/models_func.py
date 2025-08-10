from app import db
from app.models import clientes, users
from flask import current_app
import traceback
from datetime import datetime



def salvar_pedido_em_transacao( cliente_data,pedido_data, usuario_id):
    
    try:
        with db.session.begin_nested():
            # Verifica se o cliente já existe
            cliente = clientes.Clientes.query.filter_by(codigo_cliente=cliente_data['cod_cliente']).first()
            if not cliente:
                # Se o cliente não existe, cria um novo
                cliente = clientes.Clientes(
                    nome=cliente_data['cliente'],
                    codigo_cliente=cliente_data['cod_cliente'],
                    endereco=cliente_data['endereco'],
                    bairro=cliente_data['bairro'],
                    cidade=cliente_data['cidade'],
                    uf=cliente_data['uf'],
                    latitude=cliente_data['latitude'],
                    longitude=cliente_data['longitude'],
                    usuario_id=usuario_id
                )
            db.session.add(cliente)
            db.session.flush()
            
            #Verifica se o pedido já existe
            pedido = clientes.Pedido.query.filter_by(codigo_pedido=pedido_data['cod_pedido']).first()
            if pedido:
                return False, "Pedido já existe"
            
            if not pedido:
                #Formatando a data do pedido
                data_objeto = datetime.strptime(pedido_data['emissao_pedido'], "%d/%m/%Y")
                # Se o pedido não existe, cria um novo
                pedido = clientes.Pedido(
                    codigo_pedido=pedido_data['cod_pedido'],
                    cliente_id=cliente.id,
                    data_pedido=data_objeto,
                    nome_arquivo_original=pedido_data.get('nome_arquivo_original'),
                    usuario_id=usuario_id
                )
                #db.session.add(pedido)
                db.session.flush()

                #Cadastrando os produtos do pedido
                #Lista com produtos que ja foram adc ao pedido (SERVE PARA EVITAR QUE O PRODUTO SEJA CADASTRADO MAIS DE UMA VEZ)
                lista_produtos_temp = []
                for produto in pedido_data['produtos']:
                    lista_produtos_temp.append(produto['codigo'])  
                    print(lista_produtos_temp)

            #db.session.commit()
            return True, "Cliente e pedido salvos com sucesso!"

    except Exception as e:
        traceback.print_exc()
        current_app.logger.error(f"Erro ao salvar cliente: {e}")
        db.session.rollback()
        return  e, 'Error ao salvar cliente ou pedido'