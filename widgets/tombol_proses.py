import tkinter as tk
from tkinter import messagebox
from widgets.utils import parse_input_data, mark_and_interpolate_spikes, upscaling_log2_improved
import matplotlib.pyplot as plt
import numpy as np

def tombol_proses(frame_buttons, text_input, entry_threshold, entry_min_len, entry_max_len, entry_logdiff, entry_neighbors):
    def on_submit():
        try:
            threshold_error = float(entry_threshold.get())
            min_len = int(entry_min_len.get())
            max_len = int(entry_max_len.get())
            log_diff_thresh = float(entry_logdiff.get())
            min_neighbors = int(entry_neighbors.get())  # Sekarang digunakan!
            
            df = parse_input_data(text_input.get("1.0", tk.END))
            if df.empty:
                messagebox.showerror("Error", "Data tidak valid.")
                return
            
            # Proses spike detection
            df = mark_and_interpolate_spikes(df, log_diff_thresh, min_neighbors)
            
            # Upscaling dengan parameter min_neighbors yang berpengaruh
            df, zona_hasil = upscaling_log2_improved(df, threshold_error, min_len, max_len, min_neighbors)
            
            # Simpan hasil
            df.to_excel("output.xlsx", index=False)
            messagebox.showinfo("Selesai", 
                f"""Data disimpan ke 'output.xlsx'
Jumlah zona hasil: {zona_hasil}
Threshold Error: {threshold_error}
Min Neighbors: {min_neighbors}
Min Length: {min_len}
Max Length: {max_len}""")

            # Plot hasil dengan zona 1 warna
            fig, ax = plt.subplots(figsize=(10, 12))
            df = df.sort_values("MD").reset_index(drop=True)
            
            # Plot K original
            ax.semilogx(df['K'], df['MD'], label='K Original', color='blue', 
                       linestyle='-', linewidth=1, alpha=0.8)

            # Plot zona upscaling dengan 1 warna (merah)
            zones = df['Zone'].unique()
            
            for i, zone in enumerate(zones):
                zone_data = df[df['Zone'] == zone]
                md_top = zone_data['MD'].min()
                md_bot = zone_data['MD'].max()
                k_val = zone_data['K_upscaled'].iloc[0]
                
                # Fill zona dengan warna merah yang sama untuk semua zona
                if i == 0:
                    ax.fill_betweenx([md_top, md_bot], 1e-3, k_val, 
                                   color='red', alpha=0.3, 
                                   label='Upscale Zone')
                else:
                    ax.fill_betweenx([md_top, md_bot], 1e-3, k_val, 
                                   color='red', alpha=0.3)

            ax.invert_yaxis()
            ax.set_xlabel("Permeability (mD) - Log Scale", fontsize=16)
            ax.set_ylabel("Measured Depth (MD)", fontsize=16)
            ax.set_title(f"""Upscaling Result
Threshold: {threshold_error} | Min Neighbors: {min_neighbors}
Min Len: {min_len} | Max Len: {max_len} | Zones: {zona_hasil}""", fontsize=12)
            ax.tick_params(axis='both', which='major', labelsize=14)
            ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
            ax.legend(loc="upper right", fontsize=12)
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
    
    # Buat tombol
    btn = tk.Button(frame_buttons, text="Proses dan Plot Data", command=on_submit, 
                   font=("Arial", 12))
    btn.grid(row=3, column=0, pady=5, sticky="ew")

def plot_data_zonasi(df_up):
    # Pastikan df_up sudah berisi kolom 'MD' dan 'K_upscaled'
    data_x = df_up['MD']
    data_y = df_up['K_upscaled']

    # Filter data valid
    mask = (data_y > 0) & np.isfinite(data_y)
    data_x = data_x[mask]
    data_y = data_y[mask]

    # Tentukan batas log min dan max dengan margin 10%
    y_min = data_y.min()
    y_max = data_y.max()
    log_min = 10 ** (np.log10(y_min) - 0.1)
    log_max = 10 ** (np.log10(y_max) + 0.1)

    plt.figure(figsize=(8,5))
    plt.plot(data_x, data_y, marker='o', linestyle='-', label='Upscaled')
    plt.yscale('log')
    plt.ylim(log_min, log_max)
    plt.xlabel('MD', fontsize=16)
    plt.ylabel('K Upscaled', fontsize=16)
    plt.title('Plot Zonasi K Upscaled', fontsize=18)
    plt.tick_params(axis='both', which='major', labelsize=14)
    plt.tick_params(axis='both', which='minor', labelsize=12)
    plt.grid(True, which='both', ls='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()