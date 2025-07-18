from flask import Flask, render_template_string, request, redirect, flash
from instagrapi import Client
import time
import random
import os
import json

app = Flask(__name__)
app.secret_key = 'INSTABOT123'

form_html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Seguir seguidores de uma conta</title>
</head>
<body>
    <h2>Seguir seguidores de uma conta</h2>
    <form method="post">
        Usuário Instagram: <input type="text" name="usuario" required><br>
        Senha Instagram: <input type="password" name="senha" required><br>
        Conta alvo: <input type="text" name="conta_alvo" required><br>
        <input type="submit" value="Seguir seguidores">
    </form>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul>
        {% for message in messages %}
          <li>{{ message }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
</body>
</html>
'''

def caminho_sessao(usuario):
    return f'sessao_{usuario}.json'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')
        conta_alvo = request.form.get('conta_alvo')

        try:
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
            logado = False

            # Tenta reutilizar sessão salva
            if os.path.exists(caminho):
                with open(caminho, 'r') as f:
                    settings = json.load(f)
                    cl.set_settings(settings)
                try:
                    cl.get_timeline_feed()
                    logado = True
                    print(f"Sessão reutilizada para @{usuario}")
                except Exception as e:
                    print(f"Sessão inválida, novo login necessário: {e}")

            if not logado:
                cl.login(usuario, senha)
                with open(caminho, 'w') as f:
                    json.dump(cl.get_settings(), f)
                print(f"Login feito e sessão salva para @{usuario}")

            alvo_id = cl.user_id_from_username(conta_alvo)
            seguidores = cl.user_followers(alvo_id, amount=20)

            seguido_count = 0
            limite_seguir = 20

            for seguidor_id, seguidor_info in seguidores.items():
                if seguido_count >= limite_seguir:
                    break
                try:
                    medias = cl.user_medias(seguidor_id, amount=1)
                    if medias:
                        cl.media_like(medias[0].id)
                        print(f"Curtiu o post de @{seguidor_info.username}")

                    cl.user_follow(seguidor_id)
                    seguido_count += 1
                    print(f"Seguiu @{seguidor_info.username}")

                    delay = random.randint(60, 180)
                    print(f"Aguardando {delay} segundos...")
                    time.sleep(delay)
                except Exception as e:
                    print(f"Erro ao seguir @{seguidor_info.username}: {e}")

            flash(f'Total seguido: {seguido_count}')
        except Exception as e:
            flash(f'Erro: {str(e)}')

        return redirect('/')

    return render_template_string(form_html)

if __name__ == '__main__':
    app.run(debug=True)