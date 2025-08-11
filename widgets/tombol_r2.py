import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr
from widgets.utils import parse_input_data, mark_and_interpolate_spikes, upscaling_log2

def hitung_koefisien_determinan(data_input, data_upscale):
    """
    Menghitung koefisien determinan (R²) antara data input dan data upscale
    """
    # Filter data valid (tidak NaN dan > 0)
    mask = (~np.isnan(data_input)) & (~np.isnan(data_upscale)) & (data_input > 0) & (data_upscale > 0)
    x = data_input[mask]
    y = data_upscale[mask]
    
    if len(x) < 2:
        return 0.0, 0.0
    
    # Hitung korelasi Pearson
    r, p_value = pearsonr(x, y)
    
    # R² = r²
    r2 = r**2
    
    return r2, r

def hitung_statistik_perbandingan(data_input, data_upscale):
    """
    Menghitung berbagai statistik perbandingan antara data input dan upscale
    """
    # Filter data valid
    mask = (~np.isnan(data_input)) & (~np.isnan(data_upscale)) & (data_input > 0) & (data_upscale > 0)
    x = data_input[mask]
    y = data_upscale[mask]
    
    if len(x) < 2:
        return {}
    
    # Hitung R² dan korelasi
    r2, r = hitung_koefisien_determinan(data_input, data_upscale)
    
    # Hitung RMSE (Root Mean Square Error)
    rmse = np.sqrt(np.mean((x - y)**2))
    
    # Hitung MAE (Mean Absolute Error)
    mae = np.mean(np.abs(x - y))
    
    # Hitung MAPE (Mean Absolute Percentage Error)
    mape = np.mean(np.abs((x - y) / x)) * 100
    
    stats = {
        'R²': r2,
        'Korelasi (r)': r,
        'RMSE': rmse,
        'MAE': mae,
        'MAPE (%)': mape,
        'Jumlah data': len(x)
    }
    
    return stats

def tombol_r2(parent, text_input, entry_threshold, entry_min_len, entry_max_len, entry_logdiff, entry_neighbors):
    def plot_r2_analysis():
        try:
            # Ambil parameter
            threshold_error = float(entry_threshold.get())
            min_len = int(entry_min_len.get())
            max_len = int(entry_max_len.get())
            log_diff_thresh = float(entry_logdiff.get())
            min_neighbors = int(entry_neighbors.get())
            
            # Parse dan proses data
            df = parse_input_data(text_input.get("1.0", tk.END))
            if df.empty:
                messagebox.showerror("Error", "Data tidak valid.")
                return
            
            df = mark_and_interpolate_spikes(df, log_diff_thresh, min_neighbors)
            df, zona_hasil = upscaling_log2(df, threshold_error, min_len, max_len)
            
            # Hitung statistik perbandingan
            stats = hitung_statistik_perbandingan(df['K'].values, df['K_upscaled'].values)
            
            if not stats:
                messagebox.showerror("Error", "Tidak cukup data valid untuk analisis.")
                return
            
            # Plot scatter plot dengan garis 1:1
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Scatter plot linear
            mask = (~np.isnan(df['K'])) & (~np.isnan(df['K_upscaled'])) & (df['K'] > 0) & (df['K_upscaled'] > 0)
            x_data = df['K'][mask]
            y_data = df['K_upscaled'][mask]
            
            ax1.scatter(x_data, y_data, alpha=0.6, color='blue', s=30)
            
            # Garis 1:1 (ideal)
            min_val = min(x_data.min(), y_data.min())
            max_val = max(x_data.max(), y_data.max())
            ax1.plot([min_val, max_val], [min_val, max_val], 'r--', label='Garis 1:1 (Ideal)', linewidth=2)
            
            # Garis regresi
            z = np.polyfit(x_data, y_data, 1)
            p = np.poly1d(z)
            ax1.plot(x_data, p(x_data), 'g-', label=f'Regresi Linear', linewidth=2)
            
            ax1.set_xlabel('K Input (mD)', fontsize=14)
            ax1.set_ylabel('K Upscaled (mD)', fontsize=14)
            ax1.set_title(f'Perbandingan K Input vs K Upscaled\nR² = {stats["R²"]:.4f}', fontsize=16)
            ax1.tick_params(axis='both', which='major', labelsize=12)
            ax1.legend(fontsize=12)
            ax1.grid(True, alpha=0.3)
            
            # Scatter plot log
            ax2.scatter(x_data, y_data, alpha=0.6, color='blue', s=30)
            ax2.plot([min_val, max_val], [min_val, max_val], 'r--', label='Garis 1:1 (Ideal)', linewidth=2)
            ax2.plot(x_data, p(x_data), 'g-', label=f'Regresi Linear', linewidth=2)
            
            ax2.set_xscale('log')
            ax2.set_yscale('log')
            ax2.set_xlabel('K Input (mD) - Log Scale', fontsize=14)
            ax2.set_ylabel('K Upscaled (mD) - Log Scale', fontsize=14)
            ax2.set_title(f'Perbandingan K Input vs K Upscaled (Log)\nKorelasi (r) = {stats["Korelasi (r)"]:.4f}', fontsize=16)
            ax2.tick_params(axis='both', which='major', labelsize=12)
            ax2.legend(fontsize=12)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
            # Tampilkan statistik dalam messagebox
            stats_text = f"""Statistik Perbandingan Data Input vs Upscaled:
            
R² (Koefisien Determinan): {stats['R²']:.4f}
Korelasi Pearson (r): {stats['Korelasi (r)']:.4f}
RMSE: {stats['RMSE']:.4f}
MAE: {stats['MAE']:.4f}
MAPE: {stats['MAPE (%)']:.2f}%
Jumlah data valid: {stats['Jumlah data']}

Interpretasi R²:
- R² > 0.9: Korelasi sangat kuat
- 0.7 < R² ≤ 0.9: Korelasi kuat  
- 0.5 < R² ≤ 0.7: Korelasi sedang
- R² ≤ 0.5: Korelasi lemah"""
            
            messagebox.showinfo("Statistik R² dan Korelasi", stats_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Terjadi kesalahan: {str(e)}")
    
    # Buat tombol
    btn = tk.Button(parent, text="Analisis R² & Korelasi", command=plot_r2_analysis, font=("Arial", 12))
    btn.grid(row=4, column=0, sticky="ew", pady=5)