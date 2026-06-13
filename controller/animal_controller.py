from flask import Blueprint, request, jsonify
from repository.animal_repository import AnimalRepository
from repository.solicitacao_repository import SolicitacaoRepository
from decorators import jwt_required

bp_animal = Blueprint('animal', __name__, url_prefix='/api/animais')

animal_repository = AnimalRepository()
solicitacao_repository = SolicitacaoRepository()

ESPECIES_PERMITIDAS = ["Cão", "Gato", "Coelho", "Pássaro", "Peixe"]

def animal_para_dict(a, solicitacao_do_usuario=None):
    return {
        'id': a.id,
        'nome': a.nome,
        'especie': a.especie,
        'raca': a.raca,
        'idade': a.idade,
        'descricao': a.descricao,
        'foto': a.foto,
        'status': a.status,
        'usuario_id': a.usuario_id,
        'dono_nome': a.usuario.nome if a.usuario else None,
        'minha_solicitacao': solicitacao_do_usuario
    }

@bp_animal.route('/', methods=['GET'])
def listar():
    busca        = request.args.get('q', '').strip().lower()
    filtro_status = request.args.get('status', 'disponivel')
    especie      = request.args.get('especie', '').strip().lower()
    raca         = request.args.get('raca', '').strip().lower()
    idade_min    = request.args.get('idade_min', type=int)
    idade_max    = request.args.get('idade_max', type=int)

    todos = animal_repository.listar_animais()
    animais = [a for a in todos if a.status == filtro_status]

    if busca:
        animais = [a for a in animais
                   if busca in (a.nome or '').lower()
                   or busca in (a.especie or '').lower()]

    if especie:
        animais = [a for a in animais if especie in (a.especie or '').lower()]

    if raca:
        animais = [a for a in animais if raca in (a.raca or '').lower()]

    if idade_min is not None:
        animais = [a for a in animais if a.idade is not None and a.idade >= idade_min]

    if idade_max is not None:
        animais = [a for a in animais if a.idade is not None and a.idade <= idade_max]

    solicitacoes_map = {}
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        import jwt, os
        try:
            payload = jwt.decode(auth_header.split(' ')[1], os.getenv('JWT_SECRET_KEY'), algorithms=['HS256'])
            usuario_id = payload['id']
            minhas = solicitacao_repository.listar_minhas_solicitacoes(usuario_id)
            solicitacoes_map = {s.animal_id: {'id': s.id, 'status': s.status} for s in minhas}
        except Exception:
            pass

    especies = sorted(set(a.especie for a in todos if a.especie))

    qtd_disponiveis = sum(1 for a in todos if a.status == 'disponivel')
    qtd_adotados    = sum(1 for a in todos if a.status == 'adotado')

    return jsonify({
        'animais': [animal_para_dict(a, solicitacoes_map.get(a.id)) for a in animais],
        'qtd_disponiveis': qtd_disponiveis,
        'qtd_adotados': qtd_adotados,
        'especies': especies
    }), 200


@bp_animal.route('/cadastrar', methods=['POST'])
@jwt_required
def cadastrar():
    dados = request.get_json()
    usuario_id = request.usuario_logado['id']

    if dados.get('especie') not in ESPECIES_PERMITIDAS:
        return jsonify({'erro': 'Espécie não permitida'}), 400

    animal = animal_repository.cadastrar(
        nome=dados.get('nome'),
        especie=dados.get('especie'),
        raca=dados.get('raca'),
        idade=dados.get('idade'),
        descricao=dados.get('descricao'),
        foto=dados.get('foto'),
        usuario_id=usuario_id
    )
    if animal:
        return jsonify({'mensagem': 'Animal cadastrado com sucesso!'}), 201
    return jsonify({'erro': 'Erro ao cadastrar animal'}), 500


@bp_animal.route('/<int:id>', methods=['GET'])
def buscar(id):
    animal = animal_repository.buscar_por_id(id)
    if not animal:
        return jsonify({'erro': 'Animal não encontrado'}), 404
    return jsonify(animal_para_dict(animal)), 200


@bp_animal.route('/<int:id>', methods=['PUT'])
@jwt_required
def atualizar(id):
    dados = request.get_json()
    usuario_id = request.usuario_logado['id']

    animal = animal_repository.buscar_por_id(id)
    if not animal:
        return jsonify({'erro': 'Animal não encontrado'}), 404
    if animal.usuario_id != usuario_id:
        return jsonify({'erro': 'Sem permissão para editar este animal'}), 403

    if animal.status == 'adotado':
        return jsonify({'erro': 'Não é possível editar um animal já adotado'}), 400

    if dados.get('especie') and dados.get('especie') not in ESPECIES_PERMITIDAS:
        return jsonify({'erro': 'Espécie não permitida'}), 400

    ok = animal_repository.atualizar(
        id=id,
        nome=dados.get('nome'),
        especie=dados.get('especie'),
        raca=dados.get('raca'),
        idade=dados.get('idade'),
        descricao=dados.get('descricao'),
        foto=dados.get('foto')
    )
    if ok:
        return jsonify({'mensagem': 'Animal atualizado!'}), 200
    return jsonify({'erro': 'Erro ao atualizar'}), 500


@bp_animal.route('/<int:id>', methods=['DELETE'])
@jwt_required
def deletar(id):
    usuario_id = request.usuario_logado['id']
    animal = animal_repository.buscar_por_id(id)

    if not animal:
        return jsonify({'erro': 'Animal não encontrado'}), 404
    if animal.usuario_id != usuario_id:
        return jsonify({'erro': 'Sem permissão para remover este animal'}), 403

    animal_repository.deletar(animal)
    return jsonify({'mensagem': 'Animal removido'}), 200


@bp_animal.route('/<int:id>/solicitar', methods=['POST'])
@jwt_required
def solicitar_adocao(id):
    dados = request.get_json()
    solicitante_id = request.usuario_logado['id']

    animal = animal_repository.buscar_por_id(id)
    if not animal or animal.status != 'disponivel':
        return jsonify({'erro': 'Animal não disponível para adoção'}), 400
    if animal.usuario_id == solicitante_id:
        return jsonify({'erro': 'Você não pode adotar o seu próprio animal'}), 400

    existente = solicitacao_repository.buscar_por_animal_e_solicitante(id, solicitante_id)
    if existente:
        return jsonify({'erro': 'Você já enviou uma solicitação para este animal'}), 400

    ok, msg = solicitacao_repository.criar(
        animal_id=id,
        solicitante_id=solicitante_id,
        tem_espaco=dados.get('tem_espaco', False),
        tem_tempo=dados.get('tem_tempo', False),
        tem_condicoes=dados.get('tem_condicoes', False),
        mensagem=dados.get('mensagem', '')
    )
    return jsonify({'mensagem' if ok else 'erro': msg}), (201 if ok else 400)


@bp_animal.route('/<int:id>/cancelar', methods=['DELETE'])
@jwt_required
def cancelar_solicitacao(id):
    solicitante_id = request.usuario_logado['id']

    solicitacao = solicitacao_repository.buscar_por_animal_e_solicitante(id, solicitante_id)
    if not solicitacao:
        return jsonify({'erro': 'Solicitação não encontrada'}), 404
    if solicitacao.status != 'pendente':
        return jsonify({'erro': 'Só é possível cancelar solicitações pendentes'}), 400

    solicitacao_repository.deletar(solicitacao)
    return jsonify({'mensagem': 'Solicitação cancelada'}), 200