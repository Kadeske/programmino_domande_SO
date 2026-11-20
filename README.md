
E' un misto di domande dai vecchi form con aggiunte le domande dei quiz di preesame 2025/26.

### Come usare
1. Scarica tutto nella stessa directory
2. Avvia il programma python "quiz.py" nella stessa directory (serve `pip install pillow`)
	- se sei su windows puoi usare "quiz.exe" invece di python:
		1. vai su [Actions → Compila quiz.exe](https://github.com/Kadeske/programmino_domande_unica/actions/workflows/build-exe.yml) (serve essere loggati su GitHub)
		2. apri l'esecuzione più recente con la spunta verde
		3. in fondo alla pagina, sotto "Artifacts", scarica `quiz-exe` ed estrai `quiz.exe`
		4. mettilo nella stessa cartella di `domande/`, `img/` e `settings.json` e avvialo

- modifica "settings.json" per cambiare dimensione (immagini e testo) e font
- tema chiaro/scuro: bottone in alto a destra, oppure `"tema": "scuro"` dentro `UI.pagina` in "settings.json"

### Scorciatoie da tastiera
- `Invio`: verifica la risposta / passa alla prossima
- `→` / `←`: prossima / precedente
- `1`-`9`: seleziona la risposta corrispondente

#### potrebbero esserci errori

Le domande non sono le stesse dell'esame ma sono molto simili. Spesso sono identiche ma con risposte diverse.

