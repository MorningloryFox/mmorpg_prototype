import json
import pygame

# Load emoticon definitions mapping chat codes to image paths
with open('emoticons.json', 'r') as f:
    EMOTICON_DEFS = json.load(f)


def save_emoticons():
    """Persist current emoticon definitions to disk."""
    with open('emoticons.json', 'w') as f:
        json.dump(EMOTICON_DEFS, f, indent=2)


def load_surfaces():
    """Return a dict mapping codes to loaded pygame surfaces."""
    surfaces = {}
    for code, path in EMOTICON_DEFS.items():
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, (16, 16))
            surfaces[code] = img
        except Exception:
            continue
    return surfaces
