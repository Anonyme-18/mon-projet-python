import asyncio
import base64
import os
from pathlib import Path

from rodiumai import RodiumAI


def load_env():
    path = Path('.env')
    if path.exists():
        for line in path.read_text(encoding='utf-8').splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"\''))


async def main():
    load_env()
    key = os.getenv('RODIUMAI_API_KEY')
    if not key:
        raise SystemExit('RODIUMAI_API_KEY est absente du fichier .env.')
    client = RodiumAI(api_key=key, timeout=150, stream_timeout=150)
    models = {
        'chat': os.getenv('RODIUMAI_CHAT_MODEL', 'openai/gpt-4o-mini'),
        'image': os.getenv('RODIUMAI_IMAGE_MODEL'),
        'video': os.getenv('RODIUMAI_VIDEO_MODEL'),
    }
    steps = [chat, image, video]
    index = 0
    while index < 3:
        print(f'\n=== Étape {index + 1} : {("Chat", "Image", "Vidéo")[index]} ===')
        await steps[index](client, models)
        if index == 0:
            choices, prompt = {'r': 0, 's': 1}, 'Rester (r) ou suivant (s) ? '
        elif index == 2:
            choices, prompt = {'b': 1, 'r': 2, 'q': 3}, 'Retour (b), rester (r) ou quitter (q) ? '
        else:
            choices, prompt = {'b': 0, 'r': 1, 's': 2}, 'Retour (b), rester (r) ou suivant (s) ? '
        choice = input(prompt).strip().lower()
        while choice not in choices:
            choice = input('Choix invalide. Réessayez : ').strip().lower()
        index = choices[choice]
    print('Programme terminé.')


async def chat(client, models):
    response = await client.chat([{'role': 'user', 'content': input('Votre question : ')}], model=models['chat'])
    print(response.choices[0].message.content)
    cost = getattr(response, 'cost_rodi', None)
    if cost is None:
        usage = getattr(response, 'usage', None)
        cost = getattr(usage, 'cost_rodi', None) if usage else None
    print(f"Coût : {cost if cost is not None else 'inconnu'} RODI")


async def image(client, models):
    if not models['image']:
        print('Configurez RODIUMAI_IMAGE_MODEL dans .env avec un modèle image du catalogue.')
        return
    response = await client.images(model=models['image'], prompt=input("Décrivez l'image : "), n=1)
    filename = input('Nom du fichier (Entrée = image.png) : ').strip() or 'image.png'
    Path(filename).write_bytes(base64.b64decode(response.data[0].b64_json))
    print(f'Image enregistrée : {filename}')


async def video(client, models):
    if not models['video']:
        print('Configurez RODIUMAI_VIDEO_MODEL dans .env avec un modèle vidéo du catalogue.')
        return
    response = await client.videos(model=models['video'], prompt=input('Décrivez la vidéo courte : '), duration_seconds=4, timeout=150)
    item = response.data[0]
    filename = input('Nom du fichier (Entrée = video.mp4) : ').strip() or 'video.mp4'
    if item.b64_json:
        Path(filename).write_bytes(base64.b64decode(item.b64_json))
    else:
        import httpx
        async with httpx.AsyncClient(timeout=150) as http:
            result = await http.get(item.url)
            result.raise_for_status()
            Path(filename).write_bytes(result.content)
    print(f'Vidéo enregistrée : {filename}')


if __name__ == '__main__':
    asyncio.run(main())
