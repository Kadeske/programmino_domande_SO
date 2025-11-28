import random
import os
import json

# ---------------VAR GLOBALI-------------------#

# per impostaizoni da json
settings_path = "settings.json"

sec_config = "config"
# -------------------#


config = {}
settings_path_domande_selezionato = ""


# ----------------------------------------------#

def randomizza_lista(list_inp):
    new_list = []
    lista = list_inp.copy()

    while len(lista) > 0:
        rand = random.randrange(len(lista))
        new_list.append(lista.pop(rand))

    return new_list


def elenca_file_json(cartella="./"):
    files_json = []

    try:
        tutti_i_file = os.listdir(cartella)

        for file in tutti_i_file:
            if file.lower().endswith(".json"):
                files_json.append(f"{cartella}{file}")

    except FileNotFoundError:
        print(f"Errore: La cartella '{cartella}' non esiste.")
        return []

    return files_json


def get_settings(section):
    settings = None
    res = None

    try:
        with open(settings_path, 'r', encoding='utf-8') as file:
            settings = json.load(file)
    except FileNotFoundError:
        print("Errore", f"File {settings_path} non trovato!")
    except json.JSONDecodeError:
        print("Errore", f"Il file {settings_path} non è formattato correttamente.")

    try:
        res = settings[section]
    except Exception:
        print(f"Sezione {section} non presente nel file {settings_path}")

    return res


def init_config():
    global config
    config = get_settings(sec_config)
