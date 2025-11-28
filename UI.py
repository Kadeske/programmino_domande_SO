import utils
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

# VAR GLOBALI

# per settings json
sec_principale = "UI"
sec_pagina = "pagina"
sec_img = "immagini"
sec_testo = "testo"
# --------------#


root = None     # finestra principale
margine_finestre = 300   # margine della finestra principale

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


# Rubata da stack overflow:
class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        # 1. Canvas e Scrollbar
        # highlightthickness=0 rimuove i bordi brutti
        self.canvas = tk.Canvas(self, highlightthickness=0, bg="#f0f0f0")
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        # frame interno (Contenuto)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f0f0")

        # anchor="n" -> CENTRA il frame in alto (invece di "nw" che lo mette a sinistra)
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="n"
        )

        # scrollbar automatica
        self.scrollable_frame.bind(
            "<Configure>",
            self._on_frame_configure
        )

        # fix testo tagliato, larghezza automatica
        self.canvas.bind(
            "<Configure>",
            self._on_canvas_configure
        )

        # collegamento tra canvas e scroll coso
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Mousewheel
        self._bind_mouse_scroll()

    def _on_frame_configure(self, event):
        """Aggiorna la scrollbar quando il contenuto interno cambia dimensione"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Allarga il frame interno per riempire la larghezza della finestra"""
        # Questo è il trucco per evitare che il testo venga tagliato
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def force_scroll_update(self):
        """Chiama questa funzione manualmente se la scrollbar si blocca"""
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _bind_mouse_scroll(self):
        self.scrollable_frame.bind('<Enter>', self._bound_to_mousewheel)
        self.scrollable_frame.bind('<Leave>', self._unbound_to_mousewheel)

    def _bound_to_mousewheel(self, event):
        # Binding globale sicuro
        top = self.winfo_toplevel()
        if sys.platform.startswith('linux'):
            top.bind_all("<Button-4>", self._on_mousewheel)
            top.bind_all("<Button-5>", self._on_mousewheel)
        else:
            top.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        top = self.winfo_toplevel()
        if sys.platform.startswith('linux'):
            top.unbind_all("<Button-4>")
            top.unbind_all("<Button-5>")
        else:
            top.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if sys.platform.startswith('linux'):
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
