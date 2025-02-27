import sqlite3
import pandas as pd

# Conectar ao banco de dados (ou criar se não existir)
def get_db_connection():
    conn = sqlite3.connect('movies.db')
    conn.row_factory = sqlite3.Row
    return conn

# Criar tabelas no banco de dados
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabela de indicações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS indicacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            genero TEXT NOT NULL,
            filme TEXT
        )
    ''')

    # Tabela de configurações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quantidade_pessoas INTEGER
        )
    ''')

    # Tabela de resultados
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            genero_sorteado TEXT,
            filme_sorteado TEXT
        )
    ''')

    # Tabela de filmes (importada do IMDb)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            tconst TEXT PRIMARY KEY,
            primaryTitle TEXT,
            genres TEXT,
            titleType TEXT,        -- Categoria (filme, série, etc.)
            startYear INTEGER,     -- Ano de lançamento
            endYear INTEGER,       -- Ano de término (para séries)
            runtimeMinutes INTEGER, -- Duração em minutos
            isAdult INTEGER        -- Faixa etária (0 para infantil, 1 para adulto)
        )
    ''')

    conn.commit()
    conn.close()
    print("Banco de dados inicializado com sucesso!")

# Importar dados do IMDb
def importar_dados_imdb():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Carregar o arquivo TSV
    df = pd.read_csv('title.basics.tsv', sep='\t', low_memory=False)

    # Selecionar colunas relevantes
    df = df[['tconst', 'primaryTitle', 'genres', 'titleType', 'startYear', 'endYear', 'runtimeMinutes', 'isAdult']]

    # Salvar no banco de dados
    df.to_sql('movies', conn, if_exists='replace', index=False)
    print("Dados do IMDb importados com sucesso!")

    conn.close()

# Inicializar o banco de dados e importar dados do IMDb
init_db()
importar_dados_imdb()