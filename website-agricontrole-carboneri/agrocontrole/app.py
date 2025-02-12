from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
import mysql.connector, os, random


app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'agricontroleutfpr@gmail.com'  # Seu e-mail
app.config['MAIL_PASSWORD'] = 'eeck igkq hylb geoe'  # Senha de aplicativo gerada no Google
app.config['MAIL_DEFAULT_SENDER'] = 'agricontroleutfpr@gmail.com'

mail = Mail(app)

def enviar_codigo_verificacao(email):
    codigo = str(random.randint(100000, 999999))  # Gera um código de 6 dígitos
    session['codigo_verificacao'] = codigo  # Armazena na sessão
    session['email_verificacao'] = email

    msg = Message('Código de Verificação', recipients=[email])
    msg.body = f'Seu código de verificação é: {codigo}'
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False

db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'utfprsh',
    'database': 'agrocontrole',
    'port': 3306
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
        session['registro_dados'] = {
            'nome': request.form['nome'],
            'sobrenome': request.form['sobrenome'],
            'email': request.form['email'],
            'senha': request.form['senha'],
        }
        
        email = session['registro_dados']['email']
        
        if enviar_codigo_verificacao(email):
            flash('Código de verificação enviado para seu e-mail!', 'success')
            return redirect(url_for('verificar_email'))
        else:
            flash('Erro ao enviar código. Tente novamente.', 'danger')
    
    return render_template('registro.html')

@app.route('/verificar', methods=['GET', 'POST'])
def verificar_email():
    if request.method == 'POST':
        codigo_digitado = request.form['codigo']
        if codigo_digitado == session.get('codigo_verificacao'):
            flash('E-mail verificado com sucesso!', 'success')
            if 'registro_dados' in session:
                dados = session.pop('registro_dados')

                try:
                    connection = mysql.connector.connect(**db_config)
                    cursor = connection.cursor()

                    # Inserir no banco de dados
                    query = """
                        INSERT INTO pessoa (nome, sobrenome, email, senha)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(query, (dados['nome'], dados['sobrenome'], dados['email'], dados['senha']))
                    connection.commit()
                    
                    flash("Usuário registrado com sucesso!", "success")
                    return redirect(url_for('index'))  # Redirecionar para dashboard após login
                except mysql.connector.Error as err:
                    flash(f"Erro ao registrar o usuário: {err}", "danger")
                finally:
                    if connection.is_connected():
                        cursor.close()
                        connection.close()

        else:
            flash('Código inválido. Tente novamente.', 'danger')

    return render_template('verificar.html')

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
