from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import date

app = Flask(__name__)

# CONEXÃO COM BANCO
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# CRIAR BANCO
def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS entregas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            piloto TEXT NOT NULL,
            acompanhante TEXT NOT NULL,
            ponto_coleta TEXT NOT NULL,
            hora_retirada TEXT,
            hora_finalizacao TEXT,
            data_entrega TEXT,
            valor REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# HOME
@app.route('/')
def index():
    conn = get_db()

    entregas = conn.execute("""
        SELECT * FROM entregas 
        ORDER BY id DESC 
        LIMIT 3
    """).fetchall()

    resumo = conn.execute("""
        SELECT 
            COUNT(*) as total_rotas,
            COALESCE(SUM(valor),0) as total_valor
        FROM entregas
    """).fetchone()

    conn.close()

    return render_template(
        'index.html',
        entregas=entregas,
        total_rotas=resumo['total_rotas'],
        total_valor=resumo['total_valor'],
        date=date
    )

# HISTÓRICO
@app.route('/historico')
def historico():
    conn = get_db()

    entregas = conn.execute("""
        SELECT * FROM entregas 
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template('historico.html', entregas=entregas)

# ADICIONAR ENTREGA
@app.route('/add', methods=['POST'])
def add():
    data = request.form

    # validação
    if data['piloto'] == data['acompanhante']:
        return "Erro: Piloto e acompanhante não podem ser iguais!"

    conn = get_db()

    conn.execute('''
        INSERT INTO entregas (
            piloto, acompanhante, ponto_coleta,
            hora_retirada, hora_finalizacao,
            data_entrega, valor
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['piloto'],
        data['acompanhante'],
        data['ponto'],
        data['retirada'],
        data['finalizacao'],
        data['data_entrega'],
        data['valor']
    ))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# DETALHES
@app.route('/detalhes/<int:id>')
def detalhes(id):
    conn = get_db()

    entrega = conn.execute(
        "SELECT * FROM entregas WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if entrega is None:
        return "Entrega não encontrada"

    return render_template('detalhes.html', entrega=entrega)

# EDITAR ENTREGA
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db()

    if request.method == 'POST':
        data = request.form

        if data['piloto'] == data['acompanhante']:
            return "Erro: Piloto e acompanhante não podem ser iguais!"

        conn.execute('''
            UPDATE entregas SET
                piloto=?,
                acompanhante=?,
                ponto_coleta=?,
                hora_retirada=?,
                hora_finalizacao=?,
                data_entrega=?,
                valor=?
            WHERE id=?
        ''', (
            data['piloto'],
            data['acompanhante'],
            data['ponto'],
            data['retirada'],
            data['finalizacao'],
            data['data_entrega'],
            data['valor'],
            id
        ))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    entrega = conn.execute(
        "SELECT * FROM entregas WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    if entrega is None:
        return "Entrega não encontrada"

    return render_template('editar.html', entrega=entrega)

# DELETAR ENTREGA
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()

    conn.execute(
        "DELETE FROM entregas WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# START
if __name__ == '__main__':
    app.run(debug=True)