import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import yt_dlp
import threading
import os

class ExportifyDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Exportify to MP3")
        self.root.geometry("620x480")
        self.root.configure(bg="#1e1e1e")

        # UI Styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", 
                        thickness=15, 
                        troughcolor='#2d3436', 
                        background='#D4AF37', 
                        bordercolor="#1e1e1e")
        
        self.csv_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.is_downloading = False

        self.create_widgets()

    def create_widgets(self):
        # Header
        tk.Label(self.root, text="Serenity Downloader", font=("Cormorant Garamond", 24, "bold"), 
                 fg="#E8B4B8", bg="#1e1e1e", pady=20).pack()

        # Selection Area
        main_frame = tk.Frame(self.root, bg="#1e1e1e", padx=30)
        main_frame.pack(fill='both', expand=True)

        # File Input
        self.create_input_group(main_frame, "Exportify CSV File:", self.csv_path, self.browse_csv)
        # Folder Input
        self.create_input_group(main_frame, "Save Music To:", self.output_path, self.browse_folder)

        # Status & Progress
        self.status_label = tk.Label(self.root, text="Ready to sync", font=("Montserrat", 10),
                                    fg="#A8D5BA", bg="#1e1e1e", pady=10)
        self.status_label.pack()
        
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=500, mode="determinate", style="TProgressbar")
        self.progress.pack(pady=5)

        # Download Button
        self.download_btn = tk.Button(self.root, text="START CONVERSION", font=("Montserrat", 12, "bold"),
                                    bg="#D4AF37", fg="#2D3436", width=25, height=2, 
                                    activebackground="#E8B4B8", cursor="hand2",
                                    command=self.start_download_thread)
        self.download_btn.pack(pady=30)

    def create_input_group(self, parent, label_text, var, command):
        group = tk.Frame(parent, bg="#1e1e1e", pady=10)
        group.pack(fill='x')
        tk.Label(group, text=label_text, fg="#FFF5F5", bg="#1e1e1e", font=("Montserrat", 9)).pack(anchor='w')
        
        entry_frame = tk.Frame(group, bg="#2d3436")
        entry_frame.pack(fill='x', pady=5)
        
        tk.Entry(entry_frame, textvariable=var, bg="#2d3436", fg="white", insertbackground="white", 
                 font=("Montserrat", 10), bd=0).pack(side='left', fill='x', expand=True, padx=10, ipady=8)
        
        tk.Button(entry_frame, text="Browse", command=command, bg="#A8D5BA", fg="#2D3436",
                  relief="flat", font=("Montserrat", 8, "bold"), padx=15).pack(side='right')

    def browse_csv(self):
        file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file: self.csv_path.set(file)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder: self.output_path.set(folder)

    def start_download_thread(self):
        if not self.csv_path.get() or not self.output_path.get():
            messagebox.showwarning("Missing Info", "Please select both the CSV file and destination folder.")
            return
        
        if self.is_downloading: return
        
        self.is_downloading = True
        self.download_btn.config(state='disabled', text="PROCESSING...")
        threading.Thread(target=self.process_tracks, daemon=True).start()

    def process_tracks(self):
        try:
            df = pd.read_csv(self.csv_path.get())
            
            # Identify columns dynamically
            name_col = next((c for c in df.columns if 'Track Name' in c), None)
            artist_col = next((c for c in df.columns if 'Artist Name' in c), None)

            if not name_col or not artist_col:
                messagebox.showerror("Format Error", "CSV must contain 'Track Name' and 'Artist Name' columns.")
                return

            tracks = df[[name_col, artist_col]].dropna().values.tolist()
            total = len(tracks)
            self.progress["maximum"] = total

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{self.output_path.get()}/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }

            for i, (name, artist) in enumerate(tracks):
                self.status_label.config(text=f"Searching: {name} by {artist}")
                search_query = f"ytsearch1:{name} {artist}"
                
                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([search_query])
                except Exception as e:
                    print(f"Skipping {name}: {e}")

                self.progress["value"] = i + 1
                self.root.update_idletasks()

            messagebox.showinfo("Complete", f"Successfully processed {total} tracks!")
            
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        finally:
            self.is_downloading = False
            self.download_btn.config(state='normal', text="START CONVERSION")
            self.status_label.config(text="Ready")
            self.progress["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = ExportifyDownloader(root)
    root.mainloop()