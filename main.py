import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

APP_NAME = "Personal Cassette Player - No VLC"

SUPPORTED_EXTENSIONS = [
    "*.mp3",
    "*.wav",
    "*.aac",
    "*.m4a",
    "*.flac",
    "*.ogg"
]


try:
    import win32com.client
except ImportError:
    raise SystemExit(
        "Errore: pywin32 non è installato.\n"
        "Esegui: pip install -r requirements.txt"
    )


class WindowsMediaPlayerBackend:
    """
    Backend basato su Windows Media Player tramite COM.
    Non richiede VLC.
    Funziona su Windows con i codec disponibili nel sistema.
    """

    def __init__(self):
        try:
            self.player = win32com.client.Dispatch("WMPlayer.OCX")
            self.player.settings.volume = 70
        except Exception as exc:
            raise RuntimeError(
                "Impossibile inizializzare Windows Media Player.\n"
                "Su alcune versioni di Windows potrebbe essere necessario abilitare "
                "'Windows Media Player' dalle funzionalità opzionali."
            ) from exc

    def load(self, file_path: str):
        self.player.URL = file_path

    def play(self):
        self.player.controls.play()

    def pause(self):
        self.player.controls.pause()

    def stop(self):
        self.player.controls.stop()

    def set_volume(self, value: int):
        self.player.settings.volume = max(0, min(100, int(value)))


class LocalMusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("720x470")
        self.root.minsize(680, 430)

        self.playlist = []
        self.current_index = None
        self.is_paused = False

        try:
            self.audio = WindowsMediaPlayerBackend()
        except RuntimeError as exc:
            messagebox.showerror("Errore audio", str(exc))
            raise

        self.build_ui()

    def build_ui(self):
        title = tk.Label(
            self.root,
            text="🎵 Personal Cassette Player",
            font=("Segoe UI", 22, "bold")
        )
        title.pack(pady=(16, 8))

        subtitle = tk.Label(
            self.root,
            text="Versione Windows senza VLC",
            font=("Segoe UI", 10)
        )
        subtitle.pack(pady=(0, 4))

        self.current_song_label = tk.Label(
            self.root,
            text="Nessun brano selezionato",
            font=("Segoe UI", 11),
            wraplength=640
        )
        self.current_song_label.pack(pady=4)

        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.listbox = tk.Listbox(
            list_frame,
            height=11,
            font=("Segoe UI", 10),
            activestyle="dotbox"
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        self.listbox.bind("<Double-Button-1>", self.play_selected_from_list)

        controls_frame = tk.Frame(self.root)
        controls_frame.pack(pady=8)

        tk.Button(
            controls_frame,
            text="➕ Aggiungi musica",
            command=self.add_files,
            width=18
        ).grid(row=0, column=0, padx=4)

        tk.Button(
            controls_frame,
            text="🗑 Rimuovi",
            command=self.remove_selected,
            width=11
        ).grid(row=0, column=1, padx=4)

        tk.Button(
            controls_frame,
            text="⏮",
            command=self.previous_song,
            width=7
        ).grid(row=0, column=2, padx=4)

        tk.Button(
            controls_frame,
            text="▶ Play",
            command=self.play_song,
            width=10
        ).grid(row=0, column=3, padx=4)

        tk.Button(
            controls_frame,
            text="⏸ Pausa",
            command=self.pause_song,
            width=10
        ).grid(row=0, column=4, padx=4)

        tk.Button(
            controls_frame,
            text="⏹ Stop",
            command=self.stop_song,
            width=10
        ).grid(row=0, column=5, padx=4)

        tk.Button(
            controls_frame,
            text="⏭",
            command=self.next_song,
            width=7
        ).grid(row=0, column=6, padx=4)

        volume_frame = tk.Frame(self.root)
        volume_frame.pack(pady=8)

        tk.Label(
            volume_frame,
            text="Volume",
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=6)

        self.volume_slider = tk.Scale(
            volume_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.set_volume,
            length=300
        )
        self.volume_slider.set(70)
        self.volume_slider.pack(side=tk.LEFT)

        footer = tk.Label(
            self.root,
            text="Formati: MP3, WAV, AAC, M4A e altri se supportati da Windows",
            font=("Segoe UI", 9)
        )
        footer.pack(pady=(2, 10))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def add_files(self):
        filetypes = [
            ("File audio", " ".join(SUPPORTED_EXTENSIONS)),
            ("MP3", "*.mp3"),
            ("WAV", "*.wav"),
            ("AAC", "*.aac"),
            ("M4A", "*.m4a"),
            ("FLAC", "*.flac"),
            ("OGG", "*.ogg"),
            ("Tutti i file", "*.*"),
        ]

        files = filedialog.askopenfilenames(
            title="Scegli file musicali",
            filetypes=filetypes
        )

        if not files:
            return

        added = 0

        for file in files:
            if file not in self.playlist:
                self.playlist.append(file)
                self.listbox.insert(tk.END, Path(file).name)
                added += 1

        if self.current_index is None and self.playlist:
            self.current_index = 0
            self.update_current_song_label()
            self.update_listbox_selection()

        if added == 0:
            messagebox.showinfo("Playlist", "I file selezionati erano già presenti nella playlist.")

    def remove_selected(self):
        selection = self.listbox.curselection()

        if not selection:
            messagebox.showinfo("Nessuna selezione", "Seleziona un brano da rimuovere.")
            return

        index = selection[0]
        was_current = index == self.current_index

        if was_current:
            self.stop_song()

        del self.playlist[index]
        self.listbox.delete(index)

        if not self.playlist:
            self.current_index = None
            self.current_song_label.config(text="Nessun brano selezionato")
            return

        if self.current_index is None:
            self.current_index = 0
        elif index < self.current_index:
            self.current_index -= 1
        elif index == self.current_index:
            self.current_index = min(index, len(self.playlist) - 1)

        self.update_current_song_label()
        self.update_listbox_selection()

    def play_song(self):
        if not self.playlist:
            messagebox.showinfo("Nessun file", "Aggiungi prima almeno un file musicale.")
            return

        if self.current_index is None:
            self.current_index = 0

        if self.is_paused:
            self.audio.play()
            self.is_paused = False
            return

        file_path = self.playlist[self.current_index]

        if not os.path.exists(file_path):
            messagebox.showerror("File non trovato", f"Il file non esiste più:\n{file_path}")
            return

        try:
            self.audio.load(file_path)
            self.audio.play()
        except Exception as exc:
            messagebox.showerror(
                "Errore riproduzione",
                "Non riesco a riprodurre questo file.\n"
                "Potrebbe mancare il codec sul PC oppure il formato non è supportato.\n\n"
                f"File: {file_path}\n\n"
                f"Errore: {exc}"
            )
            return

        self.update_current_song_label()
        self.update_listbox_selection()

    def pause_song(self):
        try:
            self.audio.pause()
            self.is_paused = True
        except Exception:
            pass

    def stop_song(self):
        try:
            self.audio.stop()
            self.is_paused = False
        except Exception:
            pass

    def next_song(self):
        if not self.playlist:
            return

        if self.current_index is None:
            self.current_index = 0
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)

        self.is_paused = False
        self.play_song()

    def previous_song(self):
        if not self.playlist:
            return

        if self.current_index is None:
            self.current_index = 0
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)

        self.is_paused = False
        self.play_song()

    def play_selected_from_list(self, event=None):
        selection = self.listbox.curselection()

        if not selection:
            return

        self.current_index = selection[0]
        self.is_paused = False
        self.play_song()

    def set_volume(self, value):
        try:
            self.audio.set_volume(int(float(value)))
        except Exception:
            pass

    def update_current_song_label(self):
        if self.current_index is None or not self.playlist:
            self.current_song_label.config(text="Nessun brano selezionato")
            return

        song_name = Path(self.playlist[self.current_index]).name
        self.current_song_label.config(text=f"In riproduzione: {song_name}")

    def update_listbox_selection(self):
        self.listbox.selection_clear(0, tk.END)

        if self.current_index is not None and self.playlist:
            self.listbox.selection_set(self.current_index)
            self.listbox.activate(self.current_index)
            self.listbox.see(self.current_index)

    def on_close(self):
        self.stop_song()
        self.root.destroy()


def main():
    if not sys.platform.startswith("win"):
        raise SystemExit("Questa versione senza VLC è pensata per Windows.")

    root = tk.Tk()
    LocalMusicPlayer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
