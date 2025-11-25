import utils
import tkinter as tk
from PIL import Image, ImageTk
import os


# VAR GLOBALI

# per settings json
sec_principale = "UI"
sec_pagina = "pagina"
sec_img = "immagini"
sec_testo = "testo"
# --------------#


root = None     # finestra principale
margine_finestre = 40   # margine della finestra principale

dati_pagina = {}
dati_img = {}
dati_testo = {}


def init_settings_UI():
    global dati_pagina, dati_img, dati_testo

    dati = utils.get_settings(sec_principale)

    try:
        dati_pagina = dati[sec_pagina]
        dati_img = dati[sec_img]
        dati_testo = dati[sec_testo]
    except Exception:
        print("Settori UI non trovati nelle impostazioni")

    print(dati_pagina)
    print(dati_testo)


def pulisci_finestra(finestra):
    for widget in finestra.winfo_children():
        widget.destroy()


def crea_widget_immagine(contenitore, percorso_file, larghezza_max=300, altezza_max=200):
    if not os.path.exists(percorso_file):
        print(f"Errore: Immagine '{percorso_file}' non trovata.")
        return tk.Label(contenitore, text="(Immagine mancante)", bg="gray")

    try:
        img_originale = Image.open(percorso_file)

        # Calcolo Proporzioni
        img_originale.thumbnail((larghezza_max, altezza_max), Image.Resampling.LANCZOS)

        foto_tk = ImageTk.PhotoImage(img_originale)

        lbl_img = tk.Label(contenitore, image=foto_tk, bg="white")

        lbl_img.image = foto_tk
        return lbl_img

    except Exception as e:
        print(f"Errore caricamento: {e}")
        return tk.Label(contenitore, text="Errore Immagine")


#
