from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import random
from datetime import datetime
from threading import Thread
import time

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Configurações da API do TMDB
TMDB_API_KEY = '6f215bb8a87193ffde83e5487c0efe00'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

# Variáveis globais
indicacoes = []
resultados = []
votacao_ativa = False
horario_inicio = None
horario_fim = None
quantidade_pessoas = 0

import requests

# Função para buscar filmes por gênero e ordenação
def buscar_filmes_por_genero(genero_id, pagina=1, ordenar_por='popularity', ordem='desc'):
    url = f'{TMDB_BASE_URL}/discover/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'with_genres': genero_id,
        'page': pagina,
        'language': 'pt-BR',
        'sort_by': f'{ordenar_por}.{ordem}',
        'include_adult': False
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Verifica se temos resultados e se há overview
        if 'results' in data:
            for filme in data['results']:
                print(f"Filme: {filme.get('title')} - Overview: {filme.get('overview')}")  # Log para depuração
        # Para obter detalhes completos (incluindo runtime) precisamos de requisições adicionais
        # Mas para sinopse (overview), já vem na resposta básica
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None
    
# Função para buscar gêneros
def buscar_generos():
    url = f'{TMDB_BASE_URL}/genre/movie/list'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'pt-BR'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['genres']
    return []

# Função para verificar se a votação está ativa
def votacao_esta_ativa():
    global votacao_ativa, horario_inicio, horario_fim
    if not votacao_ativa:
        return False
    agora = datetime.now()
    return horario_inicio <= agora <= horario_fim

# Função para encerrar a votação automaticamente
def encerrar_votacao_automaticamente():
    global votacao_ativa, quantidade_pessoas, indicacoes
    while votacao_ativa and datetime.now() < horario_fim and len(indicacoes) < quantidade_pessoas:
        time.sleep(1)  # Verifica a cada segundo
    if votacao_ativa:
        votacao_ativa = False
        flash('Votação encerrada automaticamente.', 'info')
        sortear_genero_ou_filme()

# Função para sortear gênero ou filme
def sortear_genero_ou_filme():
    global resultados, indicacoes
    if not resultados or not resultados[-1].get('genero_sorteado'):
        # Sortear gênero
        generos_indicados = [indicacao['genero'] for indicacao in indicacoes]
        if generos_indicados:
            genero_sorteado = random.choice(generos_indicados)
            resultados.append({'genero_sorteado': genero_sorteado, 'filme_sorteado': None})
            flash(f'Gênero sorteado: {genero_sorteado}', 'success')
    else:
        # Sortear filme
        filmes_indicados = [indicacao['filme'] for indicacao in indicacoes if indicacao['filme']]
        if filmes_indicados:
            filme_sorteado = random.choice(filmes_indicados)
            resultados[-1]['filme_sorteado'] = filme_sorteado
            flash(f'Filme sorteado: {filme_sorteado}', 'success')

# Página inicial
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/sugestoes', methods=['GET', 'POST'])
def sugestoes():
    generos = buscar_generos()
    filmes = []
    total_filmes = 0
    total_paginas = 0

    genero_filtro = request.args.get('genero', '')
<<<<<<< HEAD
    ordenar_por = request.args.get('ordenar_por', 'titulo')
    ordem = request.args.get('ordem', 'asc')
=======
    ordenar_por = request.args.get('ordenar_por', 'release_date')
    ordem = request.args.get('ordem', 'desc')
>>>>>>> e94353f7a6a9c31741c2de28dd03f67241ec7249
    pagina = request.args.get('pagina', 1, type=int)
    pesquisa = request.args.get('pesquisa', '').strip()

    if genero_filtro == '':  # Caso o gênero seja "Todos" (ou vazio)
        genero_filtro = None

<<<<<<< HEAD
            if ordenar_por == 'titulo':
                filmes.sort(key=lambda x: x['title'], reverse=(ordem == 'desc'))
            elif ordenar_por == 'data':
                filmes.sort(key=lambda x: x.get('release_date', ''), reverse=(ordem == 'desc'))
        else:
            total_filmes = 0
            total_paginas = 0
=======
    # Se o gênero for selecionado e não for "Todos" ou se houver pesquisa
    if genero_filtro and pesquisa:
        resultado = buscar_filmes_por_genero(genero_filtro, pagina, ordenar_por, ordem)
        filmes = [filme for filme in resultado.get('results', []) if pesquisa.lower() in filme['title'].lower()]
    elif genero_filtro:
        # Caso haja apenas filtro de gênero
        resultado = buscar_filmes_por_genero(genero_filtro, pagina, ordenar_por, ordem)
        filmes = resultado.get('results', [])
    elif pesquisa:
        # Caso haja apenas pesquisa
        resultado = buscar_filmes_por_nome(pesquisa, pagina)
        filmes = resultado.get('results', [])
>>>>>>> e94353f7a6a9c31741c2de28dd03f67241ec7249
    else:
        # Caso "Todos os filmes" e sem pesquisa
        resultado = buscar_filmes_por_genero('', pagina, ordenar_por, ordem)  # Buscar todos os filmes
        filmes = resultado.get('results', [])

    # Atualização do número total de filmes e páginas
    if resultado:
        total_filmes = resultado.get('total_results', 0)
        total_paginas = resultado.get('total_pages', 0)

    return render_template(
        'sugestoes.html',
        generos=generos,
        filmes=filmes,
        genero_filtro=genero_filtro,
        ordenar_por=ordenar_por,
        ordem=ordem,
        pagina=pagina,
        total_paginas=total_paginas,
        total_filmes=total_filmes,
        pesquisa=pesquisa
    )


# Página de resultados e indicações
@app.route('/resultados', methods=['GET', 'POST'])
def resultados():
    global resultados
    if not isinstance(resultados, list):
        resultados = []
    return render_template('resultados.html', indicacoes=indicacoes, resultado=resultados[-1] if resultados else None)

# Página de indicação de gênero
@app.route('/indicar_genero', methods=['GET', 'POST'])
def indicar_genero():
    global indicacoes
    generos = buscar_generos()
    indicacoes_encerradas = len(indicacoes) >= 10

    if not votacao_esta_ativa():
        flash('A votação não está ativa no momento.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if indicacoes_encerradas:
            flash('As indicações de gênero foram encerradas. O limite foi atingido.', 'error')
        else:
            nome = request.form['nome']
            genero_id = request.form['genero']
            genero_nome = next((g['name'] for g in generos if g['id'] == int(genero_id)), 'Desconhecido')

            if any(indicacao['nome'] == nome for indicacao in indicacoes):
                flash('Você já indicou um gênero.', 'error')
            else:
                indicacoes.append({'nome': nome, 'genero': genero_nome, 'filme': None})
                flash('Indicação enviada com sucesso!', 'success')
                return redirect(url_for('resultados'))

    return render_template(
        'indicar_genero.html',
        generos=generos,
        indicacoes_encerradas=indicacoes_encerradas
    )

# Página de indicação de filme
@app.route('/indicar_filme', methods=['GET', 'POST'])
def indicar_filme():
    global resultados, indicacoes
    if not isinstance(resultados, list):
        resultados = []

    if not resultados or not resultados[-1].get('genero_sorteado'):
        flash('Nenhum gênero foi sorteado ainda.', 'error')
        return redirect(url_for('resultados'))

    if not votacao_esta_ativa():
        flash('A votação não está ativa no momento.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        nome = request.form['nome'].strip()
        filme = request.form['filme'].strip()

        indicacao_existente = next(
            (indicacao for indicacao in indicacoes if indicacao['nome'].strip().lower() == nome.lower()),
            None
        )

        if not indicacao_existente:
            flash('Nenhuma indicação de gênero encontrada para este nome.', 'error')
        else:
            if indicacao_existente['filme']:
                flash('Você já indicou um filme.', 'error')
            else:
                indicacao_existente['filme'] = filme
                flash('Filme enviado com sucesso!', 'success')
                return redirect(url_for('resultados'))

    return render_template('indicar_filme.html')

# Página de administração
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    global resultados, indicacoes, votacao_ativa, horario_inicio, horario_fim, quantidade_pessoas

    if request.method == 'POST':
        if 'definir_horario' in request.form:
            data_inicio = request.form['data_inicio']
            hora_inicio = request.form['hora_inicio']
            data_fim = request.form['data_fim']
            hora_fim = request.form['hora_fim']

            horario_inicio = datetime.strptime(f'{data_inicio} {hora_inicio}', '%Y-%m-%d %H:%M')
            horario_fim = datetime.strptime(f'{data_fim} {hora_fim}', '%Y-%m-%d %H:%M')

            flash('Horário de votação definido com sucesso!', 'success')

        elif 'iniciar_votacao' in request.form:
            if not horario_inicio or not horario_fim:
                flash('Defina o horário de votação antes de iniciar.', 'error')
            else:
                votacao_ativa = True
                flash('Votação iniciada!', 'success')
                Thread(target=encerrar_votacao_automaticamente).start()

        elif 'parar_votacao' in request.form:
            votacao_ativa = False
            flash('Votação parada manualmente.', 'info')

        elif 'definir_quantidade' in request.form:
            quantidade_pessoas = int(request.form['quantidade_pessoas'])
            flash(f'Quantidade de pessoas definida para {quantidade_pessoas}.', 'success')

        elif 'sortear_genero' in request.form:
            generos_indicados = [indicacao['genero'] for indicacao in indicacoes]
            if generos_indicados:
                genero_sorteado = random.choice(generos_indicados)
                resultados.append({'genero_sorteado': genero_sorteado, 'filme_sorteado': None})
                flash(f'Gênero sorteado: {genero_sorteado}', 'success')
            else:
                flash('Nenhum gênero indicado para sorteio.', 'error')

        elif 'sortear_filme' in request.form:
            filmes_indicados = [indicacao['filme'] for indicacao in indicacoes if indicacao['filme']]
            if filmes_indicados:
                filme_sorteado = random.choice(filmes_indicados)
                resultados[-1]['filme_sorteado'] = filme_sorteado
                flash(f'Filme sorteado: {filme_sorteado}', 'success')
            else:
                flash('Nenhum filme indicado para sorteio.', 'error')

        elif 'apagar_indicacao' in request.form:
            indicacao_id = int(request.form['indicacao_id'])
            if 0 <= indicacao_id < len(indicacoes):
                indicacoes.pop(indicacao_id)
                flash('Indicação apagada com sucesso!', 'success')

        elif 'resetar_sistema' in request.form:
            indicacoes.clear()
            resultados.clear()
            votacao_ativa = False
            horario_inicio = None
            horario_fim = None
            quantidade_pessoas = 0
            flash('Sistema resetado com sucesso! Todas as indicações e resultados foram apagados.', 'success')

    return render_template('admin.html', indicacoes=indicacoes, resultado=resultados[-1] if resultados else None)

def buscar_filmes_por_nome(nome, pagina=1):
    url = f'https://api.themoviedb.org/3/search/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'pt-BR',
        'query': nome,
        'page': pagina,
        'include_adult': False
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return None

# Executar a aplicação
if __name__ == '__main__':
    app.run(debug=True)