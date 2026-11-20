import UI
import utils
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import json
import os

# ---------VAR GLOBALI-----------#

lista_domande_caricata = []
lista_domande_fatte = []
punti = 0
campo_check_domanda = "isCompleted"
campo_risposte_domanda = "risposte"
campo_ordine_opzioni = "_ordine_opzioni"

elenco_file = []  # elenco file con domande scelti
randomizza_domande = True
randomizza_ordine_opzioni = True

# tipologie di domande accettate
# singola, multiple, aperta,

root = None
scroll = None       # contenitore scorrevole
app_frame = None    # frame dell'app, è scorrevole

azioni_tastiera = {}    # tasto -> funzione, aggiornato ad ogni schermata
# ------------------------------#


# ---------------- UTILITA' GRAFICHE ---------------- #

def nuova_schermata(max_larghezza=None):
    """Pulisce la finestra e ritorna una colonna centrata in cui mettere i contenuti.
    Ritorna anche una lista in cui registrare funzioni(larghezza) per il wrap del testo."""
    global azioni_tastiera
    azioni_tastiera = {}

    UI.pulisci_finestra(app_frame)
    scroll.applica_tema()
    root.configure(bg=UI.C["sfondo"])

    max_larghezza = max_larghezza or UI.larghezza_max_contenuto
    colonna = tk.Frame(app_frame, bg=UI.C["sfondo"])
    colonna.pack(fill="x", pady=(24, 40))

    callback_wrap = []

    def ridimensiona(_=None):
        w = scroll.canvas.winfo_width()
        margine = max(20, (w - max_larghezza) // 2)
        colonna.pack_configure(padx=margine)
        larghezza_utile = w - 2 * margine
        for f in callback_wrap:
            f(larghezza_utile)

    scroll.on_resize = ridimensiona
    colonna.after_idle(ridimensiona)
    scroll.torna_in_cima()
    return colonna, callback_wrap


def titolo_sezione(contenitore, testo):
    tk.Label(contenitore, text=testo.upper(), bg=UI.C["card"], fg=UI.C["testo_secondario"],
             font=UI.font_piccolo("bold"), anchor="w").pack(fill="x", pady=(0, 10))


def bottone_tema(contenitore, ridisegna):
    def cambia():
        UI.cambia_tema()
        ridisegna()
    testo = "☾  Scuro" if UI.nome_tema == "chiaro" else "☀  Chiaro"
    return UI.bottone(contenitore, testo, cambia, "secondario", UI.font_piccolo(), padx=12, pady=5)


def nome_leggibile(percorso):
    nome = os.path.basename(percorso)
    if nome.lower().endswith(".json"):
        nome = nome[:-5]
    return nome.replace("_", " ")


def conta_domande(percorso):
    try:
        with open(percorso, 'r', encoding='utf-8') as f:
            return len(json.load(f))
    except Exception:
        return None


def gestisci_tasto(event):
    # niente scorciatoie mentre si scrive in un campo di testo
    if isinstance(event.widget, (tk.Entry, tk.Text)) and event.keysym not in ("Return", "KP_Enter"):
        return
    funzione = azioni_tastiera.get(event.keysym)
    if funzione:
        funzione()


# ---------------- SCHERMATA INIZIALE ---------------- #

def genera_schermata_scelta_file():
    global elenco_file
    elenco_file = []

    colonna, callback_wrap = nuova_schermata(760)
    C = UI.C

    # intestazione
    header = tk.Frame(colonna, bg=C["sfondo"])
    header.pack(fill="x", pady=(0, 20))
    bottone_tema(header, genera_schermata_scelta_file).pack(side="right", anchor="n")
    tk.Label(header, text="Quiz", bg=C["sfondo"], fg=C["testo"],
             font=UI.font_titolo(14), anchor="w").pack(fill="x")
    tk.Label(header, text="Scegli i file di domande con cui esercitarti.", bg=C["sfondo"],
             fg=C["testo_secondario"], font=UI.font_testo(), anchor="w").pack(fill="x")

    # --- card file --- #
    esterno, card_file = UI.card(colonna)
    esterno.pack(fill="x", pady=(0, 16))
    titolo_sezione(card_file, "File di domande")
    tk.Label(card_file, text="Puoi sceglierne più di uno: verranno uniti.", bg=C["card"],
             fg=C["testo_secondario"], font=UI.font_info(), anchor="w").pack(fill="x", pady=(0, 10))

    btn_inizia = None
    scelte = []

    def aggiorna_bottone():
        if btn_inizia is not None:
            ok = any(var.get() for var, _ in scelte) or len(elenco_file) > 0
            btn_inizia.set_abilitato(ok)

    for file in sorted(utils.elenca_file_json(utils.config.get("path_domande", "domande/"))):
        var = tk.BooleanVar()
        n = conta_domande(file)
        opz = UI.Opzione(card_file, nome_leggibile(file), var, multipla=True,
                         comando=aggiorna_bottone, nota=f"{n} domande" if n is not None else None)
        opz.pack(fill="x", pady=3)
        callback_wrap.append(lambda w, o=opz: o.set_wrap(w - 260))
        scelte.append((var, file))

    if not scelte:
        tk.Label(card_file, text="Nessun file trovato nella cartella delle domande.",
                 bg=C["card"], fg=C["errore"], font=UI.font_info()).pack(fill="x", pady=6)

    # file esterni
    riga_esterni = tk.Frame(card_file, bg=C["card"])
    riga_esterni.pack(fill="x", pady=(12, 0))
    lbl_esterni = tk.Label(riga_esterni, text="", bg=C["card"], fg=C["testo_secondario"],
                           font=UI.font_info(), anchor="w", justify="left")

    def scegli_file_esterno():
        percorso_file = filedialog.askopenfilename(
            title="Seleziona un file di domande",
            initialdir=os.getcwd(),
            filetypes=[("File JSON", "*.json"), ("Tutti i file", "*.*")]
        )
        if percorso_file and percorso_file not in elenco_file:
            elenco_file.append(percorso_file)
            lbl_esterni.config(text="Esterni: " + ", ".join(os.path.basename(f) for f in elenco_file))
            aggiorna_bottone()

    UI.bottone(riga_esterni, "+  Aggiungi file esterno", scegli_file_esterno, "secondario",
               UI.font_info("bold"), padx=14, pady=6).pack(side="left")
    lbl_esterni.pack(side="left", fill="x", expand=True, padx=12)
    callback_wrap.append(lambda w: lbl_esterni.config(wraplength=max(150, w - 330)))

    # --- card opzioni --- #
    esterno, card_opz = UI.card(colonna)
    esterno.pack(fill="x", pady=(0, 20))
    titolo_sezione(card_opz, "Opzioni")

    var_ordine_domande_random = tk.BooleanVar(value=randomizza_domande)
    var_ordine_opzioni_random = tk.BooleanVar(value=randomizza_ordine_opzioni)
    UI.Opzione(card_opz, "Ordine casuale delle domande", var_ordine_domande_random).pack(fill="x", pady=3)
    UI.Opzione(card_opz, "Ordine casuale delle risposte", var_ordine_opzioni_random).pack(fill="x", pady=3)

    def conferma():
        global randomizza_domande, randomizza_ordine_opzioni

        # aggiorno elenco file scelti
        for var, file in scelte:
            if var.get():
                elenco_file.append(file)

        if not elenco_file:
            return

        # set var globali per l'ordine
        randomizza_domande = var_ordine_domande_random.get()
        randomizza_ordine_opzioni = var_ordine_opzioni_random.get()
        inizio_quiz()

    btn_inizia = UI.bottone(colonna, "Inizia il quiz  →", conferma, "primario",
                            UI.font_testo(2, "bold"), padx=28, pady=12)
    btn_inizia.pack(anchor="e")
    aggiorna_bottone()

    azioni_tastiera["Return"] = lambda: btn_inizia._abilitato and conferma()
    azioni_tastiera["KP_Enter"] = azioni_tastiera["Return"]


# ---------------- TIPOLOGIE DI DOMANDA ---------------- #

def ordina_opzioni(dati):
    """Mischia le opzioni una volta sola per domanda (così non cambiano ad ogni refresh)"""
    if campo_ordine_opzioni not in dati:
        opzioni = dati["opzioni"]
        if randomizza_ordine_opzioni:
            opzioni = utils.randomizza_lista(opzioni)
        dati[campo_ordine_opzioni] = list(opzioni)
    return dati[campo_ordine_opzioni]


def g_risp_multiple(finestra, dati, callback_wrap):
    lista_opzioni = []

    for opzione in ordina_opzioni(dati):
        var = tk.BooleanVar()

        if dati[campo_check_domanda]:   # controllo domanda già validata
            if opzione in dati[campo_risposte_domanda]:
                var.set(True)

        opz = UI.Opzione(finestra, opzione, var, multipla=True)
        opz.pack(fill="x", pady=4)
        callback_wrap.append(lambda w, o=opz: o.set_wrap(w - 150))
        lista_opzioni.append(opz)

    return lista_opzioni


def g_risp_singola(finestra, dati, callback_wrap):
    lista_opzioni = []

    var = tk.StringVar()
    # Set risposta data precedentemente (se verificata)
    if dati[campo_check_domanda]:
        if len(dati[campo_risposte_domanda]) > 0:
            var.set(dati[campo_risposte_domanda][0])    # può avere solo una soluzione, quindi segno la prima

    for opzione in ordina_opzioni(dati):
        opz = UI.Opzione(finestra, opzione, var, valore=opzione, multipla=False)
        opz.pack(fill="x", pady=4)
        callback_wrap.append(lambda w, o=opz: o.set_wrap(w - 150))
        lista_opzioni.append(opz)

    return lista_opzioni


def g_risp_aperta(finestra, dati, callback_wrap):
    C = UI.C
    bordo = tk.Frame(finestra, bg=C["bordo"])
    bordo.pack(anchor="w", pady=6)
    entry = tk.Entry(bordo, font=UI.font_testo(2), width=20, relief="flat", bd=8,
                     bg=C["input_bg"], fg=C["testo"], insertbackground=C["testo"],
                     disabledbackground=C["input_bg"], disabledforeground=C["testo"])
    entry.pack(padx=1, pady=1)
    entry.bind("<FocusIn>", lambda _: bordo.config(bg=C["primario"]))
    entry.bind("<FocusOut>", lambda _: bordo.config(bg=C["bordo"]))

    # Set risposta data precedentemente (se verificata)
    if dati[campo_check_domanda]:
        entry.insert(0, str(dati[campo_risposte_domanda][0]))
    else:
        entry.after(50, entry.focus_set)

    return entry


def valida_risposte_multiple(dati, soluzioni, lista_opzioni):
    """Ritorna (esito, testo) con esito in 'corretta', 'parziale', 'errata'"""
    global punti
    count_giuste = 0
    errore_commesso = False
    gia_fatta = dati[campo_check_domanda]

    if not gia_fatta:
        dati[campo_risposte_domanda] = []

    for opz in lista_opzioni:
        is_selezionata = opz.selezionata()
        is_corretta = opz.testo in soluzioni

        if is_selezionata and not is_corretta:
            errore_commesso = True
        if is_selezionata and is_corretta:
            count_giuste += 1
        if is_selezionata and not gia_fatta:
            dati[campo_risposte_domanda].append(opz.testo)

        if is_corretta:
            opz.segna("corretta" if is_selezionata else "mancata")
        elif is_selezionata:
            opz.segna("errata")
        else:
            opz.segna("neutra")

    # aggiorna i punti (solo la prima volta)
    if not gia_fatta and not errore_commesso and len(soluzioni) > 0:
        punti += (1 / len(soluzioni)) * count_giuste

    dati[campo_check_domanda] = True

    if errore_commesso or count_giuste == 0:
        return "errata", "Sbagliata"
    if count_giuste == len(soluzioni):
        return "corretta", "Corretta!"
    return "parziale", f"Parzialmente corretta ({count_giuste}/{len(soluzioni)})"


def valida_risposta_singola(dati, soluzioni, lista_opzioni):
    global punti
    risposta_corretta = False
    gia_fatta = dati[campo_check_domanda]

    if not gia_fatta:
        dati[campo_risposte_domanda] = []

    for opz in lista_opzioni:
        is_selezionata = opz.selezionata()
        is_corretta = opz.testo in soluzioni

        if is_selezionata and is_corretta:
            risposta_corretta = True
        if is_selezionata and not gia_fatta:
            dati[campo_risposte_domanda].append(opz.testo)

        if is_corretta:
            opz.segna("corretta" if is_selezionata else "mancata")
        elif is_selezionata:
            opz.segna("errata")
        else:
            opz.segna("neutra")

    if not gia_fatta and risposta_corretta:
        punti += 1

    dati[campo_check_domanda] = True

    if risposta_corretta:
        return "corretta", "Corretta!"
    return "errata", "Sbagliata"


def _numero(testo):
    return float(str(testo).strip().replace(",", "."))


def valida_risposta_aperta(dati, soluzioni, entry):
    global punti

    try:
        risposta = _numero(entry.get())  # recupero il testo inserito
    except ValueError:
        return None, "Inserisci un numero valido"

    # controllo risposta corretta
    isCorretta = risposta in [_numero(x) for x in soluzioni]

    if not dati[campo_check_domanda]:   # controllo risposta mai validata
        dati[campo_risposte_domanda] = [risposta]
        if isCorretta:
            punti += 1

    entry.config(state="disabled")
    dati[campo_check_domanda] = True

    if isCorretta:
        return "corretta", "Corretta!"
    etichetta = "Risposta corretta:" if len(soluzioni) == 1 else "Risposte corrette:"
    return "errata", f"Sbagliata — {etichetta} {'; '.join(soluzioni)}"


# ---------------- SCHERMATA DOMANDA ---------------- #

def genera_schermata(dati, img=None):
    # estrai cose utili per comodità
    domanda = dati["domanda"]
    soluzioni = dati["soluzioni"]
    tipo_domanda = dati["tipologia"]
    C = UI.C

    n_totale = len(lista_domande_caricata) + len(lista_domande_fatte)
    n_attuale = len(lista_domande_fatte)

    # se c'è un'immagine grande allargo la colonna
    max_larghezza = UI.larghezza_max_contenuto
    if img is not None:
        max_larghezza = max(max_larghezza, UI.dati_img["larghezza"] + 100)

    colonna, callback_wrap = nuova_schermata(max_larghezza)

    def ridisegna():
        genera_schermata(dati, img)

    # ---- barra superiore ---- #
    barra = tk.Frame(colonna, bg=C["sfondo"])
    barra.pack(fill="x")

    tk.Label(barra, text=f"Domanda {n_attuale} / {n_totale}", bg=C["sfondo"], fg=C["testo"],
             font=UI.font_testo(0, "bold")).pack(side="left")

    # controlli (tema, dimensione testo, refresh)
    def cambia_dimensione(delta):
        if UI.dati_testo["dimensione_base"] + delta < 8:
            return
        UI.dati_testo["dimensione_base"] += delta
        segno = 1 if delta > 0 else -1
        UI.dati_img["larghezza"] = max(100, UI.dati_img["larghezza"] + segno * UI.dati_img["incremento_dimensione"])
        UI.dati_img["altezza"] = max(100, UI.dati_img["altezza"] + segno * UI.dati_img["incremento_dimensione"])
        ridisegna()

    bottone_tema(barra, ridisegna).pack(side="right")
    for testo, comando in (("A+", lambda: cambia_dimensione(2)), ("A−", lambda: cambia_dimensione(-2)),
                           ("↻", ridisegna)):
        UI.bottone(barra, testo, comando, "secondario", UI.font_piccolo(), padx=10, pady=5).pack(side="right", padx=(0, 6))

    riga_prog = tk.Frame(colonna, bg=C["sfondo"])
    riga_prog.pack(fill="x", pady=(10, 18))
    lbl_punti = tk.Label(riga_prog, text="", bg=C["primario"], fg=C["testo_primario"],
                         font=UI.font_info("bold"), padx=10, pady=2)
    lbl_punti.pack(side="right", padx=(14, 0))
    prog = UI.barra_progresso(riga_prog, n_attuale / n_totale if n_totale else 0)
    prog.pack(side="left", fill="x", expand=True)

    def aggiorna_punti():
        lbl_punti.config(text=f"★ {punti:.2f} punti")
    aggiorna_punti()

    # ---- card domanda ---- #
    esterno, card_domanda = UI.card(colonna, padx=28, pady=24)
    esterno.pack(fill="x")

    descrizione_tipo = {
        "multiple": f"Risposta multipla · seleziona tutte le risposte corrette ({len(soluzioni)})",
        "singola": "Risposta singola",
        "aperta": "Risposta aperta · inserisci un numero",
    }.get(tipo_domanda, tipo_domanda)
    titolo_sezione(card_domanda, descrizione_tipo)

    lbl_domanda = tk.Label(card_domanda, text=domanda, bg=C["card"], fg=C["testo"],
                           font=UI.font_titolo(), justify="left", anchor="w")
    lbl_domanda.pack(fill="x", pady=(0, 16))
    callback_wrap.append(lambda w: lbl_domanda.config(wraplength=max(200, w - 70)))

    # controllo immagine (e caricamento)
    if img is not None:
        img_w = UI.crea_widget_immagine(card_domanda, f"{utils.config.get('path_img', 'img/')}{img}",
                                        UI.dati_img["larghezza"], UI.dati_img["altezza"])
        img_w.pack(pady=(0, 16))
        tk.Label(card_domanda, text=img, bg=C["card"], fg=C["testo_secondario"],
                 font=UI.font_piccolo("")).pack(pady=(0, 12))

    # CARICA OPZIONI (in base al tipo di domande)
    dati_opzioni = None
    match tipo_domanda:
        case "multiple": dati_opzioni = g_risp_multiple(card_domanda, dati, callback_wrap)
        case "singola": dati_opzioni = g_risp_singola(card_domanda, dati, callback_wrap)
        case "aperta": dati_opzioni = g_risp_aperta(card_domanda, dati, callback_wrap)

    # banner esito (nascosto finché non si valida)
    banner = tk.Label(card_domanda, text="", font=UI.font_testo(0, "bold"), anchor="w",
                      justify="left", padx=14, pady=10)
    callback_wrap.append(lambda w: banner.config(wraplength=max(200, w - 100)))

    # ---- tasti ---- #
    frame_tasti = tk.Frame(colonna, bg=C["sfondo"])
    frame_tasti.pack(fill="x", pady=(18, 0))

    btn_indietro = UI.bottone(frame_tasti, "←  Indietro", carica_domanda_precedente, "secondario")
    btn_indietro.pack(side="left")
    if len(lista_domande_fatte) < 2:
        btn_indietro.set_abilitato(False)

    btn_prossima = UI.bottone(frame_tasti, "Salta  →", carica_nuova_domanda, "secondario")
    btn_prossima.pack(side="right")

    btn_valida = UI.bottone(frame_tasti, "Verifica", None, "primario")
    btn_valida.pack(side="right", padx=10)

    tk.Label(colonna, text="Invio: verifica / prossima   ·   ← →: naviga   ·   1-9: seleziona risposta",
             bg=C["sfondo"], fg=C["testo_secondario"], font=UI.font_piccolo("")).pack(pady=(16, 0))

    # LOGICA VALIDA (in base alla tipologia)
    def valida_risposte():
        if dati[campo_check_domanda] and btn_valida._abilitato is False:
            return
        match tipo_domanda:
            case "multiple": esito, testo = valida_risposte_multiple(dati, soluzioni, dati_opzioni)
            case "singola": esito, testo = valida_risposta_singola(dati, soluzioni, dati_opzioni)
            case "aperta": esito, testo = valida_risposta_aperta(dati, soluzioni, dati_opzioni)
            case _: return

        colori = {
            "corretta": (C["successo_bg"], C["successo"], "✓  "),
            "parziale": (C["successo_bg"], C["successo"], "◐  "),
            "errata": (C["errore_bg"], C["errore"], "✗  "),
            None: (C["errore_bg"], C["errore"], "!  "),
        }
        bg, fg, icona = colori[esito]
        banner.config(text=icona + testo, bg=bg, fg=fg)
        banner.pack(fill="x", pady=(14, 0))

        if esito is None:   # input non valido, si può riprovare
            return

        aggiorna_punti()

        btn_valida.set_abilitato(False)
        btn_prossima.destroy()
        nuovo = UI.bottone(frame_tasti, "Prossima  →", carica_nuova_domanda, "primario")
        nuovo.pack(side="right", before=btn_valida)
        app_frame.focus_set()

    btn_valida.bind("<ButtonRelease-1>", lambda _: btn_valida._abilitato and valida_risposte(), add="+")

    # scorciatoie da tastiera
    def invio():
        if dati[campo_check_domanda]:
            carica_nuova_domanda()
        else:
            valida_risposte()

    azioni_tastiera["Return"] = invio
    azioni_tastiera["KP_Enter"] = invio
    azioni_tastiera["Right"] = carica_nuova_domanda
    if len(lista_domande_fatte) >= 2:
        azioni_tastiera["Left"] = carica_domanda_precedente
    if tipo_domanda in ("multiple", "singola"):
        for i, opz in enumerate(dati_opzioni[:9]):
            azioni_tastiera[str(i + 1)] = (lambda o=opz: o._click(None))

    # valida automaticamente (senza dare punti) se la domanda è già stata completata
    if dati[campo_check_domanda]:
        valida_risposte()


# ---------------- SCHERMATA FINALE ---------------- #

def genera_schermata_finale():
    colonna, callback_wrap = nuova_schermata(640)
    C = UI.C

    n_totale = len(lista_domande_fatte)
    n_risposte = sum(1 for d in lista_domande_fatte if d.get(campo_check_domanda))
    percentuale = (punti / n_totale * 100) if n_totale else 0

    header = tk.Frame(colonna, bg=C["sfondo"])
    header.pack(fill="x", pady=(0, 20))
    bottone_tema(header, genera_schermata_finale).pack(side="right")

    esterno, c = UI.card(colonna, padx=32, pady=32)
    esterno.pack(fill="x")

    tk.Label(c, text="Quiz completato!", bg=C["card"], fg=C["testo"], font=UI.font_titolo(8)).pack()
    lbl_sotto = tk.Label(c, text="Hai risposto a tutte le domande disponibili.", bg=C["card"],
                         fg=C["testo_secondario"], font=UI.font_testo(), justify="center")
    lbl_sotto.pack(pady=(4, 24))
    callback_wrap.append(lambda w: lbl_sotto.config(wraplength=max(150, w - 80)))

    colore = C["successo"] if percentuale >= 60 else C["errore"]
    tk.Label(c, text=f"{punti:.2f} / {n_totale}", bg=C["card"], fg=colore, font=UI.font_titolo(20)).pack()
    tk.Label(c, text=f"{percentuale:.0f}%", bg=C["card"], fg=C["testo_secondario"], font=UI.font_titolo(2)).pack()

    prog = UI.barra_progresso(c, percentuale / 100, altezza=10)
    prog.pack(fill="x", pady=20)

    tk.Label(c, text=f"Domande verificate: {n_risposte}   ·   Saltate: {n_totale - n_risposte}",
             bg=C["card"], fg=C["testo_secondario"], font=UI.font_info()).pack()

    tasti = tk.Frame(colonna, bg=C["sfondo"])
    tasti.pack(pady=24)
    UI.bottone(tasti, "Esci", root.destroy, "secondario").pack(side="left", padx=6)
    UI.bottone(tasti, "↺  Ricomincia", ricomincia, "primario").pack(side="left", padx=6)

    azioni_tastiera["Return"] = ricomincia
    azioni_tastiera["KP_Enter"] = ricomincia


def ricomincia():
    global lista_domande_caricata, lista_domande_fatte, punti
    lista_domande_caricata = []
    lista_domande_fatte = []
    punti = 0
    genera_schermata_scelta_file()


# ---------------- LOGICA ---------------- #

def inizio_quiz():
    inizializza_dati()

    if lista_domande_caricata:
        carica_nuova_domanda()
    else:
        messagebox.showwarning("Attenzione", "Nessuna domanda caricata dai file scelti.")
        ricomincia()


def deduci_tipologia(n_opzioni, n_soluzioni):
    if n_opzioni > 0 and n_soluzioni > 1:
        return "multiple"
    if n_opzioni > 0 and n_soluzioni == 1:
        return "singola"

    return "aperta"


def inizializza_dati():
    global lista_domande_caricata

    for nome_file in elenco_file:
        try:
            with open(nome_file, 'r', encoding='utf-8') as file:
                lista_domande_caricata += json.load(file)
        except FileNotFoundError:
            messagebox.showerror("Errore", f"File {nome_file} non trovato!")
        except json.JSONDecodeError:
            messagebox.showerror(
                "Errore", f"Il file {nome_file} non è formattato correttamente.")

    # aggiungo campo di verifica della risposta a ciascuna domanda, controllo inserimento tipologia
    for item in lista_domande_caricata:
        item[campo_check_domanda] = False
        item.pop(campo_ordine_opzioni, None)
        item.setdefault("opzioni", [])

        # controllo esistenza campo tipologia
        if "tipologia" not in item:
            item["tipologia"] = deduci_tipologia(len(item["opzioni"]), len(item["soluzioni"]))

    # randomizza le domande
    if randomizza_domande:
        lista_domande_caricata = utils.randomizza_lista(lista_domande_caricata)
    else:
        # le domande vengono prese dalla fine della lista
        lista_domande_caricata.reverse()


def carica_domanda_precedente():
    if len(lista_domande_fatte) < 2:
        return
    lista_domande_caricata.append(lista_domande_fatte.pop(-1))
    lista_domande_caricata.append(lista_domande_fatte.pop(-1))

    carica_nuova_domanda()


def carica_nuova_domanda():
    # domande finite
    if not lista_domande_caricata:
        genera_schermata_finale()
        return

    # sposto la domanda attuale nella lista degli "scarti"
    lista_domande_fatte.append(lista_domande_caricata.pop())
    dati = lista_domande_fatte[-1]

    genera_schermata(dati, dati.get("img"))


'''
    1) carica settings
    2) inizializza pagina di scelta del file
    3) init domande
        - carica
        - mischia le domande
    4) funzione quiz
        - controlla necessità immagine allegata (e controlla che esista)
'''


def main():
    global root, app_frame, scroll

    UI.init_settings_UI()
    utils.init_config()
    if utils.config is None:
        utils.config = {}

    root = tk.Tk()
    root.title("Quiz")

    w = UI.dati_pagina.get("larghezza", 900)
    h = UI.dati_pagina.get("altezza", 750)
    root.geometry(f"{w}x{h}")
    root.minsize(520, 400)

    scroll = UI.ScrollableFrame(root)
    scroll.pack(fill="both", expand=True)

    app_frame = scroll.scrollable_frame
    root.bind_all("<Key>", gestisci_tasto)

    genera_schermata_scelta_file()

    root.mainloop()


if __name__ == "__main__":
    main()
