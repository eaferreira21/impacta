from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# Configurar a conexão com o banco de dados MySQL
db = mysql.connector.connect(
    host="localhost",
    user="usuario_estoque",
    password="Mara250184.#",
    database="estoque"
)
cursor = db.cursor()

@app.route('/')
def menu_principal():
    return render_template('menu.html')


#@app.route('/')
#def index():
#    # Consultar todos os produtos no banco de dados
#    cursor.execute("SELECT * FROM produtos")
#    produtos = cursor.fetchall()
#    cursor.fetchall()  # Lê todos os resultados e descarta-os
#    return render_template('index.html', produtos=produtos)

@app.route('/cadastro_produto', methods=['GET', 'POST'])
def cadastro_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        data_entrada = datetime.now().strftime("%Y-%m-%d")  # Captura a data atual

        # Inserir o novo produto no banco de dados
        sql = "INSERT INTO produtos (nome, quantidade, data_entrada) VALUES (%s, %s, %s)"
        val = (nome, quantidade, data_entrada)
        cursor.execute(sql, val)
        db.commit()

        return redirect(url_for('index'))
    return render_template('cadastro_produto.html')

@app.route('/entrada_produto', methods=['GET', 'POST'])
def entrada_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        data_entrada = datetime.now().strftime("%Y-%m-%d")  # Captura a data atual

        # Verifica se o produto já existe no banco de dados
        cursor.execute("SELECT * FROM produtos WHERE nome = %s", (nome,))
        produto_existente = cursor.fetchone()

        if produto_existente:
            # Atualiza a quantidade do produto existente
            nova_quantidade = produto_existente[2] + int(quantidade)
            sql = "UPDATE produtos SET quantidade = %s, data_entrada = %s WHERE id = %s"
            val = (nova_quantidade, data_entrada, produto_existente[0])
            cursor.execute(sql, val)
        else:
            # Insere o novo produto no banco de dados
            sql = "INSERT INTO produtos (nome, quantidade, data_entrada) VALUES (%s, %s, %s)"
            val = (nome, quantidade, data_entrada)
            cursor.execute(sql, val)

        db.commit()

        # Lê ou descarta os resultados para evitar o erro de "Unread result found"
        cursor.fetchall()

        return redirect(url_for('menu_principal'))
    return render_template('entrada_produto.html')


@app.route('/saida_produto', methods=['GET', 'POST'])
def saida_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        data_saida = datetime.now().strftime("%Y-%m-%d")  # Captura a data atual

        # Atualizar a quantidade do produto no banco de dados
        sql = "UPDATE produtos SET quantidade = quantidade - %s, data_saida = %s WHERE nome = %s"
        val = (quantidade, data_saida, nome)
        cursor.execute(sql, val)
        db.commit()

        return redirect(url_for('menu_principal'))
    return render_template('saida_produto.html')

def relatorio():
    # Consultar todos os produtos no banco de dados
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()
    cursor.fetchall()  # Lê todos os resultados e descarta-os
    return render_template('relatorio.html', produtos=produtos)

@app.route('/Inserir Produto no Estoque', methods=['GET', 'POST'])
def adicionar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        data_entrada = datetime.now().strftime("%Y-%m-%d")  # Captura a data atual

        # Inserir o novo produto no banco de dados
        sql = "INSERT INTO produtos (nome, quantidade, data_entrada) VALUES (%s, %s, %s)"
        val = (nome, quantidade, data_entrada)
        cursor.execute(sql, val)
        db.commit()

        return redirect(url_for('index'))
    return render_template('Inserir Produto no Estoque')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
