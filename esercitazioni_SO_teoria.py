import tkinter as tk
import json
from tkinter import messagebox
import random



lista_domande_caricata = []
lista_domande_fatte = []


def randomizza_lista(list_inp):
    new_list = []
    lista = list_inp.copy()

    while len(lista) > 0:
        rand = random.randrange(len(lista))
        new_list.append(lista.pop(rand))

    return new_list


def genera_schermata(finestra, domanda, opzioni, soluzioni, funzione_salta):
    """
    Genera la schermata del quiz.
    """
    # pulisci schiavo
    for widget in finestra.winfo_children():
        widget.destroy()

    # <--- Aumentato wraplength per finestre più larghe, ci sta gem
    lbl_domanda = tk.Label(finestra, text=domanda, font=(
        "Arial", 14, "bold"), wraplength=550, justify="center")
    lbl_domanda.pack(pady=20)

    # 3. OPZIONI
    lista_checkbuttons = []

    frame_opzioni = tk.Frame(finestra)
    frame_opzioni.pack(pady=10)

    temp_opzioni = randomizza_lista(opzioni)
    for opzione in temp_opzioni:
        var = tk.BooleanVar()
        # Aggiunto wraplength anche alle opzioni per evitare che escano dallo schermo, super mario karta
        chk = tk.Checkbutton(frame_opzioni, text=opzione, variable=var, font=(
            "Arial", 11), selectcolor="white", wraplength=500, justify="left")
        chk.pack(anchor="w", pady=2)
        lista_checkbuttons.append((chk, var, opzione))

    # LOGICA VALIDA
    def valida_risposte():
        for chk_widget, var_value, testo_opzione in lista_checkbuttons:
            chk_widget.config(bg="#f0f0f0", fg="black")

            if testo_opzione in soluzioni:
                chk_widget.config(bg="lightgreen", selectcolor="lightgreen")

            elif var_value.get() == True and testo_opzione not in soluzioni:
                chk_widget.config(bg="#ffcccc")

    # tastini oja
    frame_tasti = tk.Frame(finestra)
    frame_tasti.pack(side="bottom", pady=20)

    btn_indietro = tk.Button(frame_tasti, text="INDIETRO", bg="red", fg ="white", font= ("Arial",10,"bold"), command = carica_domanda_precedente)
    btn_indietro.pack(side = "left", padx = 20)
    btn_valida = tk.Button(frame_tasti, text="VALIDA", bg="green", fg="white", font=("Arial", 10, "bold"),
                           command=valida_risposte)
    btn_valida.pack(side="right", padx=20)

    btn_salta = tk.Button(frame_tasti, text="SALTA / PROSSIMA", bg="orange", fg="white", font=("Arial", 10, "bold"),
                          command=funzione_salta)
    btn_salta.pack(side="left", expand = True)
    

    frame_info = tk.Frame(finestra)
    frame_info.pack(pady=10)

    label_N_domande = tk.Label(frame_info, text = f"{len(lista_domande_fatte)}/{len(lista_domande_caricata)+len(lista_domande_fatte)}")
    label_N_domande.pack(padx=20)
    




def inizializza_dati():
    """Legge il file JSON una volta sola all'avvio"""
    global lista_domande_caricata
    try:
        # <--- CORREZIONE: Aggiunto encoding='utf-8' per leggere gli accenti correttamente, onomatopea della libellula
        with open('domande.json', 'r', encoding='utf-8') as file:
            lista_domande_caricata = json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Errore", "File 'domande.json' non trovato!")
        root.destroy()
    except json.JSONDecodeError:
        messagebox.showerror(
            "Errore", "Il file 'domande.json' non è formattato correttamente.")
        root.destroy()

    #randomizza le domande
    mischia_domande()


def mischia_domande():
    global lista_domande_caricata
    lista_domande_caricata = randomizza_lista(lista_domande_caricata)



def carica_domanda_precedente():
    lista_domande_caricata.append(lista_domande_fatte.pop(-1))
    lista_domande_caricata.append(lista_domande_fatte.pop(-1))

    
    carica_nuova_domanda()


def carica_nuova_domanda():
    """Pesca una domanda dalla lista caricata e aggiorna la grafica"""

    if not lista_domande_caricata:
        messagebox.showinfo(
            "Finito!", "Hai risposto a tutte le domande disponibili.")
        root.destroy()
        return

    
    
    lista_domande_fatte.append(lista_domande_caricata.pop())
    dati = lista_domande_fatte[-1]
    # Chiama la funzione grafica
    genera_schermata(
        root,
        dati["domanda"],
        dati["opzioni"],
        dati["soluzioni"],
        carica_nuova_domanda
    )


# --- main senza main ---
root = tk.Tk()
root.title("Quiz SO")
root.geometry("700x500")

inizializza_dati()

if lista_domande_caricata:
    carica_nuova_domanda()

root.mainloop()
