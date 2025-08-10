from . import auth_bp
from flask import request, redirect, jsonify, render_template_string, url_for, current_app
from app.models import users
from app import db, mail
from flask_mail import Message
from app.utils import validator
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
import jwt, os, dotenv
dotenv.load_dotenv()
nada = os.getenv('JWT_SECRET_KEY')
@auth_bp.route('/')
def root():
    return f'{nada}'

@auth_bp.route('/register', methods = ['PUT'])
#@login_required
def register():
    """Para registrar um novo usuario é preciso informar [
    users(email, senha, confirmação da senha,)
    perfil(nome, sobre nome, cargo, setor, tell, cnh se aplicavel)
    ]"""
    #Pegando os dados do front
    argumentos = request.get_json()

    #Carregando o usuario
    usuario_existente = users.Usuario.query.filter_by(email = argumentos['email']).first()

    #Aqui é verificado se o email já está cadastrado
    if usuario_existente:
        return 'Email já cadastrado', 400
    
    #Aqui passamos o email pelo (validator)
    flag_email = validator.validar_dado(argumentos['email'], 'email')
    
    #Aqui passamos a senha pelo (validator)
    flag_senha = validator.validar_dado(argumentos['pwd'], 'senha')
        
    #Aqui é varificado se a senha são iguais
    
    if argumentos['pwd'] == argumentos['confirmar_pwd']:

        if flag_senha == True and flag_email == True:#Somente quando as flag dos dados forem True que vamos ao commit

            novo_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            senhaHash = generate_password_hash(argumentos['pwd'])
            #verificação caso o perfil tenha CNH
            if 'cnh' in argumentos:    
                new_perfil = users.Perfil(nome=argumentos['nome'].captalize(), sobrenome=argumentos['sobrenome'].captalize(), tell=argumentos['tell'], setor=argumentos['setor'].lower(), cargo=argumentos['cargo'].lower(), cnh=argumentos['cnh'])
            else:
                new_perfil = users.Perfil(nome=argumentos['nome'], sobrenome=argumentos['sobrenome'], tell=argumentos['tell'], setor=argumentos['setor'].lower(), cargo=argumentos['cargo'].lower())

            #Adc os dados
            db.session.add(new_perfil)
            db.session.flush()
            new_usuario = users.Usuario(email=argumentos['email'], pwd=senhaHash,perfil_id=new_perfil.id, autor=current_user.perfil.id, token=novo_token)


            #Salva os dados
            db.session.add(new_usuario)
            db.session.commit()

            #Apos criar o usuario o email é enviado com o token para confirmação
            msg = Message("Teste Flask-Mail", sender='daviragnar226@gmail.com', recipients=[argumentos['email']])
            html_body = render_template_string("""
                    <h2>Olá {{ nome }},</h2>
                    <p>Seja bem-vindo(a) à nossa plataforma!</p>
                    <p> Por favor, confirme seu e-mail e altere sua senha clicando no botão abaixo:</p>
                    <p>
                        <a href="{{ link_confirmacao }}" style="background-color:#4CAF50; color:white; padding:10px 20px; text-decoration:none; border-radius:5px;">
                            Confirmar e-mail
                        </a>
                    </p>
                    <p>Se você não criou esta conta, pode ignorar este e-mail.</p>
                    <br>
                    <p>Abraços,<br><strong>Equipe Astro Gelato</strong></p>
                """, nome=argumentos['nome'], link_confirmacao=f"https://seudominio.com/confirmar_email?token={novo_token}")
            
            msg.html = html_body
            mail.send(msg)


            return f'Cadastrado com sucesso  - {argumentos["email"]}', 200
        else: return 'Tente outra senha', 400
    else: return 'As senhas não são iguais!', 400

@auth_bp.route('/login', methods = ['POST'])
def login():


    argumentos = request.get_json()
    usuario = users.Usuario.query.filter_by(email=argumentos['email']).first()
    if usuario:
        #Verificando se a senha está correta
        if  check_password_hash(usuario.pwd, argumentos['pwd']) == True:
            login_user(usuario)

            # Identity deve ser string ou int (aqui vamos usar o email)
            access_token = create_access_token(identity=usuario.email, additional_claims={
                "id": usuario.id,
                "email": usuario.email
            })

            decoded_token = jwt.decode(
                access_token,
                os.getenv('JWT_SECRET_KEY'),
                algorithms=["HS256"]
            )

            usuario.iat = decoded_token['iat']
            usuario.jwt = access_token
            db.session.commit()
            return jsonify({
            "access_token": access_token,
            "message": "Logado com sucesso"
        }), 200
        
        else: return jsonify({
            'message': 'Senha incorreta'
                              }), 401
        
    else: return jsonify({
            'message': 'Algo deu errado'
                              }), 401

@auth_bp.route('/alterar_senha', methods=['PUT'])
def alterar_senha():
    argumentos = request.get_json()
    usuario = users.Usuario.query.filter_by(id=argumentos['id']).first()

    if usuario:
        if argumentos['nova_senha'] == argumentos['confirmar_senha']:

            #Verificando se é igual a senha antiga
            if check_password_hash(usuario.pwd, argumentos['nova_senha']) == True:
                return "A nova senha não pode ser igual a senha antiga", 400
            elif check_password_hash(usuario.pwd, argumentos['nova_senha']) == False:
                #Verificando se a nova senha está dentro dos padrões
                if validator.validar_dado(argumentos['nova_senha'], 'senha') == True:
                    new_pwd = generate_password_hash(argumentos['nova_senha'])
                    usuario.pwd = new_pwd
                    usuario.falg_alter_pwd = True
                    db.session.add(usuario)
                    db.session.commit()
                    return "Senha alterada com sucesso!", 200
                
                else: return 'A senha não está seguindo as regras', 400
        else: return 'A senhas não são iguais', 400
    else: return 'Usuario não encontrado', 400

@auth_bp.route('/confirmar_email', methods=['PUT'])
def confirmar_email():
    argumentos = request.get_json()
    usuario = users.Usuario.query.filter_by(id=argumentos['id']).first()
    if argumentos['token'] == usuario.token:
        usuario.flag_confirm_email = True
        db.session.add(usuario)
        db.session.commit()
        return 'Email confirmado com sucesso!', 200
    else: return 'Não foi possivel confirmar o email', 400

@auth_bp.route('/update_user', methods=['PUT'])
@login_required
def update_user():
    try:
        argumentos = request.get_json()
        update_user = users.Usuario.query.filter_by(id = argumentos['id']).first()
        if update_user == None:
            return 'Usuario não encontrado', 400

        for chave, valor in argumentos.items():
            print('chave', chave)
            if chave == 'email' or chave == "flag_alter_pwd" or chave == 'flag_confirm_email' or chave == 'status':

                setattr(update_user, chave, valor)
            if  chave == 'pwd':
                setattr(update_user, chave, generate_password_hash(valor))
                
            if chave == 'nome' or chave == "sobrenome" or chave == 'tell' or chave == 'setor' or chave == 'cargo' or chave == 'cnh':

                setattr(update_user.perfil, chave, valor)


        db.session.add(update_user)
        db.session.flush()

        db.session.commit()
        print(update_user.email)        
        return jsonify(argumentos)
    except:
        return "Não foi possivel atualizar o usuario", 400

@auth_bp.route('/logout', methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return 'deslogado'