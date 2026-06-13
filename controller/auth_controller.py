import jwt
import os
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from repository.usuario_repository import UsuarioRepository
from models.usuario import Usuario

bp_auth = Blueprint('usuario', __name__, url_prefix='/api/auth')

usuario_repository = UsuarioRepository()

def gerar_token(usuario):
    payload = {
        'id': usuario.id,
        'email': usuario.email,
        'nome': usuario.nome,
        'exp': datetime.now(timezone.utc) + timedelta(hours=8)
    }
    return jwt.encode(payload, os.getenv('JWT_SECRET_KEY'), algorithm='HS256')


@bp_auth.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Dados não enviados'}), 400

    email = dados.get('email')
    senha = dados.get('senha')

    if not email or not senha:
        return jsonify({'erro': 'Email e senha são obrigatórios'}), 400

    usuario = usuario_repository.verificar_login(email, senha)
    if not usuario:
        return jsonify({'erro': 'Email ou senha inválidos'}), 401

    token = gerar_token(usuario)
    return jsonify({
        'token': token,
        'usuario': {
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email
        }
    }), 200


@bp_auth.route('/cadastrar', methods=['POST'])
def cadastrar():

    dados = request.get_json()

    if not dados:
        return jsonify({
            'erro': 'Dados não enviados'
        }), 400

    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')
    telefone = dados.get('telefone')

    if not all([nome, email, senha]):
        return jsonify({
            'erro': 'Nome, email e senha são obrigatórios'
        }), 400


    usuario_existente = usuario_repository.buscar_por_email(email)

    if usuario_existente:
        return jsonify({
            'erro': 'E-mail já cadastrado'
        }), 409


    usuario = Usuario(
        nome=nome,
        email=email,
        senha=senha,
        telefone=telefone
    )


    usuario_repository.cadastrar(usuario)

    return jsonify({
        'mensagem': 'Conta criada com sucesso!'
    }), 201


@bp_auth.route('/redefinir-senha', methods=['POST'])
def redefinir_senha():
    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Dados não enviados'}), 400

    email = dados.get('email')
    nova_senha = dados.get('nova_senha')
    confirmar_senha = dados.get('confirmar_senha')

    if not email or not nova_senha:
        return jsonify({'erro': 'E-mail e nova senha são obrigatórios'}), 400

    if nova_senha != confirmar_senha:
        return jsonify({'erro': 'As senhas não coincidem'}), 400

    usuario = usuario_repository.buscar_por_email(email)
    if not usuario:
        return jsonify({'erro': 'Nenhuma conta encontrada com este e-mail'}), 404

    usuario_repository.atualizar_senha(usuario.id, nova_senha)
    return jsonify({'mensagem': 'Senha redefinida com sucesso!'}), 200