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
        'total_gb': entry_total_gb.get(),
        'target_profit': entry_target_profit.get(),
        'target_limit': entry_target_limit.get()
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
                
                # Hedef değerleri ayarla
                if 'target_profit' in data:
                    entry_target_profit.delete(0, tk.END)
                    entry_target_profit.insert(0, data['target_profit'])
                if 'target_limit' in data:
                    entry_target_limit.delete(0, tk.END)
                    entry_target_limit.insert(0, data['target_limit'])
                
                # Hesaplamaları güncelle
                calculate()
    except Exception as e:
        pass

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
    # Negatif süreleri pozitife çevir ama işareti sakla
    is_negative = td.total_seconds() < 0
    td = abs(td)
    
    total_seconds = int(td.total_seconds())
    days = total_seconds // (24 * 3600)
    remaining = total_seconds % (24 * 3600)
    hours = remaining // 3600
    remaining = remaining % 3600
    minutes = remaining // 60
    seconds = remaining % 60
    
    # İşareti ekle
    sign = "-" if is_negative else ""
    return f"{sign}{days}:{hours:02d}:{minutes:02d}:{seconds:02d}"

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
        now = datetime.now()
        
        total_days = (end_date - start_date).total_seconds() / (24 * 3600)
        total_mb = total_gb * 1024
        daily_mb = total_mb / total_days
        
        time_passed = now - start_date
        days_passed = time_passed.total_seconds() / (24 * 3600)
        
        used_mb = total_mb - remaining_mb
        profit_mb = (daily_mb * time_passed.total_seconds() / (24 * 3600)) - used_mb
        profit_timedelta = timedelta(days=profit_mb / daily_mb)
        
        # Ortalama indirme hesaplama
        average_download = used_mb / days_passed if days_passed > 0 else 0
        
        # Olası aşım tarihi (ortalama indirmeye göre)
        if average_download > 0:
            days_until_overage = remaining_mb / average_download
            overage_date = now + timedelta(days=days_until_overage)
            if overage_date > end_date:
                label_overage_date.config(
                    text=f"Olası Aşım Tarihi: {overage_date.strftime('%d.%m.%Y %H:%M:%S')}\n"
                         f"Bitiş Tarihi: {end_date.strftime('%d.%m.%Y %H:%M:%S')}\n"
                         f"(Kotayı aşmayacaksınız)",
                    fg="green"
                )
            else:
                label_overage_date.config(
                    text=f"Olası Aşım Tarihi: {overage_date.strftime('%d.%m.%Y %H:%M:%S')}\n"
                         f"Bitiş Tarihi: {end_date.strftime('%d.%m.%Y %H:%M:%S')}\n"
                         f"(Dikkat: Kota aşılacak!)",
                    fg="red"
                )
        else:
            label_overage_date.config(
                text=f"Olası Aşım Tarihi: --\n"
                     f"Bitiş Tarihi: {end_date.strftime('%d.%m.%Y %H:%M:%S')}\n"
                     f"(Henüz veri kullanımı yok)",
                fg="gray"
            )
        
        time_remaining = end_date - now
        remaining_days = time_remaining.total_seconds() / (24 * 3600)
        daily_limit = remaining_mb / remaining_days if remaining_days > 0 else 0
        
        # Hedef kâr için gereken gün ve tarih hesaplama
        try:
            target_profit_mb = float(entry_target_profit.get())
            days_for_target_profit = (target_profit_mb - profit_mb) / daily_mb
            target_profit_date = now + timedelta(days=days_for_target_profit)
            label_days_for_profit.config(
                text=f"Hedef Kâr İçin: {format_timedelta(timedelta(days=days_for_target_profit))}\n"
                     f"Hedef Kâr Tarihi: {target_profit_date.strftime('%d.%m.%Y %H:%M:%S')}"
            )
        except:
            label_days_for_profit.config(text="Hedef Kâr İçin: --\nHedef Kâr Tarihi: --")
        
        # Hedef sınır için gereken gün ve tarih hesaplama
        try:
            target_limit_mb = float(entry_target_limit.get())
            days_for_target_limit = remaining_days - (remaining_mb / target_limit_mb)
            target_limit_date = now + timedelta(days=days_for_target_limit)
            label_days_for_limit.config(
                text=f"Hedef Sınır İçin: {format_timedelta(timedelta(days=days_for_target_limit))}\n"
                     f"Hedef Sınır Tarihi: {target_limit_date.strftime('%d.%m.%Y %H:%M:%S')}"
            )
        except:
            label_days_for_limit.config(text="Hedef Sınır İçin: --\nHedef Sınır Tarihi: --")
        
        # Diğer labelları güncelle
        label_total_days.config(text=f"Toplam Gün: {format_timedelta(timedelta(days=total_days))}")
        label_daily_mb.config(text=f"Toplam Güne Göre (MB): {daily_mb}")
        label_average_download.config(text=f"Ortalama İndirme (MB/Gün): {average_download}")
        label_profit_mb.config(text=f"Kâr (MB): {profit_mb}")
        label_profit_days.config(text=f"Kâr (Gün): {format_timedelta(profit_timedelta)}")
        label_daily_limit.config(text=f"Sınır (MB/Gün): {daily_limit}")
        label_time_passed.config(text=f"Geçen Süre: {format_timedelta(time_passed)}")
        label_time_remaining.config(text=f"Kalan Süre: {format_timedelta(time_remaining)}")
        
        root.after(100, update_labels)  # Her 100ms'de güncelle
        
    except ValueError:
        pass

# Arayüz tasarımı
root = tk.Tk()
root.title("Mobil İnternet Hesaplama")
root.geometry("800x750")  # Pencereyi daha geniş yaptım

# Grid sütun ayarları
root.grid_columnconfigure(1, weight=1, minsize=200)  # Entry'lerin olduğu sütunu sabit genişlikte tut

# Başlangıç ve Bitiş tarihleri
frame_dates = ttk.Frame(root)
frame_dates.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
frame_dates.grid_columnconfigure(1, weight=1, minsize=200)

tk.Label(frame_dates, text="Başlangıç:").grid(row=0, column=0, sticky="w", pady=5)
start_datetime_entry = DateTimeEntry(frame_dates)
start_datetime_entry.grid(row=0, column=1, sticky="w")

tk.Label(frame_dates, text="Bitiş:").grid(row=1, column=0, sticky="w", pady=5)
end_datetime_entry = DateTimeEntry(frame_dates)
end_datetime_entry.grid(row=1, column=1, sticky="w")

# Değerler için frame
frame_values = ttk.Frame(root)
frame_values.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
frame_values.grid_columnconfigure(1, weight=1, minsize=200)

# Kalan MB ve Toplam GB
tk.Label(frame_values, text="Kalan MB:").grid(row=0, column=0, sticky="w", pady=5)
entry_remaining_mb = tk.Entry(frame_values, width=30)
entry_remaining_mb.grid(row=0, column=1, sticky="w")

tk.Label(frame_values, text="Toplam GB:").grid(row=1, column=0, sticky="w", pady=5)
entry_total_gb = tk.Entry(frame_values, width=30)
entry_total_gb.grid(row=1, column=1, sticky="w")

# Hedef değerler için giriş alanları
tk.Label(frame_values, text="Hedef Kâr (MB):").grid(row=2, column=0, sticky="w", pady=5)
entry_target_profit = tk.Entry(frame_values, width=30)
entry_target_profit.grid(row=2, column=1, sticky="w")

tk.Label(frame_values, text="Hedef Sınır (MB/Gün):").grid(row=3, column=0, sticky="w", pady=5)
entry_target_limit = tk.Entry(frame_values, width=30)
entry_target_limit.grid(row=3, column=1, sticky="w")

# Sonuçlar için frame
frame_results = ttk.Frame(root)
frame_results.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

# Sonuçlar (önceki labellar aynı)
label_total_days = tk.Label(frame_results, text="Toplam Gün: --", font=("Arial", 12))
label_total_days.pack(anchor="w", pady=5)

label_daily_mb = tk.Label(frame_results, text="Toplam Güne Göre (MB): --", font=("Arial", 12))
label_daily_mb.pack(anchor="w", pady=5)

label_average_download = tk.Label(frame_results, text="Ortalama İndirme (MB/Gün): --", font=("Arial", 12), fg="orange")
label_average_download.pack(anchor="w", pady=5)

# Olası aşım tarihi
label_overage_date = tk.Label(frame_results, text="Olası Aşım Tarihi: --\n(Henüz veri kullanımı yok)", font=("Arial", 12), fg="gray")
label_overage_date.pack(anchor="w", pady=5)

label_profit_mb = tk.Label(frame_results, text="Kâr (MB): --", font=("Arial", 12), fg="green")
label_profit_mb.pack(anchor="w", pady=5)

label_profit_days = tk.Label(frame_results, text="Kâr (Gün): --", font=("Arial", 12), fg="blue")
label_profit_days.pack(anchor="w", pady=5)

label_daily_limit = tk.Label(frame_results, text="Sınır (MB/Gün): --", font=("Arial", 12), fg="purple")
label_daily_limit.pack(anchor="w", pady=5)

# Hedef hesaplama sonuçları
label_days_for_profit = tk.Label(frame_results, text="Hedef Kâr İçin: --\nHedef Kâr Tarihi: --", font=("Arial", 12), fg="red")
label_days_for_profit.pack(anchor="w", pady=5)

label_days_for_limit = tk.Label(frame_results, text="Hedef Sınır İçin: --\nHedef Sınır Tarihi: --", font=("Arial", 12), fg="red")
label_days_for_limit.pack(anchor="w", pady=5)

label_time_passed = tk.Label(frame_results, text="Geçen Süre: --", font=("Arial", 12))
label_time_passed.pack(anchor="w", pady=5)

label_time_remaining = tk.Label(frame_results, text="Kalan Süre: --", font=("Arial", 12))
label_time_remaining.pack(anchor="w", pady=5)

# Hesaplama butonu
button_calculate = ttk.Button(root, text="Hesapla", command=calculate)
button_calculate.grid(row=3, column=0, columnspan=2, pady=20)

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
