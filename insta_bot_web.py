from flask import Flask, render_template, request, redirect, flash
from instagrapi import Client
import time
import os
import json
import random

app = Flask(__name__)
app.secret_key = 'INSTABOT123'

# Função que retorna o caminho do arquivo de sessão baseado no nome do usuário
def caminho_sessao(usuario):
    return f'settings_{usuario}.json'

# Cria e retorna um cliente instagrapi com simulação de iPhone 11
def criar_cliente(usuario):
    cl = Client()

    cl.set_device({
        "app_version": "259.0.0.17.109",
        "android_version": 14,
        "android_release": "14.0",
        "dpi": "460dpi",
        "resolution": "828x1792",
        "manufacturer": "Apple",
        "device": "iPhone12,1",
        "model": "iPhone 11",
        "cpu": "Apple A13"
    })

    caminho = caminho_sessao(usuario)

    # Se existir sessão salva, tenta reutilizar
    if os.path.exists(caminho):
        with open(caminho, 'r') as f:
            settings = json.load(f)
            cl.set_settings(settings)

        try:
            cl.get_timeline_feed()
            print(f"Sessão reutilizada para @{usuario}")
            return cl, False  # False = não precisou logar de novo
        except Exception as e:
            print(f"Sessão inválida para @{usuario}, novo login necessário: {e}")

    return cl, True  # True = precisará logar

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        mensagem = request.form.get('mensagem')

        mensagens_variadas = [
            mensagem,
            f"Olá @{usuario}, obrigado pelo comentário!",
            "Agradecemos sua participação!",
            "Ficamos felizes com seu comentário!",
            "Valeu por comentar!"
        ]

        try:
            cl, precisa_logar = criar_cliente(usuario)

            if precisa_logar:
                cl.login(usuario, senha)
                print(f"Login feito com sucesso para @{usuario}")

                with open(caminho_sessao(usuario), 'w') as f:
                    json.dump(cl.get_settings(), f)

            meu_id = cl.user_id_from_username(usuario)
            posts = cl.user_medias(meu_id, amount=3)

            enviados = set()
            enviados_count = 0
            limite_envios = 20

            for post in posts:
                print(f"Analisando post: {post.id}")
                comentarios = cl.media_comments(post.id)
                print(f"Total de comentários: {len(comentarios)}")
                for comentario in comentarios:
                    nome = comentario.user.username
                    print(f"Comentário de: @{nome}")
                    if nome != usuario and nome not in enviados and enviados_count < limite_envios:
                        try:
                            uid = cl.user_id_from_username(nome)
                            mensagem_aleatoria = random.choice(mensagens_variadas)
                            print(f"Enviando mensagem para @{nome} (ID: {uid})")
                            cl.direct_send(mensagem_aleatoria, [uid])
                            enviados.add(nome)
                            enviados_count += 1

                            # Responde publicamente ao comentário
                            try:
                                cl.comment_reply(post.id, comentario.id, mensagem_aleatoria)
                                print(f"Comentário respondido publicamente para @{nome}")
                            except Exception as e:
                                print(f"Erro ao responder comentário público de @{nome}: {e}")

                            delay = random.randint(60, 120)
                            print(f"Aguardando {delay} segundos antes do próximo envio...")
                            time.sleep(delay)
                        except Exception as e:
                            print(f"Erro com @{nome}: {e}")

            flash(f'Mensagens enviadas com sucesso! Total: {enviados_count}')

        except Exception as e:
            print(f"Erro geral: {e}")
            flash(f'Erro ao fazer login ou enviar mensagens: {str(e)}')

        return redirect('/')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
