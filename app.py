import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from datetime import date

app = Flask(__name__)

# CONEXÃO COM POSTGRES
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL)

# CRIAR TABELA
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS entregas (
            id SERIAL PRIMARY KEY,
            piloto TEXT NOT NULL,
            acompanhante TEXT NOT NULL,
            ponto_coleta TEXT NOT NULL,
            hora_retirada TEXT,
            hora_finalizacao TEXT,
            data_entrega TEXT,
            valor NUMERIC
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()

init_db()

# HOME
@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM entregas ORDER BY id DESC LIMIT 3")
    entregas = cur.fetchall()

    cur.execute("SELECT COUNT(*), COALESCE(SUM(valor),0) FROM entregas")
    total_rotas, total_valor = cur.fetchone()

    conn.close()

    return render_template(
        'index.html',
        entregas=entregas,
        total_rotas=total_rotas,
        total_valor=total_valor,
        date=date
    )

# HISTÓRICO
@app.route('/historico')
def historico():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM entregas ORDER BY id DESC")
    entregas = cur.fetchall()

    conn.close()
    return render_template('historico.html', entregas=entregas)

# ADD
@app.route('/add', methods=['POST'])
def add():
    d = request.form

    if d['piloto'] == d['acompanhante']:
        return "Erro: Piloto e acompanhante não podem ser iguais!"

    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO entregas (
            piloto, acompanhante, ponto_coleta,
            hora_retirada, hora_finalizacao,
            data_entrega, valor
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (
        d['piloto'],
        d['acompanhante'],
        d['ponto'],
        d['retirada'],
        d['finalizacao'],
        d['data_entrega'],
        d['valor']
    ))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# DETALHES
@app.route('/detalhes/<int:id>')
def detalhes(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM entregas WHERE id = %s", (id,))
    entrega = cur.fetchone()

    conn.close()

    if not entrega:
        return "Entrega não encontrada"

    return render_template('detalhes.html', entrega=entrega)

# EDITAR
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        d = request.form

        if d['piloto'] == d['acompanhante']:
            return "Erro!"

        cur.execute('''
            UPDATE entregas SET
                piloto=%s,
                acompanhante=%s,
                ponto_coleta=%s,
                hora_retirada=%s,
                hora_finalizacao=%s,
                data_entrega=%s,
                valor=%s
            WHERE id=%s
        ''', (
            d['piloto'],
            d['acompanhante'],
            d['ponto'],
            d['retirada'],
            d['finalizacao'],
            d['data_entrega'],
            d['valor'],
            id
        ))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM entregas WHERE id = %s", (id,))
    entrega = cur.fetchone()

    conn.close()
    return render_template('editar.html', entrega=entrega)

# DELETE
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM entregas WHERE id = %s", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()