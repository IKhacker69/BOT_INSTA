
from flask import Flask, render_template, request, redirect, flash
from instagrapi import Client
import time

app = Flask(__name__)
app.secret_key = 'INSTABOT123'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        mensagem = request.form.get('mensagem')

        try:
            cl = Client()
            cl.login(usuario, senha)

            meu_id = cl.user_id_from_username(usuario)
            posts = cl.user_medias(meu_id, amount=3)

            enviados = set()
            for post in posts:
                comentarios = cl.media_comments(post.id)
                for comentario in comentarios:
                    nome = comentario.user.username
                    if nome != usuario and nome not in enviados:
                        try:
                            uid = cl.user_id_from_username(nome)
                            cl.direct_send(mensagem, [uid])
                            enviados.add(nome)
                            time.sleep(5)
                        except Exception as e:
                            print(f"Erro com @{nome}: {e}")
            flash('Mensagens enviadas com sucesso!')
        except Exception as e:
            flash(f'Erro ao fazer login ou enviar mensagens: {str(e)}')

        return redirect('/')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
