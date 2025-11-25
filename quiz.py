import UI
import utils
import tkinter as tk
from tkinter import messagebox
import json

# ---------VAR GLOBALI-----------#

lista_domande_caricata = []
lista_domande_fatte = []
punti = 0
campo_check_domanda = "isCompleted"
campo_risposte_domanda = "risposte"

nome_file = ""  # nome del file delle domande

# ------------------------------#


def genera_schermata_scelta_file():
    global nome_file

    var_temp = tk.StringVar(value=None)

    lbl = tk.Label(root, text="Quale file vuoi usare?", font=(
        UI.dati_testo["font_titoli"], UI.dati_testo["dimensione_base"] + UI.dati_testo["diff_titoli"], "bold"))
    lbl.pack(pady=10)

    for file in utils.elenca_file_json(utils.config["path_domande"]):

        radio = tk.Radiobutton(
            root,
            text=file.split("/")[-1],
            value=file,
            variable=var_temp,
            font=(
                UI.dati_testo["font_testo"],
                UI.dati_testo["dimensione_base"]
            ),
            anchor="w"
        )
        radio.pack(fill='x', padx=20, pady=2)

    def set_nome_file():
        global nome_file
        nome_file = var_temp.get()
        inizio_quiz()

    btn = tk.Button(root, text="CONFERMA SCELTA", bg="green",
                    fg="white", command=set_nome_file)
    btn.pack(pady=20)


def genera_schermata(finestra, dati, funzione_salta, img=None):
    global punti

    # estrai cose utili per comodità
    domanda = dati["domanda"]
    opzioni = dati["opzioni"]
    soluzioni = dati["soluzioni"]

    # pulisci schiavo
    for widget in finestra.winfo_children():
        widget.destroy()

    # DOMMANNDDA
    # <--- Aumentato wraplength per finestre più larghe, ci sta gem
    lbl_domanda = tk.Label(finestra, text=domanda, font=(
        UI.dati_testo["font_titoli"], UI.dati_testo["dimensione_base"] + UI.dati_testo["diff_titoli"], "bold"), justify="center")
    lbl_domanda.pack(pady=20, expand=True, fill='both')

    if img is not None:
        img_w = UI.crea_widget_immagine(finestra, f"{utils.config["path_img"]}{
                                        img}", UI.dati_img["larghezza"], UI.dati_img["altezza"])
        img_w.pack(pady=10)

    # carica opzioni della domanda
    lista_checkbuttons = []

    frame_opzioni = tk.Frame(finestra)
    frame_opzioni.pack(pady=10)

    temp_opzioni = utils.randomizza_lista(opzioni)
    for opzione in temp_opzioni:
        var = tk.BooleanVar()

        if dati[campo_check_domanda]:
            if opzione in dati[campo_risposte_domanda]:
                var.set(True)

        # Aggiunto wraplength anche alle opzioni per evitare che escano dallo schermo, super mario karta
        chk = tk.Checkbutton(frame_opzioni, text=opzione, variable=var, font=(
            UI.dati_testo["font_testo"], UI.dati_testo["dimensione_base"]), selectcolor="white", wraplength=500, justify="left")
        chk.pack(anchor="w", pady=2)
        lista_checkbuttons.append((chk, var, opzione))

    # LOGICA VALIDA
    def valida_risposte():
        global punti
        count_giuste = 0
        errore_commesso = False

        # creo un nuovo campo per tenere le riposte date
        if not dati[campo_check_domanda]:
            dati[campo_risposte_domanda] = []

        for chk_widget, var_value, testo_opzione in lista_checkbuttons:

            is_selezionata = var_value.get()
            is_corretta = testo_opzione in soluzioni

            if not dati[campo_check_domanda]:

                # calcolo punti
                if is_selezionata and not is_corretta:
                    errore_commesso = True

                if is_selezionata and is_corretta:
                    count_giuste += 1

                # -------------------------

                # segno le risposte date (solo se non ha mai risposto a questa domanda)

                if is_selezionata:
                    dati[campo_risposte_domanda].append(testo_opzione)

            # ---------------------

            chk_widget.config(bg="#f0f0f0", fg="black")  # Reset

            if is_corretta:
                chk_widget.config(bg="lightgreen", selectcolor="lightgreen")

            elif is_selezionata and not is_corretta:
                chk_widget.config(bg="#ffcccc")

        # aggiorna i punti
        if dati[campo_check_domanda] is False:  # controllo se ha già risposto alla domanda
            if not errore_commesso and len(soluzioni) > 0:
                tot_punti = (1 / len(soluzioni)) * count_giuste
                punti += tot_punti

        # segno la domanda come completata
        dati[campo_check_domanda] = True

    # tastini oja
    frame_tasti = tk.Frame(finestra)
    frame_tasti.pack(side="bottom", pady=20)

    btn_indietro = tk.Button(frame_tasti, text="INDIETRO", bg="red", fg="white", font=(
        UI.dati_testo["font_testo"], UI.dati_testo["dimensione_base"], "bold"), command=carica_domanda_precedente)
    btn_indietro.pack(side="left", padx=20)
    btn_valida = tk.Button(frame_tasti, text="VALIDA", bg="green", fg="white", font=(UI.dati_testo["font_testo"], UI.dati_testo["dimensione_base"], "bold"),
                           command=valida_risposte)
    btn_valida.pack(side="right", padx=20)

    btn_salta = tk.Button(frame_tasti, text="SALTA / PROSSIMA", bg="orange", fg="white", font=(UI.dati_testo["font_testo"], UI.dati_testo["dimensione_base"], "bold"),
                          command=funzione_salta)
    btn_salta.pack(side="left", expand=True)

    # info
    frame_info = tk.Frame(finestra)
    frame_info.pack(pady=10)
    label_N_domande = tk.Label(frame_info, text=f"domanda: {len(lista_domande_fatte)}/{len(lista_domande_caricata) + len(
        lista_domande_fatte)}", font=(UI.dati_testo["font_testo"], UI.dati_testo["dimensione_base"] - UI.dati_testo["diff_info"]))
    label_N_domande.pack(side="left", padx=20)

    label_punti = tk.Label(frame_info, text=f"punti: {punti:.2f}/{len(lista_domande_caricata) + len(lista_domande_fatte)}", font=(
        UI.dati_testo["font_testo"], UI.dati_testo["dimensione_base"] - UI.dati_testo["diff_info"]))
    label_punti.pack(side="right", padx=20)

    def inc_dim_text():

        UI.dati_testo["dimensione_base"] += 2
        UI.dati_img["larghezza"] += UI.dati_img["incremento_dimensione"]
        UI.dati_img["altezza"] += UI.dati_img["incremento_dimensione"]
        genera_schermata(finestra, dati, funzione_salta, img)
        return

    def dec_dim_text():

        UI.dati_testo["dimensione_base"] -= 2
        UI.dati_img["larghezza"] -= UI.dati_img["incremento_dimensione"]
        UI.dati_img["altezza"] -= UI.dati_img["incremento_dimensione"]
        genera_schermata(finestra, dati, funzione_salta, img)
        return

    inc_button = tk.Button(frame_info, text="+", bg="gray", fg="black", font=(
        UI.dati_testo["font_testo"], UI.dati_testo["dimensione_base"] - UI.dati_testo["diff_sett"], "bold"), command=inc_dim_text)
    inc_button.pack(side="right", pady=2)
    dec_button = tk.Button(frame_info, text="-", bg="gray", fg="black", font=(
        UI.dati_testo["font_testo"], UI.dati_testo["dimensione_base"] - UI.dati_testo["diff_sett"], "bold"), command=dec_dim_text)
    dec_button.pack(side="left", pady=2)

    # mantiene un margine costante anche con la finestra scalata

    def aggiorna_wraplength(event):
        # Imposta il wraplength alla larghezza della finestra meno un margine (es. 40px)
        lbl_domanda.config(
            wraplength=finestra.winfo_width() - UI.margine_finestre)
        label_N_domande.config(
            wraplength=finestra.winfo_width() - UI.margine_finestre)
        label_punti.config(
            wraplength=finestra.winfo_width() - UI.margine_finestre)
    finestra.bind('<Configure>', aggiorna_wraplength)

    # valida automaticamente (senza dare punti) se la domanda è già stata completata
    if dati[campo_check_domanda]:
        valida_risposte()


def inizio_quiz():
    inizializza_dati()

    if lista_domande_caricata:
        carica_nuova_domanda()


def inizializza_dati():
    global nome_file
    global lista_domande_caricata

    try:
        # <--- CORREZIONE: Aggiunto encoding='utf-8' per leggere gli accenti correttamente, onomatopea della libellula
        with open(nome_file, 'r', encoding='utf-8') as file:
            lista_domande_caricata = json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Errore", f"File {nome_file} non trovato!")
        root.destroy()
    except json.JSONDecodeError:
        messagebox.showerror(
            "Errore", f"Il file {nome_file} non è formattato correttamente.")
        root.destroy()

    # aggiungo campo di verifica della risposta a ciascuna domanda
    for item in lista_domande_caricata:
        # (non ancora completata, e grazie alla pisella)
        item[campo_check_domanda] = False

    # randomizza le domande
    lista_domande_caricata = utils.randomizza_lista(lista_domande_caricata)

############


def carica_domanda_precedente():
    lista_domande_caricata.append(lista_domande_fatte.pop(-1))
    lista_domande_caricata.append(lista_domande_fatte.pop(-1))

    carica_nuova_domanda()


def carica_nuova_domanda():

    # avviso domande finite
    if not lista_domande_caricata:
        messagebox.showinfo(
            "Finito!", f"Hai risposto a tutte le domande disponibili. Hai fatto {punti} punti.")
        root.destroy()
        return

    # aggiorno n domande fatte in totale

    # sposto la domana attuale nella lista degli "scarti"
    lista_domande_fatte.append(lista_domande_caricata.pop())
    dati = lista_domande_fatte[-1]

    # controllo necessità immagine
    img = None
    try:
        img = dati["img"]
    except Exception:
        pass

    # Chiama la funzione grafica
    genera_schermata(
        root,
        dati,
        carica_nuova_domanda,
        img  # None se non serve
    )


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
    global root

    UI.init_settings_UI()
    utils.init_config()

    root = tk.Tk()
    root.title("Quiz")
    root.geometry(f"{UI.dati_pagina["altezza"]}x{UI.dati_pagina["larghezza"]}")

    genera_schermata_scelta_file()

    root.mainloop()


if __name__ == "__main__":
    main()
