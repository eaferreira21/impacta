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

# Criar tabela quantidade_produto se não existir
cursor.execute("""
    CREATE TABLE IF NOT EXISTS quantidade_produto (
        id INT AUTO_INCREMENT PRIMARY KEY,
        produto_id INT,
        quantidade INT,
        data_entrada DATE,
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    )
""")

@app.route('/')
def menu_principal():
    return render_template('menu.html')

@app.route('/cadastro_produto', methods=['GET', 'POST'])
def cadastro_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        data_entrada = datetime.now().strftime("%Y-%m-%d")  # Captura a data atual

        # Inserir o novo produto na tabela 'produtos'
        cursor.execute("INSERT INTO produtos (nome) VALUES (%s)", (nome,))
        db.commit()

        return redirect(url_for('menu_principal'))
    return render_template('cadastro_produto.html')



@app.route('/entrada_produto', methods=['GET', 'POST'])
def entrada_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = int(request.form['quantidade'])
        data_entrada = datetime.now().strftime("%Y-%m-%d")

        # Verifica se o produto já existe no banco de dados
        cursor.execute("SELECT id FROM produtos WHERE nome = %s", (nome,))
        produto = cursor.fetchone()

        if produto:
            # Produto existe, verifica se já há uma entrada na tabela quantidade_produto
            cursor.execute("SELECT produto_id FROM quantidade_produto WHERE produto_id = %s", (produto[0],))
            registro = cursor.fetchone()

            if registro:
                # Já há uma entrada para este produto, apenas atualiza a quantidade
                cursor.execute("UPDATE quantidade_produto SET quantidade = quantidade + %s WHERE produto_id = %s",
                               (quantidade, produto[0]))
            else:
                # Insere um novo registro na tabela quantidade_produto
                cursor.execute("INSERT INTO quantidade_produto (produto_id, quantidade, data_entrada) VALUES (%s, %s, %s)",
                               (produto[0], quantidade, data_entrada))
        else:
            # Produto não existe, insere o novo produto na tabela 'produtos' e na tabela 'quantidade_produto'
            cursor.execute("INSERT INTO produtos (nome) VALUES (%s)", (nome,))
            db.commit()
            produto_id = cursor.lastrowid  # Obtém o ID do produto recém-inserido
            # Insere a quantidade e a data de entrada do produto na tabela quantidade_produto
            cursor.execute("INSERT INTO quantidade_produto (produto_id, quantidade, data_entrada) VALUES (%s, %s, %s)",
                           (produto_id, quantidade, data_entrada))

        db.commit()

        return redirect(url_for('menu_principal'))
    return render_template('entrada_produto.html')






@app.route('/saida_produto', methods=['GET', 'POST'])
def saida_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = int(request.form['quantidade'])
        data_saida = datetime.now().strftime("%Y-%m-%d")  # Captura a data atual

        # Verifica se o produto existe no banco de dados
        cursor.execute("SELECT id FROM produtos WHERE nome = %s", (nome,))
        produto = cursor.fetchone()

        if produto:
            # Produto existe, verifica se há quantidade suficiente para a saída
            cursor.execute("SELECT quantidade FROM quantidade_produto WHERE produto_id = %s", (produto[0],))
            quantidade_atual = cursor.fetchone()
            cursor.fetchall()  # Leia e descarte os resultados

            if quantidade_atual and quantidade_atual[0] >= quantidade:
                # Quantidade suficiente, atualiza a quantidade na tabela quantidade_produto
                cursor.execute("UPDATE quantidade_produto SET quantidade = quantidade - %s, data_saida = %s "
                               "WHERE produto_id = %s",
                               (quantidade, data_saida, produto[0]))
                db.commit()
            else:
                return "Quantidade insuficiente para a saída."
        else:
            # Produto não encontrado
            return "Produto não encontrado."

        return redirect(url_for('menu_principal'))
    return render_template('saida_produto.html')




@app.route('/relatorio', methods=['GET', 'POST'])
def relatorio():
    if request.method == 'POST':
        nome = request.form.get('nome')

        if nome:  # Se o nome do produto for fornecido, gere o relatório apenas para esse produto
            cursor.execute("""
                SELECT p.nome, qp.quantidade, qp.data_entrada, qp.data_saida
                FROM produtos p
                LEFT JOIN quantidade_produto qp ON p.id = qp.produto_id
                WHERE p.nome = %s
            """, (nome,))
            produtos = cursor.fetchall()
        else:  # Caso contrário, gere um relatório total de todos os produtos
            cursor.execute("""
                SELECT p.nome, SUM(qp.quantidade) AS total, MIN(qp.data_entrada) AS primeira_entrada, MAX(qp.data_saida) AS ultima_saida
                FROM produtos p
                LEFT JOIN quantidade_produto qp ON p.id = qp.produto_id
                GROUP BY p.nome
            """)
            produtos = cursor.fetchall()

        return render_template('relatorio.html', produtos=produtos)

    # Se não houver dados enviados via POST, renderize o formulário para selecionar o produto
    return render_template('selecionar_produto.html')







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
