import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import tkinter.messagebox as messagebox
import json
import os

# Veri kaydetme ve yükleme fonksiyonları
def save_data():
    data = {
        'start_date': start_datetime_entry.get_datetime().strftime("%d.%m.%Y %H:%M"),
        'end_date': end_datetime_entry.get_datetime().strftime("%d.%m.%Y %H:%M"),
        'remaining_mb': entry_remaining_mb.get(),
        'total_gb': entry_total_gb.get()
    }
    try:
        with open('internet_data.json', 'w') as f:
            json.dump(data, f)
    except Exception as e:
        messagebox.showerror("Hata", "Veriler kaydedilirken hata oluştu!")

def load_data():
    try:
        if os.path.exists('internet_data.json'):
            with open('internet_data.json', 'r') as f:
                data = json.load(f)
                
                # Tarihleri ayarla
                start_date = datetime.strptime(data['start_date'], "%d.%m.%Y %H:%M")
                end_date = datetime.strptime(data['end_date'], "%d.%m.%Y %H:%M")
                start_datetime_entry.set_datetime(start_date)
                end_datetime_entry.set_datetime(end_date)
                
                # MB ve GB değerlerini ayarla
                entry_remaining_mb.delete(0, tk.END)
                entry_remaining_mb.insert(0, data['remaining_mb'])
                entry_total_gb.delete(0, tk.END)
                entry_total_gb.insert(0, data['total_gb'])
                
                # Hesaplamaları güncelle
                calculate()
    except Exception as e:
        pass  # İlk kez çalıştırılıyorsa veya dosya yoksa sessizce devam et

class TimeEntry(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Saat girişi
        self.hour_var = tk.StringVar(value="00")
        self.minute_var = tk.StringVar(value="00")
        
        # Saat spinbox
        self.hour_spinbox = ttk.Spinbox(
            self, from_=0, to=23, width=2,
            format="%02.0f",
            textvariable=self.hour_var,
            wrap=True
        )
        self.hour_spinbox.pack(side=tk.LEFT)
        
        tk.Label(self, text=":").pack(side=tk.LEFT)
        
        # Dakika spinbox
        self.minute_spinbox = ttk.Spinbox(
            self, from_=0, to=59, width=2,
            format="%02.0f",
            textvariable=self.minute_var,
            wrap=True
        )
        self.minute_spinbox.pack(side=tk.LEFT)
    
    def get_time(self):
        return f"{self.hour_var.get()}:{self.minute_var.get()}"

    def set_time(self, time_str):
        hour, minute = time_str.split(":")
        self.hour_var.set(hour)
        self.minute_var.set(minute)

class DateTimeEntry(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Tarih seçici
        self.date_picker = DateEntry(self, width=12, background='darkblue',
                                   foreground='white', borderwidth=2,
                                   date_pattern='dd.mm.yyyy')
        self.date_picker.pack(side=tk.LEFT, padx=5)
        
        # Zaman girişi
        self.time_entry = TimeEntry(self)
        self.time_entry.pack(side=tk.LEFT, padx=5)
    
    def get_datetime(self):
        date_str = self.date_picker.get()
        time_str = self.time_entry.get_time()
        return datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")

    def set_datetime(self, dt):
        self.date_picker.set_date(dt)
        self.time_entry.set_time(dt.strftime("%H:%M"))

def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    days = total_seconds // (24 * 3600)
    remaining = total_seconds % (24 * 3600)
    hours = remaining // 3600
    remaining = remaining % 3600
    minutes = remaining // 60
    seconds = remaining % 60
    return f"{days}:{hours:02d}:{minutes:02d}:{seconds:02d}"

def calculate():
    try:
        start_date = start_datetime_entry.get_datetime()
        end_date = end_datetime_entry.get_datetime()
        remaining_mb = float(entry_remaining_mb.get())
        total_gb = float(entry_total_gb.get())
        
        # Verileri kaydet
        save_data()
        
        # Toplam gün hesaplama
        total_days = (end_date - start_date).total_seconds() / (24 * 3600)
        
        # Toplam MB ve günlük ortalama MB
        total_mb = total_gb * 1024
        daily_mb = total_mb / total_days
        
        # Geçen süre (gün + saat + dakika + saniye olarak)
        time_passed = datetime.now() - start_date
        days_passed = time_passed.total_seconds() / (24 * 3600)
        
        # Kullanılan MB
        used_mb = total_mb - remaining_mb
        
        # Kâr hesaplama (MB)
        profit_mb = (daily_mb * days_passed) - used_mb
        
        # Kâr (Gün olarak)
        profit_days = profit_mb / daily_mb
        
        # Kalan süre
        time_remaining = end_date - datetime.now()
        remaining_days = time_remaining.total_seconds() / (24 * 3600)
        
        # Günlük sınır (Kalan MB/Kalan gün)
        daily_limit = remaining_mb / remaining_days if remaining_days > 0 else 0
        
        update_labels()
        
    except ValueError as e:
        messagebox.showerror("Hata", "Lütfen tüm alanları doğru formatta doldurun.")

def update_labels():
    try:
        start_date = start_datetime_entry.get_datetime()
        end_date = end_datetime_entry.get_datetime()
        remaining_mb = float(entry_remaining_mb.get())
        total_gb = float(entry_total_gb.get())
        
        total_days = (end_date - start_date).total_seconds() / (24 * 3600)
        total_mb = total_gb * 1024
        daily_mb = total_mb / total_days
        
        time_passed = datetime.now() - start_date
        days_passed = time_passed.total_seconds() / (24 * 3600)
        
        used_mb = total_mb - remaining_mb
        profit_mb = (daily_mb * time_passed.total_seconds() / (24 * 3600)) - used_mb
        profit_timedelta = timedelta(days=profit_mb / daily_mb)
        
        # Ortalama indirme hesaplama
        average_download = used_mb / days_passed if days_passed > 0 else 0
        
        time_remaining = end_date - datetime.now()
        remaining_days = time_remaining.total_seconds() / (24 * 3600)
        daily_limit = remaining_mb / remaining_days if remaining_days > 0 else 0
        
        label_total_days.config(text=f"Toplam Gün: {total_days:.2f}")
        label_daily_mb.config(text=f"Toplam Güne Göre (MB): {daily_mb:.2f}")
        label_average_download.config(text=f"Ortalama İndirme (MB/Gün): {average_download:.2f}")
        label_profit_mb.config(text=f"Kâr (MB): {profit_mb:.2f}")
        label_profit_days.config(text=f"Kâr (Gün): {format_timedelta(profit_timedelta)}")
        label_daily_limit.config(text=f"Sınır (MB/Gün): {daily_limit:.2f}")
        label_time_passed.config(text=f"Geçen Süre: {format_timedelta(time_passed)}")
        label_time_remaining.config(text=f"Kalan Süre: {format_timedelta(time_remaining)}")
        
        root.after(1000, update_labels)  # Her saniye güncelle
        
    except ValueError:
        pass

# Arayüz tasarımı
root = tk.Tk()
root.title("Mobil İnternet Hesaplama")
root.geometry("600x550")  # Pencere boyutunu biraz büyüttüm

# Başlangıç ve Bitiş tarihleri
tk.Label(root, text="Başlangıç:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
start_datetime_entry = DateTimeEntry(root)
start_datetime_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Bitiş:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
end_datetime_entry = DateTimeEntry(root)
end_datetime_entry.grid(row=1, column=1, padx=10, pady=5)

# Kalan MB ve Toplam GB
tk.Label(root, text="Kalan MB:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_remaining_mb = tk.Entry(root)
entry_remaining_mb.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Toplam GB:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_total_gb = tk.Entry(root)
entry_total_gb.grid(row=3, column=1, padx=10, pady=5)

# Sonuçlar
label_total_days = tk.Label(root, text="Toplam Gün: --", font=("Arial", 12))
label_total_days.grid(row=4, column=0, columnspan=2, pady=10, sticky="w")

label_daily_mb = tk.Label(root, text="Toplam Güne Göre (MB): --", font=("Arial", 12))
label_daily_mb.grid(row=5, column=0, columnspan=2, pady=10, sticky="w")

label_average_download = tk.Label(root, text="Ortalama İndirme (MB/Gün): --", font=("Arial", 12), fg="orange")
label_average_download.grid(row=6, column=0, columnspan=2, pady=10, sticky="w")

label_profit_mb = tk.Label(root, text="Kâr (MB): --", font=("Arial", 12), fg="green")
label_profit_mb.grid(row=7, column=0, columnspan=2, pady=10, sticky="w")

label_profit_days = tk.Label(root, text="Kâr (Gün): --", font=("Arial", 12), fg="blue")
label_profit_days.grid(row=8, column=0, columnspan=2, pady=10, sticky="w")

label_daily_limit = tk.Label(root, text="Sınır (MB/Gün): --", font=("Arial", 12), fg="purple")
label_daily_limit.grid(row=9, column=0, columnspan=2, pady=10, sticky="w")

label_time_passed = tk.Label(root, text="Geçen Süre: --", font=("Arial", 12))
label_time_passed.grid(row=10, column=0, columnspan=2, pady=10, sticky="w")

label_time_remaining = tk.Label(root, text="Kalan Süre: --", font=("Arial", 12))
label_time_remaining.grid(row=11, column=0, columnspan=2, pady=10, sticky="w")

# Hesaplama butonu
button_calculate = ttk.Button(root, text="Hesapla", command=calculate)
button_calculate.grid(row=12, column=0, columnspan=2, pady=20)

# Pencere kapanırken verileri kaydet
def on_closing():
    try:
        save_data()
    except:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Program başladığında verileri yükle
load_data()

root.mainloop()
