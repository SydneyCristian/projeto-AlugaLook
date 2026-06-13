from flask import Blueprint, request, jsonify
from repository.usuario_repository import UsuarioRepository
from repository.animal_repository import AnimalRepository
from repository.solicitacao_repository import SolicitacaoRepository
from decorators import jwt_required

bp_perfil = Blueprint('perfil', __name__, url_prefix='/api/perfil')

usuario_repository = UsuarioRepository()
animal_repository = AnimalRepository()
solicitacao_repository = SolicitacaoRepository()

def animal_para_dict(a, adotante=None):
    d = {
        'id': a.id,
        'nome': a.nome,
        'especie': a.especie,
        'raca': a.raca,
        'idade': a.idade,
        'descricao': a.descricao,
        'foto': a.foto,
        'status': a.status,
        'usuario_id': a.usuario_id,
        'adotante': None
    }
    if adotante:
        d['adotante'] = {
            'nome': adotante.nome,
            'email': adotante.email,
            'telefone': adotante.telefone
        }
    return d


def solicitacao_para_dict(s):
    return {
        'id': s.id,
        'animal_id': s.animal_id,
        'animal_nome': s.animal.nome if s.animal else None,
        'animal_especie': s.animal.especie if s.animal else None,
        'animal_raca': s.animal.raca if s.animal else None,
        'animal_idade': s.animal.idade if s.animal else None,
        'animal_descricao': s.animal.descricao if s.animal else None,
        'animal_status': s.animal.status if s.animal else None,
        'solicitante_id': s.solicitante_id,
        'solicitante_nome': s.solicitante.nome if s.solicitante else None,
        'solicitante_email': s.solicitante.email if s.solicitante else None,
        'solicitante_telefone': s.solicitante.telefone if s.solicitante else None,
        'animal_foto': s.animal.foto if s.animal else None,
        
        'doador_id': s.animal.usuario_id if s.animal else None,
        'doador_nome': s.animal.usuario.nome if (s.animal and s.animal.usuario) else None,
        'doador_email': s.animal.usuario.email if (s.animal and s.animal.usuario) else None,
        'doador_telefone': s.animal.usuario.telefone if (s.animal and s.animal.usuario) else None,
        'tem_espaco': s.tem_espaco,
        'tem_tempo': s.tem_tempo,
        'tem_condicoes': s.tem_condicoes,
        'status': s.status,
        'mensagem': s.mensagem,
        'criado_em': s.data_criacao.isoformat() if s.data_criacao else None
    }


@bp_perfil.route('/', methods=['GET'])
@jwt_required
def ver():
    usuario_id = request.usuario_logado['id']
    usuario = usuario_repository.buscar_por_id(usuario_id)

    meus_animais = animal_repository.listar_por_dono(usuario_id)
    minhas_solicitacoes = solicitacao_repository.listar_minhas_solicitacoes(usuario_id)
    pendentes_para_mim = solicitacao_repository.listar_pendentes_do_dono(usuario_id)
    aprovadas_para_mim = solicitacao_repository.listar_aprovadas_do_dono(usuario_id)

    adotantes_por_animal = {
        s.animal_id: s.solicitante
        for s in aprovadas_para_mim
    }

    historico = [s for s in minhas_solicitacoes if s.status == 'aprovada']

    return jsonify({
        'usuario': {
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email,
            'telefone': usuario.telefone,
            'foto': usuario.foto
        },
        'meus_animais': [
            animal_para_dict(a, adotantes_por_animal.get(a.id))
            for a in meus_animais
        ],
        'minhas_solicitacoes': [solicitacao_para_dict(s) for s in minhas_solicitacoes],
        'pendentes_para_mim': [solicitacao_para_dict(s) for s in pendentes_para_mim],
        'historico_adocoes': [solicitacao_para_dict(s) for s in historico]
    }), 200


@bp_perfil.route('/notificacoes', methods=['GET'])
@jwt_required
def notificacoes():
    
    usuario_id = request.usuario_logado['id']
    notifs = solicitacao_repository.listar_notificacoes(usuario_id)
    return jsonify({
        'notificacoes': [
            {
                'id': s.id,
                'animal_nome': s.animal.nome if s.animal else None,
                'animal_especie': s.animal.especie if s.animal else None,
                'status': s.status
            }
            for s in notifs
        ]
    }), 200


@bp_perfil.route('/notificacoes/marcar-vistas', methods=['POST'])
@jwt_required
def marcar_vistas():
    usuario_id = request.usuario_logado['id']
    solicitacao_repository.marcar_notificacoes_vistas(usuario_id)
    return jsonify({'mensagem': 'Notificações marcadas como vistas'}), 200


@bp_perfil.route('/editar', methods=['PUT'])
@jwt_required
def editar():
    dados = request.get_json()
    usuario_id = request.usuario_logado['id']

    ok = usuario_repository.atualizar(
        usuario_id,
        dados.get('nome'),
        dados.get('email'),
        dados.get('telefone')
    )
    if not ok:
        return jsonify({'erro': 'Não foi possível atualizar. O e-mail pode estar em uso.'}), 400

    nova_senha = dados.get('nova_senha')
    confirmar_senha = dados.get('confirmar_senha')
    if nova_senha:
        if nova_senha != confirmar_senha:
            return jsonify({'erro': 'As senhas não coincidem.'}), 400
        usuario_repository.atualizar_senha(usuario_id, nova_senha)

    usuario = usuario_repository.buscar_por_id(usuario_id)
    return jsonify({
        'mensagem': 'Dados atualizados com sucesso!',
        'usuario': {
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email,
            'telefone': usuario.telefone,
            'foto': usuario.foto
        }
    }), 200


@bp_perfil.route('/foto', methods=['PUT'])
@jwt_required
def atualizar_foto():
    dados = request.get_json()
    usuario_id = request.usuario_logado['id']
    foto = dados.get('foto')  

    ok = usuario_repository.atualizar_foto(usuario_id, foto)
    if ok:
        return jsonify({'mensagem': 'Foto atualizada!', 'foto': foto}), 200
    return jsonify({'erro': 'Erro ao atualizar foto'}), 500


@bp_perfil.route('/animal/editar/<int:id>', methods=['PUT'])
@jwt_required
def editar_animal(id):
    dados = request.get_json()
    usuario_id = request.usuario_logado['id']

    animal = animal_repository.buscar_por_id(id)
    if not animal or animal.usuario_id != usuario_id:
        return jsonify({'erro': 'Sem permissão'}), 403

    ok = animal_repository.atualizar(
        id=id,
        nome=dados.get('nome'),
        especie=dados.get('especie'),
        raca=dados.get('raca'),
        idade=dados.get('idade'),
        descricao=dados.get('descricao')
    )
    if ok:
        return jsonify({'mensagem': 'Animal atualizado com sucesso!'}), 200
    return jsonify({'erro': 'Erro ao atualizar animal.'}), 500


@bp_perfil.route('/animal/excluir/<int:id>', methods=['DELETE'])
@jwt_required
def excluir_animal(id):
    usuario_id = request.usuario_logado['id']
    animal = animal_repository.buscar_por_id(id)

    if not animal or animal.usuario_id != usuario_id:
        return jsonify({'erro': 'Sem permissão'}), 403

    animal_repository.deletar(id)
    return jsonify({'mensagem': 'Animal removido.'}), 200


@bp_perfil.route('/solicitacao/aprovar/<int:id>', methods=['POST'])
@jwt_required
def aprovar_solicitacao(id):
    usuario_id = request.usuario_logado['id']
    ok, msg = solicitacao_repository.aprovar(id, usuario_id)
    return jsonify({'mensagem' if ok else 'erro': msg}), (200 if ok else 400)


@bp_perfil.route('/solicitacao/recusar/<int:id>', methods=['POST'])
@jwt_required
def recusar_solicitacao(id):
    usuario_id = request.usuario_logado['id']
    ok, msg = solicitacao_repository.recusar(id, usuario_id)
    return jsonify({'mensagem' if ok else 'erro': msg}), (200 if ok else 400)