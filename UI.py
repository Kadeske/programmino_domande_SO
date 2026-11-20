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
larghezza_max_contenuto = 980   # larghezza massima della colonna centrale

dati_pagina = {}
dati_img = {}
dati_testo = {}

# ---------------- TEMI ---------------- #

TEMI = {
    "chiaro": {
        "sfondo": "#eef1f6",
        "card": "#ffffff",
        "bordo": "#dde2ea",
        "hover": "#f3f5fa",
        "testo": "#1f2937",
        "testo_secondario": "#6b7280",
        "primario": "#4f46e5",
        "primario_hover": "#4338ca",
        "testo_primario": "#ffffff",
        "secondario": "#e5e8ef",
        "secondario_hover": "#d6dbe5",
        "successo": "#16a34a",
        "successo_bg": "#dcfce7",
        "errore": "#dc2626",
        "errore_bg": "#fee2e2",
        "progresso_bg": "#dde2ea",
        "input_bg": "#ffffff",
    },
    "scuro": {
        "sfondo": "#111827",
        "card": "#1f2937",
        "bordo": "#374151",
        "hover": "#273244",
        "testo": "#f3f4f6",
        "testo_secondario": "#9ca3af",
        "primario": "#6366f1",
        "primario_hover": "#818cf8",
        "testo_primario": "#ffffff",
        "secondario": "#374151",
        "secondario_hover": "#4b5563",
        "successo": "#4ade80",
        "successo_bg": "#14532d",
        "errore": "#f87171",
        "errore_bg": "#7f1d1d",
        "progresso_bg": "#374151",
        "input_bg": "#111827",
    },
}

nome_tema = "chiaro"
C = dict(TEMI[nome_tema])   # colori del tema attivo


def init_settings_UI():
    global dati_pagina, dati_img, dati_testo

    dati = utils.get_settings(sec_principale) or {}

    dati_pagina = dati.get(sec_pagina, {})
    dati_img = dati.get(sec_img, {})
    dati_testo = dati.get(sec_testo, {})

    # valori di default se mancano nel settings.json
    dati_img.setdefault("larghezza", 800)
    dati_img.setdefault("altezza", 600)
    dati_img.setdefault("incremento_dimensione", 100)
    dati_testo.setdefault("font_titoli", "Arial")
    dati_testo.setdefault("font_testo", "Arial")
    dati_testo.setdefault("dimensione_base", 14)
    dati_testo.setdefault("diff_titoli", 2)
    dati_testo.setdefault("diff_info", 4)
    dati_testo.setdefault("diff_sett", 6)

    imposta_tema(dati_pagina.get("tema", "chiaro"))


def imposta_tema(nome):
    global nome_tema
    if nome not in TEMI:
        nome = "chiaro"
    nome_tema = nome
    C.clear()
    C.update(TEMI[nome])


def cambia_tema():
    imposta_tema("scuro" if nome_tema == "chiaro" else "chiaro")


# ---------------- FONT ---------------- #

def _dim(delta=0):
    return max(6, dati_testo["dimensione_base"] + delta)


def font_titolo(delta=0):
    return (dati_testo["font_titoli"], _dim(dati_testo["diff_titoli"] + delta), "bold")


def font_testo(delta=0, stile=""):
    if stile:
        return (dati_testo["font_testo"], _dim(delta), stile)
    return (dati_testo["font_testo"], _dim(delta))


def font_info(stile=""):
    return font_testo(-dati_testo["diff_info"], stile)


def font_piccolo(stile="bold"):
    return font_testo(-dati_testo["diff_sett"], stile)


# ---------------- WIDGET ---------------- #

def pulisci_finestra(finestra):
    for widget in finestra.winfo_children():
        widget.destroy()


def bottone(contenitore, testo, comando, stile="primario", font=None, padx=18, pady=8):
    """Bottone piatto con effetto hover. stile: primario, secondario, successo, errore"""
    colori = {
        "primario": (C["primario"], C["primario_hover"], C["testo_primario"]),
        "secondario": (C["secondario"], C["secondario_hover"], C["testo"]),
        "successo": (C["successo"], C["successo"], C["testo_primario"]),
        "errore": (C["errore"], C["errore"], C["testo_primario"]),
    }
    bg, bg_hover, fg = colori.get(stile, colori["primario"])

    btn = tk.Label(
        contenitore, text=testo, bg=bg, fg=fg,
        font=font or font_testo(0, "bold"),
        padx=padx, pady=pady, cursor="hand2",
    )
    btn._abilitato = True

    def on_enter(_):
        if btn._abilitato:
            btn.config(bg=bg_hover)

    def on_leave(_):
        if btn._abilitato:
            btn.config(bg=bg)

    def on_click(_):
        if btn._abilitato and comando:
            comando()

    def set_abilitato(stato):
        btn._abilitato = stato
        if stato:
            btn.config(bg=bg, fg=fg, cursor="hand2")
        else:
            btn.config(bg=C["secondario"], fg=C["testo_secondario"], cursor="arrow")

    btn.set_abilitato = set_abilitato
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    btn.bind("<ButtonRelease-1>", on_click)
    return btn


def card(contenitore, padx=24, pady=20):
    """Pannello bianco (o scuro) con bordo sottile. Ritorna (esterno, interno)."""
    esterno = tk.Frame(contenitore, bg=C["bordo"])
    interno = tk.Frame(esterno, bg=C["card"], padx=padx, pady=pady)
    interno.pack(fill="both", expand=True, padx=1, pady=1)
    return esterno, interno


def barra_progresso(contenitore, frazione, altezza=6):
    cv = tk.Canvas(contenitore, height=altezza, bg=C["progresso_bg"], highlightthickness=0, bd=0)

    def ridisegna(_=None):
        cv.delete("all")
        w = cv.winfo_width()
        cv.create_rectangle(0, 0, int(w * max(0.0, min(1.0, frazione))), altezza,
                            fill=C["primario"], width=0)

    cv.bind("<Configure>", ridisegna)
    return cv


class Opzione(tk.Frame):
    """Riga cliccabile per una risposta (checkbox o radio disegnati a mano)."""

    def __init__(self, contenitore, testo, variabile, valore=None, multipla=True, comando=None, nota=None):
        super().__init__(contenitore, bg=C["bordo"], cursor="hand2")
        self.testo = testo
        self.var = variabile
        self.valore = valore
        self.multipla = multipla
        self.comando = comando
        self.bloccata = False
        self.stato = None   # None, "corretta", "errata", "mancata"

        self.interno = tk.Frame(self, bg=C["card"], padx=14, pady=10)
        self.interno.pack(fill="both", expand=True, padx=1, pady=1)

        self.indicatore = tk.Label(self.interno, bg=C["card"], fg=C["testo_secondario"],
                                   font=font_testo(2), width=2)
        self.indicatore.pack(side="left", anchor="n")

        self.etichetta = tk.Label(self.interno, text=testo, bg=C["card"], fg=C["testo"],
                                  font=font_testo(), justify="left", anchor="w")
        self.etichetta.pack(side="left", fill="x", expand=True, padx=(8, 0))

        self.esito = tk.Label(self.interno, bg=C["card"], font=font_testo(0, "bold"))
        self.esito.pack(side="right", anchor="n", padx=(8, 0))

        widgets = [self, self.interno, self.indicatore, self.etichetta, self.esito]
        self.nota = None
        if nota:
            self.nota = tk.Label(self.interno, text=nota, bg=C["card"], fg=C["testo_secondario"],
                                 font=font_info())
            self.nota.pack(side="right", padx=(8, 0))
            widgets.append(self.nota)

        for w in widgets:
            w.bind("<ButtonRelease-1>", self._click)
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)

        self.var.trace_add("write", lambda *_: self.aggiorna())
        self.aggiorna()

    def selezionata(self):
        if self.multipla:
            return bool(self.var.get())
        return self.var.get() == self.valore

    def _click(self, _):
        if self.bloccata:
            return
        if self.multipla:
            self.var.set(not self.var.get())
        else:
            self.var.set(self.valore)
        if self.comando:
            self.comando()

    def _enter(self, _):
        if not self.bloccata and self.stato is None:
            self._sfondo(C["hover"])

    def _leave(self, _):
        if self.stato is None:
            self._sfondo(C["card"])

    def _sfondo(self, colore):
        for w in (self.interno, self.indicatore, self.etichetta, self.esito, self.nota):
            if w is not None:
                w.config(bg=colore)

    def set_wrap(self, larghezza):
        self.etichetta.config(wraplength=max(150, larghezza))

    def segna(self, stato):
        """stato: 'corretta', 'errata', 'mancata' (corretta ma non selezionata) o None"""
        self.stato = stato
        self.bloccata = stato is not None
        self.config(cursor="arrow" if self.bloccata else "hand2")
        self.aggiorna()

    def aggiorna(self):
        sel = self.selezionata()
        if self.multipla:
            simbolo = "☑" if sel else "☐"
        else:
            simbolo = "◉" if sel else "○"

        bordo = C["primario"] if sel else C["bordo"]
        sfondo = C["card"]
        colore_ind = C["primario"] if sel else C["testo_secondario"]
        esito = ""
        colore_esito = C["testo"]

        if self.stato == "corretta":
            bordo, sfondo, colore_ind = C["successo"], C["successo_bg"], C["successo"]
            esito, colore_esito = "✓", C["successo"]
        elif self.stato == "mancata":
            bordo, sfondo, colore_ind = C["successo"], C["successo_bg"], C["successo"]
            esito, colore_esito = "✓", C["successo"]
        elif self.stato == "errata":
            bordo, sfondo, colore_ind = C["errore"], C["errore_bg"], C["errore"]
            esito, colore_esito = "✗", C["errore"]

        self.config(bg=bordo)
        self._sfondo(sfondo)
        self.indicatore.config(text=simbolo, fg=colore_ind)
        self.esito.config(text=esito, fg=colore_esito)


def crea_widget_immagine(contenitore, percorso_file, larghezza_max=300, altezza_max=200):
    if not os.path.exists(percorso_file):
        print(f"Errore: Immagine '{percorso_file}' non trovata.")
        return tk.Label(contenitore, text="(Immagine mancante)", bg=C["card"],
                        fg=C["testo_secondario"], font=font_info("italic"))

    try:
        img_originale = Image.open(percorso_file)

        # Calcolo Proporzioni
        img_originale.thumbnail((larghezza_max, altezza_max), Image.Resampling.LANCZOS)

        foto_tk = ImageTk.PhotoImage(img_originale)

        lbl_img = tk.Label(contenitore, image=foto_tk, bg=C["card"], bd=0)

        lbl_img.image = foto_tk
        return lbl_img

    except Exception as e:
        print(f"Errore caricamento: {e}")
        return tk.Label(contenitore, text="Errore Immagine", bg=C["card"], fg=C["errore"])


# Rubata da stack overflow (e poi sistemata):
class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.on_resize = None   # funzione(larghezza) chiamata quando cambia la larghezza

        # 1. Canvas e Scrollbar
        # highlightthickness=0 rimuove i bordi brutti
        self.canvas = tk.Canvas(self, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                      relief="flat", bd=0, width=12, elementborderwidth=0)

        # frame interno (Contenuto)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        # scrollbar automatica
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)

        # fix testo tagliato, larghezza automatica
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # collegamento tra canvas e scroll coso
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.applica_tema()

        # Mousewheel (su tutta la finestra)
        self._bind_mouse_scroll()

    def applica_tema(self):
        self.config(bg=C["sfondo"])
        self.canvas.config(bg=C["sfondo"])
        self.scrollable_frame.config(bg=C["sfondo"])
        self.scrollbar.config(bg=C["secondario"], troughcolor=C["sfondo"],
                              activebackground=C["secondario_hover"])

    def _on_frame_configure(self, event):
        """Aggiorna la scrollbar quando il contenuto interno cambia dimensione"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Allarga il frame interno per riempire la larghezza della finestra"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        if self.on_resize:
            self.on_resize(event.width)

    def force_scroll_update(self):
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def torna_in_cima(self):
        self.canvas.yview_moveto(0)

    def _bind_mouse_scroll(self):
        top = self.winfo_toplevel()
        if sys.platform.startswith('linux'):
            top.bind_all("<Button-4>", self._on_mousewheel)
            top.bind_all("<Button-5>", self._on_mousewheel)
        else:
            top.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        # non scrollare se il contenuto sta tutto nella finestra
        if self.canvas.yview() == (0.0, 1.0):
            return
        if sys.platform.startswith('linux'):
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
