from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector, os


app = Flask(__name__)

app.secret_key = os.urandom(24)

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'C4rb0n3r1$',
    'database': 'agrocontrole',
    'port': 3307
}

def verificar_login(username, password):
    try:
        # Conectar ao banco de dados
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Consultar o banco para verificar o usuário e a senha
        query = "SELECT * FROM pessoa WHERE nome = %s AND senha = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()  # Retorna a primeira linha (ou None se não encontrado)
        
        return user  # Retorna o usuário se encontrado, caso contrário retorna None
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route("/")
def index():
    return render_template('index.html')
@app.route('/registro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Capturar os dados do formulário
        nome = request.form['nome']
        sobrenome = request.form['sobrenome']
        cpf = request.form['CPF']
        email = request.form['email']
        senha = request.form['senha']
        data_nascimento = request.form['data_nascimento']
        
        # Conectar ao banco de dados e inserir os dados
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            
            # Inserir no banco de dados
            query = """
                INSERT INTO pessoa (nome, CPF, email, senha, data_nascimento, sobrenome)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (nome, cpf, email, senha, data_nascimento, sobrenome))
            connection.commit()
            
            return f"Usuário {nome} registrado com sucesso!"
        except mysql.connector.Error as err:
            return f"Erro ao registrar o usuário: {err}"
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Captura os dados do formulário
        username = request.form['nome']
        password = request.form['senha']
        
        # Verifica se o login é válido
        user = verificar_login(username, password)
        
        if user:
            return redirect(url_for('index'))  # Login bem-sucedido
        else:
            flash('Usuário ou senha inválidos', 'danger')  # Mensagem de erro
    
    return render_template('login.html')



if __name__ == '__main__':
    app.run(debug=True)
