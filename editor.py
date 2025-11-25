import UI
import utils

import tkinter as tk
from tkinter import messagebox
import json

# --------------- VAR GLOBALI ---------------

root = None 
nome_file = ""
domande_caricate = []
file_stream = None      # stream di scrittura

# ---------------------------------------------

def gen_sh_scelta_file():
    global nome_file


    lbl = tk.Label(root, text="Quale file vuoi modificare?", font=(
        UI.dati_testo["font_titoli"], UI.dati_testo["dimensione_base"] + UI.dati_testo["diff_titoli"], "bold"))
    lbl.pack(pady=10)


    var_temp = tk.StringVar(value=None)
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
        avvio_editor()


    btn = tk.Button(root, text="CONFERMA SCELTA", bg="green",
                    fg="white", command=set_nome_file)
    btn.pack(pady=20)

    btn = tk.Button(root, text="CREA NUOVO FILE", bg="red",
                    fg="white", command=crea_file_domande)
    btn.pack(pady=20)


def crea_file_domande():
    UI.pulisci_finestra(root)
    tk.Label(root, text="Inserisci nome nuovo file(senza estensione):").pack()

    entry_nome = tk.Entry(root, width=40)
    entry_nome.pack()

    def set_nome_file():
        global nome_file
        nome_file = entry_nome.get()
        open(f"{nome_file}.json", "w+")   #crea file
        avvio_editor()

    btn = tk.Button(root, text="CONFERMA SCELTA", bg="green",
                    fg="white", command=set_nome_file)
    btn.pack(pady=20)

def avvio_editor():
    init_dati() # carica l'array di file (se esiste)


def gen_schermata(dati, domanda = "" ,n_opzioni = 1, opzioni = []):

    UI.pulisci_finestra(root)

    domanda = dati["domanda"]
    opzioni = dati["opzioni"]
    soluzioni = dati["soluzioni"]
    img = None
    try: 
        img = dati["img"]
    except Exception:
        pass 


    lbl = tk.Label(root, text="Domanda: ", font=(
        UI.dati_testo["font_titoli"], UI.dati_testo["dimensione_base"] + UI.dati_testo["diff_titoli"], "bold"))
    lbl.pack(pady=10)

    #text box domanda
    text_area_domanda = tk.Text(root, width=40, height=3) 
    text_area_domanda.pack()
    text_area_domanda.insert(tk.END, domanda)


    # -------- opzioni ------------
    frame_opzioni = tk.Frame(root)
    frame_opzioni.pack(pady=10)

    lista_opzioni = [] 

    if len(opzioni) < n_opzioni:
        for _ in range(n_opzioni - len(opzioni)):
            opzioni.append("")

    for o in opzioni:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(frame_opzioni, variable=var)
        chk.pack(anchor="w", pady=2)

        opt = tk.Text(root, width=40, height=3) 
        opt.pack(anchor="e", pady=2)
        opt.insert(tk.END, o)

        lista_opzioni.append((var, opt))

    #tasto aggiunta opzioni
    dec_button = tk.Button(frame_opzioni, text="aggiungi opzione", bg="gray", fg="black", font=(
        UI.dati_testo["font_testo"], UI.dati_testo["dimensione_base"] - UI.dati_testo["diff_sett"], "bold"), command=inc_opzioni)
    dec_button.pack(side="left", pady=2)

    # ------------------------------


    btn = tk.Button(root, text="SALVA", bg="green",
                    fg="white", command=add_quesito)
    btn.pack(pady=20)


    def inc_opzioni():
        gen_schermata(dati, text_area_domanda.get("1.0", "end-1c"),n_opzioni+1, opzioni)

    def add_quesito():
        # domanda, opzioni, soluzioni, img
        pass





def init_dati():
    global domande_caricate, file_stream

    try:
        with open(nome_file, 'r', encoding='utf-8') as file:
            domande_caricate = json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Errore", f"File {nome_file} non trovato!")
        root.destroy()
    except json.JSONDecodeError:
        messagebox.showerror(
            "Errore", f"Il file {nome_file} non è formattato correttamente.")
        root.destroy()

    # crea backup domande in "<nome_file>_backup.json"
    with open(f"{nome_file}_backup.json", "w+", encoding='utf-8') as file:
        json.dump(domande_caricate, file, indent=4, ensure_ascii=False)

    # apro stream (globale)
    file_stream = open(nome_file, "w+",encoding='utf-8')
    


def main():
    '''
        1) schermata scelta file
            - mostra file esistenti da aprire (e modificare)
            - tasto nuovo file
        2) carica schermata editor:
            CREA COPIA TEMPORANEA DEL FILE
            stile simile ai quiz con tasto prossima domanda e indietro.
            Campi inseribili:
                - domanda
                - opzioni
                  - opzione bool a fianco per selezionare se è corretta
                  - tasto aggiungi opzione
                - caricamento immagine
            Tasto SALVA sempre visibile
    '''
    
    UI.init_settings_UI()
    utils.init_config()

    root = tk.Tk()
    root.title("Editor domande")
    root.geometry(f"{UI.dati_pagina["altezza"]}x{UI.dati_pagina["larghezza"]}")


    root.mainloop()


if __name__ == "__main__":
    main()

