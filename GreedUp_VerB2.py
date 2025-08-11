import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "widgets"))

import tkinter as tk
from tkinter import scrolledtext
from widgets.tombol_proses import tombol_proses
from widgets.tombol_histogram import tombol_histogram
from widgets.tombol_copyrasio import tombol_copyrasio
from widgets.tombol_boxplot import tombol_boxplot
from widgets.tombol_r2 import tombol_r2
from widgets.utils import upscaling_log2_improved
import numpy as np
import pandas as pd

# Hapus atau komentari baris ini jika tidak perlu
# df_up = pd.read_csv('your_data_file.csv')

# --- Fungsi untuk memproses dan memvalidasi data ---
def proses_data(data_input, threshold_error, min_len, max_len, threshold_spike, jumlah_tetangga):
    # ...fungsi yang ada sebelumnya...
    pass

def run_app():
    root = tk.Tk()
    root.title("GreedUp - Upscaling Permeabilitas Multi Parameter")
    root.geometry("1200x700")

    main_frame = tk.Frame(root, padx=10, pady=10)
    main_frame.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Area input data
    tk.Label(main_frame, text="Paste Data MD dan K:", font=("Arial", 12)).grid(row=0, column=0, sticky="w")
    text_input = scrolledtext.ScrolledText(main_frame, width=80, height=10, font=("Courier New", 12))
    text_input.grid(row=1, column=0, padx=0, pady=5, sticky="nsew")

    # Area parameter
    param_frame = tk.Frame(main_frame, bd=2, relief="groove")
    param_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
    param_frame.columnconfigure(1, weight=1)
    row_idx = 0

    tk.Label(param_frame, text="Parameter Upscaling", font=("Arial", 13, "bold")).grid(row=row_idx, column=0, columnspan=2, pady=(0,5))
    row_idx += 1

    entry_threshold = tk.Entry(param_frame, font=("Arial", 12)); entry_threshold.insert(0, "1")
    tk.Label(param_frame, text="Threshold Error Zona:", font=("Arial", 12)).grid(row=row_idx, column=0, sticky="w")
    entry_threshold.grid(row=row_idx, column=1, sticky="ew"); row_idx += 1

    entry_min_len = tk.Entry(param_frame, font=("Arial", 12)); entry_min_len.insert(0, "2")
    tk.Label(param_frame, text="Minimal Data per Zona:", font=("Arial", 12)).grid(row=row_idx, column=0, sticky="w")
    entry_min_len.grid(row=row_idx, column=1, sticky="ew"); row_idx += 1

    entry_max_len = tk.Entry(param_frame, font=("Arial", 12)); entry_max_len.insert(0, "6")
    tk.Label(param_frame, text="Maksimal Data per Zona:", font=("Arial", 12)).grid(row=row_idx, column=0, sticky="w")
    entry_max_len.grid(row=row_idx, column=1, sticky="ew"); row_idx += 1

    entry_logdiff = tk.Entry(param_frame, font=("Arial", 12)); entry_logdiff.insert(0, "2.0")
    tk.Label(param_frame, text="Threshold Spike (log2):", font=("Arial", 12)).grid(row=row_idx, column=0, sticky="w")
    entry_logdiff.grid(row=row_idx, column=1, sticky="ew"); row_idx += 1

    entry_neighbors = tk.Entry(param_frame, font=("Arial", 12)); entry_neighbors.insert(0, "1")
    tk.Label(param_frame, text="Jumlah Tetangga Minimal:", font=("Arial", 12)).grid(row=row_idx, column=0, sticky="w")
    entry_neighbors.grid(row=row_idx, column=1, sticky="ew"); row_idx += 1

    entry_binwidth = tk.Entry(param_frame, font=("Arial", 12)); entry_binwidth.insert(0, "0.2")
    tk.Label(param_frame, text="Lebar Kelas Histogram:", font=("Arial", 12)).grid(row=row_idx, column=0, sticky="w")
    entry_binwidth.grid(row=row_idx, column=1, sticky="ew"); row_idx += 1

    # Area tombol-tombol
    button_frame = tk.Frame(main_frame)
    button_frame.grid(row=3, column=0, pady=10, sticky="ew")
    button_frame.columnconfigure(0, weight=1)

    tombol_histogram(button_frame, text_input, entry_threshold, entry_min_len, entry_max_len, entry_logdiff, entry_neighbors, entry_binwidth)
    tombol_boxplot(button_frame, text_input, entry_threshold, entry_min_len, entry_max_len, entry_logdiff, entry_neighbors)
    tombol_copyrasio(button_frame)  # Hanya berikan parent frame seperti kode lama
    tombol_proses(button_frame, text_input, entry_threshold, entry_min_len, entry_max_len, entry_logdiff, entry_neighbors)
    tombol_r2(button_frame, text_input, entry_threshold, entry_min_len, entry_max_len, entry_logdiff, entry_neighbors)

    root.mainloop()

if __name__ == "__main__":
    run_app()