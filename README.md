# Exercice 3 - RodiumAI avec le SDK Python

Script interactif utilisant le SDK officiel `rodiumai` pour le chat, la génération d'image et la génération de vidéo.

## Installation

Python 3.9 ou supérieur :

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Copiez `.env.example` vers `.env`, puis renseignez votre clé. Ajoutez aussi les identifiants exacts des modèles image et vidéo disponibles dans votre catalogue : `RODIUMAI_IMAGE_MODEL` et `RODIUMAI_VIDEO_MODEL`.

## Lancement

```bash
python main.py
```
