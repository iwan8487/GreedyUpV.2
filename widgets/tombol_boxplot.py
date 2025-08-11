import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from widgets.utils import parse_input_data, mark_and_interpolate_spikes, upscaling_log2

def tombol_boxplot(frame_buttons, text_input, entry_threshold, entry_min_len, entry_max_len, entry_logdiff, entry_neighbors):
    def plot_boxplot():
        try:
            df_input = parse_input_data(text_input.get("1.0", tk.END))
            if df_input.empty:
                messagebox.showerror("Error", "Data input tidak valid.")
                return
            threshold_error = float(entry_threshold.get())
            min_len = int(entry_min_len.get())
            max_len = int(entry_max_len.get())
            log_diff_thresh = float(entry_logdiff.get())
            min_neighbors = int(entry_neighbors.get())

            df_up = mark_and_interpolate_spikes(df_input, log_diff_thresh, min_neighbors)
            df_up, _ = upscaling_log2(df_up, threshold_error, min_len, max_len)

            # Gabungkan berdasarkan MD (pastikan urutan sama)
            df_merged = df_input.copy()
            df_merged['K_upscaled'] = df_up['K_upscaled']

            # Hitung selisih log10
            diff_log10 = np.log10(df_merged['K']) - np.log10(df_merged['K_upscaled'])
            rms = np.sqrt(np.mean(diff_log10**2))

            # Simpan ke Excel
            df_merged['log10K_input'] = np.log10(df_merged['K'])
            df_merged['log10K_upscaled'] = np.log10(df_merged['K_upscaled'])
            df_merged['diff_log10'] = diff_log10
            df_merged['RMS'] = rms
            df_merged.to_excel("output_boxplot.xlsx", index=False)

            fig, ax = plt.subplots(figsize=(5, 6))
            ax.boxplot(diff_log10, vert=True, patch_artist=True, boxprops=dict(facecolor='lightblue'))
            ax.set_ylabel("log10(K_input) - log10(K_upscaled)")
            ax.set_title("Boxplot Selisih log10(K) Input vs Upscale")
            ax.text(1.1, np.median(diff_log10), f"RMS = {rms:.4f}", fontsize=12, color='red', va='center')
            plt.tight_layout()
            plt.show()

            messagebox.showinfo("Selesai", "Data boxplot dan RMS telah disimpan ke 'output_boxplot.xlsx'")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat boxplot:\n{e}")

    tk.Button(frame_buttons, text="Boxplot Selisih & RMS", command=plot_boxplot, font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky="ew")