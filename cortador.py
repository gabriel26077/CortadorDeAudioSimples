import tkinter as tk
from tkinter import filedialog, messagebox
import librosa
import librosa.display
import matplotlib.pyplot as plt
import numpy as np
import os
import soundfile as sf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AudioCutterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Cutter")
        
        # Garantir encerramento completo ao fechar
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.audio_data = None
        self.sr = None
        self.filepath = None
        self.cut_points = []
        self.click_count = 0
        self.temp_points = []
        
        # Interface layout
        self.load_button = tk.Button(root, text="Carregar Áudio", command=self.load_audio)
        self.load_button.pack(pady=10)
        
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack()
        self.canvas.mpl_connect("button_press_event", self.on_click)
        
        self.cut_button = tk.Button(root, text="Cortar Áudio", command=self.cut_audio)
        self.cut_button.pack(pady=10)
    
    def on_close(self):
        # Mensagem de confirmação (opcional)
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            self.root.destroy()  # Fecha a janela principal
            exit()
    
    def load_audio(self):
        initial_dir = os.path.dirname(os.path.abspath(__file__))
        self.filepath = filedialog.askopenfilename(
            initialdir=initial_dir, 
            filetypes=[("Audio Files", "*.wav *.mp3")]
        )
        if not self.filepath:
            return
        
        try:
            self.audio_data, self.sr = librosa.load(self.filepath, sr=None)
            self.plot_waveform()
            self.cut_points = []
            self.temp_points = []
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar o áudio: {e}")
    
    def plot_waveform(self):
        self.ax.clear()
        librosa.display.waveshow(self.audio_data, sr=self.sr, ax=self.ax)
        self.ax.set_title("Forma de Onda do Áudio")
        self.ax.set_xlabel("Tempo (s)")
        self.ax.set_ylabel("Amplitude")
        self.canvas.draw()
    
    def on_click(self, event):
        if self.audio_data is None:
            return
        
        time = event.xdata
        if time is None:
            return
        
        if self.click_count % 2 == 0:
            self.temp_points.append(time)
            self.ax.scatter(time, 0, color="blue", label="Início" if self.click_count == 0 else "", zorder=5)
        else:
            self.temp_points.append(time)
            self.ax.scatter(time, 0, color="red", label="Fim" if self.click_count == 1 else "", zorder=5)
            self.cut_points.append((min(self.temp_points), max(self.temp_points)))
            self.temp_points = []
        
        self.click_count += 1
        self.ax.legend()
        self.canvas.draw()
    
    def cut_audio(self):
        if not self.cut_points:
            messagebox.showwarning("Aviso", "Nenhum ponto de corte definido.")
            return
        
        output_dir = os.path.join(os.path.dirname(self.filepath), "cortes")
        os.makedirs(output_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(self.filepath))[0]
        
        for i, (start, end) in enumerate(self.cut_points):
            start_sample = int(start * self.sr)
            end_sample = int(end * self.sr)
            cut_audio = self.audio_data[start_sample:end_sample]
            
            output_path = os.path.join(output_dir, f"{base_name}_corte_{i + 1}.wav")
            try:
                sf.write(output_path, cut_audio, self.sr)
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar o áudio cortado: {e}")
                return
        
        messagebox.showinfo("Sucesso", f"Áudios cortados salvos em: {output_dir}")

# Inicializar a aplicação
root = tk.Tk()
app = AudioCutterApp(root)
root.mainloop()
