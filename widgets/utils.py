import pandas as pd
import numpy as np
from math import gcd
from functools import reduce
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.image as mpimg
import base64
from io import BytesIO
from PIL import Image

# Logo base64 string (isi sesuai kebutuhan Anda, atau import dari file lain)
logo_base64 = ""  # <- isi jika ingin logo, atau biarkan kosong

def calculate_error(log2_vals, mean_log2):
    return np.sum((log2_vals - mean_log2) ** 2)

def mark_and_interpolate_spikes(df, log_diff_threshold=2.0, min_neighbors=1):
    df = df.copy()
    df['log2K'] = np.log2(df['K'])
    is_spike = []
    for i in range(len(df)):
        val = df.loc[i, 'log2K']
        neighbors = []
        if i > 0:
            neighbors.append(df.loc[i - 1, 'log2K'])
        if i < len(df) - 1:
            neighbors.append(df.loc[i + 1, 'log2K'])
        diff_ok = [abs(val - n) <= log_diff_threshold for n in neighbors]
        is_spike.append(sum(diff_ok) < min_neighbors)
    df['is_spike'] = is_spike

    # Interpolasi data spike
    df['K_edited'] = df['K']
    for i in range(len(df)):
        if df.loc[i, 'is_spike']:
            if i > 0 and i < len(df) - 1:
                df.loc[i, 'K_edited'] = (df.loc[i - 1, 'K'] + df.loc[i + 1, 'K']) / 2
            elif i > 0:
                df.loc[i, 'K_edited'] = df.loc[i - 1, 'K']
            elif i < len(df) - 1:
                df.loc[i, 'K_edited'] = df.loc[i + 1, 'K']
    return df

def upscaling_log2(df, threshold_error, min_len, max_len):
    df = df.sort_values("MD").reset_index(drop=True)
    df['Zone'] = -1
    df['log2K_edited'] = np.log2(df['K_edited'])
    zone_id = 0
    i = 0
    while i < len(df):
        max_window = min(max_len, len(df) - i)
        found = False
        while max_window >= min_len:
            window_data = df.iloc[i:i+max_window]
            core_data = window_data[~window_data['is_spike']]
            if len(core_data) < min_len:
                max_window -= 1
                continue
            log2_vals = core_data['log2K_edited'].values
            mean_log2 = log2_vals.mean()
            error = calculate_error(log2_vals, mean_log2)
            if error <= threshold_error:
                df.loc[i:i+max_window-1, 'Zone'] = zone_id
                zone_id += 1
                i += max_window
                found = True
                break
            else:
                max_window -= 1
        if not found:
            df.loc[i:i+min_len-1, 'Zone'] = zone_id
            zone_id += 1
            i += min_len
    df['K_upscaled'] = df.groupby('Zone')['log2K_edited'].transform(lambda x: 2 ** x.mean())
    return df, df['Zone'].nunique()

def parse_input_data(text):
    lines = text.strip().split('\n')
    md_vals = []
    k_vals = []
    for line in lines:
        parts = line.strip().replace(',', '.').split()
        if len(parts) != 2:
            continue
        try:
            md = float(parts[0])
            k = float(parts[1])
            md_vals.append(md)
            k_vals.append(k)
        except ValueError:
            continue
    return pd.DataFrame({'MD': md_vals, 'K': k_vals})

def plot_data(df, frame_plot):
    # Bersihkan canvas sebelumnya
    for widget in frame_plot.winfo_children():
        widget.destroy()

    fig, ax = plt.subplots(figsize=(10, 14))
    df = df.sort_values("MD").reset_index(drop=True)

    # Plot data asli
    ax.semilogx(df['K'], df['MD'], label='K Original', color='blue', linestyle='-', linewidth=1, alpha=0.6)
    # Plot data yang telah diedit
    ax.semilogx(df['K_edited'], df['MD'], label='K Edited', color='black', linestyle='-', linewidth=1.5)

    ax.invert_yaxis()
    ax.set_xlabel("Permeability (mD) - Log Scale")
    ax.set_ylabel("Measured Depth (MD)")
    ax.set_title("Permeability vs Depth")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Plot zona
    zones = df['Zone'].unique()
    zone_thicknesses = df.groupby("Zone")["MD"].apply(lambda x: x.max() - x.min()).tolist()
    cm_thicknesses = [int(round(t * 100)) for t in zone_thicknesses]
    if cm_thicknesses and all(cm_thicknesses):
        gcd_val = reduce(gcd, cm_thicknesses)
        ratios = [round(t * 100 / gcd_val) for t in zone_thicknesses]
        ratio_text = ", ".join(map(str, ratios))
    else:
        ratios = []
        ratio_text = ""

    for i, zone in enumerate(zones):
        zone_data = df[df['Zone'] == zone]
        md_top = zone_data['MD'].min()
        md_bot = zone_data['MD'].max()
        k_val = zone_data['K_upscaled'].iloc[0]
        md_mid = (md_top + md_bot) / 2
        ax.fill_betweenx([md_top, md_bot], 1e-3, k_val, color='red', alpha=0.3)
        ax.text(k_val * 1.1, md_mid, f"{md_bot - md_top:.2f}", va='center', fontsize=8, color='darkred')
        if ratios:
            ax.text(ax.get_xlim()[1] * 0.8, md_mid, f"{ratios[i]}", va='center', fontsize=9, color='black')

    ax.set_xlabel(f"Permeability (mD) - Log Scale\nRasio Zona: {ratio_text}")

    # Tambahkan logo jika ada
    if logo_base64.strip():
        try:
            logo_data = base64.b64decode(logo_base64)
            logo_image = Image.open(BytesIO(logo_data))
            logo_image.save("temp_logo.png")
            logo = mpimg.imread("temp_logo.png")
            fig.figimage(logo, xo=fig.bbox.xmax - 250, yo=fig.bbox.ymin + 180, zorder=10, alpha=0.8)
        except Exception:
            pass

    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

def upscaling_log2_improved(df, threshold_error, min_len, max_len, min_neighbors=1):
    """
    Upscaling yang diperbaiki dengan parameter min_neighbors yang berpengaruh
    """
    return upscaling_adaptif_tetangga(df, threshold_error, min_len, max_len, min_neighbors)

def upscaling_dengan_similarity(df, threshold_error, min_len, max_len, similarity_threshold=0.5):
    """
    Upscaling dengan mempertimbangkan similarity antar titik data
    """
    df = df.copy()
    df = df.sort_values('MD').reset_index(drop=True)
    
    zones = []
    zone_id = 1
    i = 0
    
    while i < len(df):
        current_zone = [i]
        j = i + 1
        
        while j < len(df) and len(current_zone) < max_len:
            # Hitung similarity dengan zona saat ini
            current_k = df.loc[current_zone, 'K'].values
            new_k = df.loc[j, 'K']
            
            # Similarity berdasarkan log difference
            log_current_mean = np.mean(np.log10(current_k))
            log_new = np.log10(new_k)
            log_diff = abs(log_current_mean - log_new)
            
            # Check similarity dan error threshold
            if log_diff <= similarity_threshold:
                # Cek error threshold
                all_k = np.append(current_k, new_k)
                log_all = np.log10(all_k)
                error = np.std(log_all) / np.abs(np.mean(log_all)) if np.mean(log_all) != 0 else float('inf')
                
                if error <= threshold_error:
                    current_zone.append(j)
                    j += 1
                else:
                    break
            else:
                break
        
        # Pastikan zona memenuhi min_len
        while len(current_zone) < min_len and j < len(df):
            current_zone.append(j)
            j += 1
        
        # Assign zone
        for idx in current_zone:
            zones.append(zone_id)
        
        zone_id += 1
        i = j
    
    df['Zone'] = zones
    df['K_upscaled'] = df.groupby('Zone')['K'].transform('mean')
    
    return df, len(df['Zone'].unique())

def upscaling_dengan_tetangga(df, threshold_error, min_len, max_len, min_neighbors=1):
    """
    Upscaling dengan mempertimbangkan jumlah tetangga minimal
    min_neighbors: jumlah titik tetangga yang harus memiliki nilai K serupa
    """
    df = df.copy()
    df = df.sort_values('MD').reset_index(drop=True)
    
    zones = []
    zone_id = 1
    i = 0
    
    while i < len(df):
        current_zone = [i]
        base_k = df.loc[i, 'K']
        base_log_k = np.log10(base_k)
        
        # Cari tetangga yang serupa
        j = i + 1
        similar_neighbors = 0
        
        while j < len(df) and len(current_zone) < max_len:
            current_k = df.loc[j, 'K']
            current_log_k = np.log10(current_k)
            
            # Hitung similarity dengan titik base
            log_diff = abs(base_log_k - current_log_k)
            
            # Jika serupa, tambahkan sebagai tetangga
            if log_diff <= threshold_error:
                similar_neighbors += 1
                current_zone.append(j)
                
                # Update base K dengan rata-rata zona
                zone_k_values = df.loc[current_zone, 'K'].values
                base_k = np.mean(zone_k_values)
                base_log_k = np.log10(base_k)
                
                j += 1
            else:
                # Jika tidak serupa, cek apakah sudah cukup tetangga
                if similar_neighbors >= min_neighbors and len(current_zone) >= min_len:
                    break  # Zona sudah cukup
                else:
                    # Paksa tambahkan untuk memenuhi min_neighbors atau min_len
                    current_zone.append(j)
                    j += 1
        
        # Pastikan zona memenuhi min_len
        while len(current_zone) < min_len and j < len(df):
            current_zone.append(j)
            j += 1
        
        # Assign zone
        for idx in current_zone:
            zones.append(zone_id)
        
        zone_id += 1
        i = j
    
    df['Zone'] = zones
    df['K_upscaled'] = df.groupby('Zone')['K'].transform('mean')
    
    return df, len(df['Zone'].unique())

def upscaling_adaptif_tetangga(df, threshold_error, min_len, max_len, min_neighbors=1):
    """
    Algoritma upscaling adaptif yang mempertimbangkan kemiripan tetangga
    """
    df = df.copy()
    df = df.sort_values('MD').reset_index(drop=True)
    
    zones = []
    zone_id = 1
    i = 0
    
    while i < len(df):
        current_zone = [i]
        
        # Mulai dari titik ke-i, cari tetangga yang serupa
        j = i + 1
        neighbors_found = 0
        
        while j < len(df) and len(current_zone) < max_len:
            # Hitung K rata-rata zona saat ini
            current_k_values = df.loc[current_zone, 'K'].values
            current_mean_k = np.mean(current_k_values)
            
            # K dari titik kandidat
            candidate_k = df.loc[j, 'K']
            
            # Hitung error jika kandidat ditambahkan
            potential_k_values = np.append(current_k_values, candidate_k)
            potential_std = np.std(np.log10(potential_k_values))
            potential_mean = np.mean(np.log10(potential_k_values))
            relative_error = potential_std / abs(potential_mean) if potential_mean != 0 else float('inf')
            
            # Cek apakah kandidat dapat ditambahkan
            if relative_error <= threshold_error:
                current_zone.append(j)
                neighbors_found += 1
                j += 1
            else:
                # Jika tidak memenuhi threshold, cek kondisi stopping
                if neighbors_found >= min_neighbors and len(current_zone) >= min_len:
                    break  # Zona sudah memenuhi syarat
                elif len(current_zone) < min_len:
                    # Paksa tambahkan untuk memenuhi min_len
                    current_zone.append(j)
                    j += 1
                else:
                    break
        
        # Pastikan zona memenuhi min_len
        while len(current_zone) < min_len and j < len(df):
            current_zone.append(j)
            j += 1
        
        # Assign zone ID
        for idx in current_zone:
            zones.append(zone_id)
        
        zone_id += 1
        i = j
    
    df['Zone'] = zones
    df['K_upscaled'] = df.groupby('Zone')['K'].transform('mean')
    
    return df, len(df['Zone'].unique())