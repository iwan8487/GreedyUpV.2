import tkinter as tk
from tkinter import messagebox
import pandas as pd
from math import gcd
from functools import reduce

def tombol_copyrasio(frame_buttons):
    def copy_ratios_to_clipboard():
        try:
            df = pd.read_excel("output.xlsx")
            df = df.sort_values("MD").reset_index(drop=True)
            zone_thicknesses = df.groupby("Zone")["MD"].apply(lambda x: x.max() - x.min()).tolist()
            cm_thicknesses = [int(round(t * 100)) for t in zone_thicknesses]
            gcd_val = reduce(gcd, cm_thicknesses)
            ratios = [round(t * 100 / gcd_val) for t in zone_thicknesses]
            ratio_text = ",".join(str(r) for r in ratios)
            frame_buttons.clipboard_clear()
            frame_buttons.clipboard_append(ratio_text)
            messagebox.showinfo("Disalin", f"Rasio ketebalan zona disalin ke clipboard:\n{ratio_text}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyalin rasio: {e}")
    
    tk.Button(frame_buttons, text="Salin Rasio Zona", command=copy_ratios_to_clipboard, font=("Arial", 12)).grid(row=2, column=0, pady=5, sticky="ew")