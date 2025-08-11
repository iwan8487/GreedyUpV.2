import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
from widgets.utils import parse_input_data, mark_and_interpolate_spikes, upscaling_log2_improved

def tombol_histogram(parent, text_input, entry_threshold, entry_min_len, entry_max_len, entry_logdiff, entry_neighbors, entry_binwidth):
    def plot_histogram():
        try:
            # --- Ambil dan proses data input ---
            df_input = parse_input_data(text_input.get("1.0", tk.END))
            if df_input.empty:
                messagebox.showerror("Error", "Data input tidak valid.")
                return
            threshold_error = float(entry_threshold.get())
            min_len = int(entry_min_len.get())
            max_len = int(entry_max_len.get())
            log_diff_thresh = float(entry_logdiff.get())
            min_neighbors = int(entry_neighbors.get())  # Sekarang digunakan!
            bin_width = float(entry_binwidth.get())
            if bin_width <= 0:
                messagebox.showerror("Error", "Lebar kelas histogram harus > 0.")
                return

            # --- Proses upscaling ---
            df_up = mark_and_interpolate_spikes(df_input, log_diff_thresh, min_neighbors)
            df_up, _ = upscaling_log2_improved(df_up, threshold_error, min_len, max_len, min_neighbors)

            # --- FILTERING DATA ---
            df_valid = df_up.dropna(subset=['K', 'K_upscaled'])
            df_valid = df_valid[(df_valid['K'] > 0) & (df_valid['K_upscaled'] > 0)]
            mask = np.isfinite(df_valid['K']) & np.isfinite(df_valid['K_upscaled'])
            df_valid = df_valid[mask]

            data_input_log = np.log10(df_valid['K'].values)
            data_up_log = np.log10(df_valid['K_upscaled'].values)

            if len(data_input_log) == 0 or len(data_up_log) == 0 or len(data_input_log) != len(data_up_log):
                messagebox.showerror("Error", "Tidak ada data valid untuk histogram dan korelasi.\n"
                                              "Periksa apakah data K dan K_upscaled bernilai positif dan tidak kosong.")
                return

            # --- Plot: Histogram komparasi & Scatter korelasi ---
            min_val = min(data_input_log.min(), data_up_log.min())
            max_val = max(data_input_log.max(), data_up_log.max())
            bins = np.arange(np.floor(min_val), np.ceil(max_val) + bin_width, bin_width)
            bin_centers = (bins[:-1] + bins[1:]) / 2
            width = bin_width * 0.4

            fig, axs = plt.subplots(2, 1, figsize=(8, 10))

            # Histogram komparasi input vs upscaled
            counts_input, _ = np.histogram(data_input_log, bins=bins)
            counts_up, _ = np.histogram(data_up_log, bins=bins)
            axs[0].bar(bin_centers - width/2, counts_input, width=width, color='skyblue', edgecolor='black', alpha=0.7, label='Input (log10 K)')
            axs[0].bar(bin_centers + width/2, counts_up, width=width, color='salmon', edgecolor='black', alpha=0.7, label='Upscaling (log10 K)')
            axs[0].set_title("Histogram Data Input & Upscaling (log10 K)", fontsize=14)
            axs[0].set_xlabel("log10(K)", fontsize=12)
            axs[0].set_ylabel("Frekuensi", fontsize=12)
            axs[0].legend()
            axs[0].grid(True, alpha=0.3)

            # Scatter plot + garis korelasi
            axs[1].scatter(data_input_log, data_up_log, alpha=0.7, color='blue', s=30)
            if len(data_input_log) > 1:
                slope, intercept, r_value, _, _ = linregress(data_input_log, data_up_log)
                reg_x = np.array([data_input_log.min(), data_input_log.max()])
                reg_y = slope * reg_x + intercept
                axs[1].plot(reg_x, reg_y, color='red', linewidth=2, label=f"Regresi Linier (r={r_value:.3f})")
                
                # Garis 1:1
                min_xy = min(data_input_log.min(), data_up_log.min())
                max_xy = max(data_input_log.max(), data_up_log.max())
                axs[1].plot([min_xy, max_xy], [min_xy, max_xy], 'k--', alpha=0.7, label='Garis 1:1')
                
                axs[1].legend()
                axs[1].text(0.05, 0.95, f"Pearson r = {r_value:.3f}", transform=axs[1].transAxes, fontsize=12, verticalalignment='top')
            else:
                axs[1].text(0.05, 0.95, "Data tidak cukup untuk korelasi", transform=axs[1].transAxes, fontsize=12, verticalalignment='top')

            axs[1].set_xlabel("log10(K Input)", fontsize=12)
            axs[1].set_ylabel("log10(K Upscaled)", fontsize=12)
            axs[1].set_title("Scatter Plot log10(K Input) vs log10(K Upscaled)", fontsize=14)
            axs[1].grid(True, alpha=0.3)

            plt.tight_layout()
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat histogram:\n{e}")

    # Tombol di GUI
    btn = tk.Button(parent, text="Histogram & Korelasi", command=plot_histogram, font=("Arial", 12))
    btn.grid(row=0, column=0, sticky="ew", pady=5)