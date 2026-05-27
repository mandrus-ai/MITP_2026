# Данные магазина
SKINS = {
    0: {"id": 0, "name": "Единорог", "price": 0, "file": "unic.png", "owned": True, "type": "skin"},
    1: {"id": 1, "name": "Единорог 2", "price": 100, "file": "unic2.png", "owned": False, "type": "skin"},
    2: {"id": 2, "name": "Единорог 3", "price": 250, "file": "unic3.png", "owned": False, "type": "skin"},
}

BACKGROUNDS = {
    100: {"id": 100, "name": "Розовый фон", "price": 0, "file": "fone.jpg", "owned": True, "type": "bg"},
    101: {"id": 101, "name": "Фон 2", "price": 50, "file": "fone2.jpg", "owned": False, "type": "bg"},
    102: {"id": 102, "name": "Фон 3", "price": 100, "file": "fone3.jpg", "owned": False, "type": "bg"},
}

def get_skin_by_id(skin_id):
    return SKINS.get(skin_id)

def get_background_by_id(bg_id):
    return BACKGROUNDS.get(bg_id)

def get_all_skins():
    return list(SKINS.values())

def get_all_backgrounds():
    return list(BACKGROUNDS.values())