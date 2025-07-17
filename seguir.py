from instagrapi import Client
import time
import random

usuario = "SEU_USUARIO"
senha = "SUA_SENHA"
conta_alvo = "usuario_alvo"  # Conta cujos seguidores você quer seguir

cl = Client()
cl.login(usuario, senha)

# Obtém o ID da conta alvo
alvo_id = cl.user_id_from_username(conta_alvo)

# Obtém lista de seguidores (limite de 20 por execução)
seguidores = cl.user_followers(alvo_id, amount=150)

seguido_count = 0
limite_seguir = 10  # Limite de ações por execução

for seguidor_id, seguidor_info in seguidores.items():
    if seguido_count >= limite_seguir:
        break
    try:
        cl.user_follow(seguidor_id)
        print(f"Seguiu @{seguidor_info.username}")
        seguido_count += 1
        delay = random.randint(60, 120, 87, 93, 105, 110, 100, 68, 75, 80)
        print(f"Aguardando {delay} segundos...")
        time.sleep(delay)
    except Exception as e:
        print(f"Erro ao seguir @{seguidor_info.username}: {e}")

print(f"Total seguido: {seguido_count}")