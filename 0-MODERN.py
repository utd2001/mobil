import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry
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
        messagebox.showerror("Hata", f"Veriler kaydedilirken hata oluştu!\n{e}")

def load_data():
    try:
        if os.path.exists('internet_data.json'):
            with open('internet_data.json', 'r') as f:
                data = json.load(f)
                start_date = datetime.strptime(data['start_date'], "%d.%m.%Y %H:%M")
                end_date = datetime.strptime(data['end_date'], "%d.%m.%Y %H:%M")
                start_datetime_entry.set_datetime(start_date)
                end_datetime_entry.set_datetime(end_date)
                entry_remaining_mb.delete(0, tk.END)
                entry_remaining_mb.insert(0, data['remaining_mb'])
                entry_total_gb.delete(0, tk.END)
                entry_total_gb.insert(0, data['total_gb'])
                entry_target_profit.delete(0, tk.END)
                entry_target_profit.insert(0, data['target_profit'])
                entry_target_limit.delete(0, tk.END)
                entry_target_limit.insert(0, data['target_limit'])
                calculate()
    except Exception as e:
        messagebox.showerror("Hata", f"Veriler yüklenirken hata oluştu!\n{e}")

class DateTimeEntry(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.date_picker = DateEntry(
            self, width=12, background='#404040', foreground='white', borderwidth=2,
            date_pattern='dd.mm.yyyy', selectbackground='#606060', selectforeground='white',
            normalbackground='#404040', normalforeground='white', headersbackground='#404040',
            headersforeground='white'
        )
        self.date_picker.pack(side=tk.LEFT, padx=5)
        self.hour_var = tk.StringVar(value="00")
        self.minute_var = tk.StringVar(value="00")
        self.hour_spinbox = ttk.Spinbox(self, from_=0, to=23, textvariable=self.hour_var, width=3)
        self.hour_spinbox.pack(side=tk.LEFT, padx=2)
        tk.Label(self, text=":", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        self.minute_spinbox = ttk.Spinbox(self, from_=0, to=59, textvariable=self.minute_var, width=3)
        self.minute_spinbox.pack(side=tk.LEFT, padx=2)

    def get_datetime(self):
        date_str = self.date_picker.get()
        time_str = f"{self.hour_var.get()}:{self.minute_var.get()}"
        return datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")

    def set_datetime(self, dt):
        self.date_picker.set_date(dt)
        self.hour_var.set(dt.strftime("%H"))
        self.minute_var.set(dt.strftime("%M"))

def calculate():
    try:
        start_date = start_datetime_entry.get_datetime()
        end_date = end_datetime_entry.get_datetime()
        remaining_mb = float(entry_remaining_mb.get())
        total_gb = float(entry_total_gb.get())
        target_profit = float(entry_target_profit.get())
        target_limit = float(entry_target_limit.get())

        total_mb = total_gb * 1024
        used_mb = total_mb - remaining_mb
        now = datetime.now()
        elapsed_days = (now - start_date).total_seconds() / (24 * 3600)
        total_days = (end_date - start_date).total_seconds() / (24 * 3600)
        daily_mb = total_mb / total_days
        profit_mb = (daily_mb * elapsed_days) - used_mb
        remaining_days = (end_date - now).total_seconds() / (24 * 3600)
        daily_limit = remaining_mb / remaining_days if remaining_days > 0 else 0

        label_total_days.config(text=f"Toplam Gün: {total_days:.2f}")
        label_daily_mb.config(text=f"Günlük MB: {daily_mb:.2f}")
        label_profit_mb.config(text=f"Kâr MB: {profit_mb:.2f}")
        label_daily_limit.config(text=f"Günlük Limit: {daily_limit:.2f}")

        if profit_mb >= target_profit:
            label_status.config(text="Hedef kâr gerçekleşti!", foreground="green")
        else:
            label_status.config(text="Hedef kâr gerçekleşmedi.", foreground="red")

        if daily_limit >= target_limit:
            label_limit_status.config(text="Hedef limit karşılanıyor!", foreground="green")
        else:
            label_limit_status.config(text="Hedef limit karşılanmıyor.", foreground="red")
    except ValueError:
        messagebox.showerror("Hata", "Lütfen tüm alanları doğru doldurun.")

# Arayüz tasarımı
root = tk.Tk()
root.title("Mobil İnternet Hesaplama")
root.configure(bg='#2b2b2b')

# Koyu tema
style = ttk.Style()
style.configure('.', background='#2b2b2b', foreground='white')

# Veri giriş alanları
frame_data = ttk.LabelFrame(root, text="Veri Girişi")
frame_data.pack(padx=10, pady=5, fill='x')

ttk.Label(frame_data, text="Kalan MB:").pack(side='left', padx=5, pady=5)
entry_remaining_mb = ttk.Entry(frame_data)
entry_remaining_mb.pack(side='left', padx=5, pady=5)

ttk.Label(frame_data, text="Toplam GB:").pack(side='left', padx=5, pady=5)
entry_total_gb = ttk.Entry(frame_data)
entry_total_gb.pack(side='left', padx=5, pady=5)

ttk.Label(frame_data, text="Başlangıç Tarihi:").pack(side='left', padx=5, pady=5)
start_datetime_entry = DateTimeEntry(frame_data)
start_datetime_entry.pack(side='left', padx=5)

ttk.Label(frame_data, text="Bitiş Tarihi:").pack(side='left', padx=5, pady=5)
end_datetime_entry = DateTimeEntry(frame_data)
end_datetime_entry.pack(side='left', padx=5)

ttk.Label(frame_data, text="Hedef Kâr (MB):").pack(side='left', padx=5, pady=5)
entry_target_profit = ttk.Entry(frame_data)
entry_target_profit.pack(side='left', padx=5, pady=5)

ttk.Label(frame_data, text="Hedef Günlük Limit (MB):").pack(side='left', padx=5, pady=5)
entry_target_limit = ttk.Entry(frame_data)
entry_target_limit.pack(side='left', padx=5, pady=5)

# Bilgi ve sonuç alanları
frame_info = ttk.LabelFrame(root, text="Bilgiler")
frame_info.pack(padx=10, pady=5, fill='x')

label_total_days = ttk.Label(frame_info, text="Toplam Gün: --")
label_total_days.pack(pady=5)
label_daily_mb = ttk.Label(frame_info, text="Günlük MB: --")
label_daily_mb.pack(pady=5)
label_profit_mb = ttk.Label(frame_info, text="Kâr MB: --")
label_profit_mb.pack(pady=5)
label_daily_limit = ttk.Label(frame_info, text="Günlük Limit: --")
label_daily_limit.pack(pady=5)

label_status = ttk.Label(frame_info, text="Hedef Durumu: --")
label_status.pack(pady=5)
label_limit_status = ttk.Label(frame_info, text="Limit Durumu: --")
label_limit_status.pack(pady=5)

# Hesaplama ve veri yönetimi butonları
button_calculate = ttk.Button(root, text="Hesapla", command=calculate)
button_calculate.pack(pady=10)

button_save = ttk.Button(root, text="Kaydet", command=save_data)
button_save.pack(side='left', padx=10, pady=10)

button_load = ttk.Button(root, text="Yükle", command=load_data)
button_load.pack(side='right', padx=10, pady=10)

# Önceden kaydedilmiş verileri yükle
load_data()
root.mainloop()
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
        self.configure(bg='#2b2b2b')
        
        # Saat girişi
        self.hour_var = tk.StringVar(value="00")
        self.minute_var = tk.StringVar(value="00")
        
        # Saat spinbox
        self.hour_spinbox = ttk.Spinbox(
            self, from_=0, to=23, width=2,
            format="%02.0f",
            textvariable=self.hour_var,
            wrap=True,
            style='Dark.TSpinbox'
        )
        self.hour_spinbox.pack(side=tk.LEFT)
        
        tk.Label(self, text=":", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        
        # Dakika spinbox
        self.minute_spinbox = ttk.Spinbox(
            self, from_=0, to=59, width=2,
            format="%02.0f",
            textvariable=self.minute_var,
            wrap=True,
            style='Dark.TSpinbox'
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
        self.configure(bg='#2b2b2b')
        
        # Tarih seçici
        self.date_picker = DateEntry(
            self, width=12,
            background='#404040',
            foreground='white',
            borderwidth=2,
            date_pattern='dd.mm.yyyy',
            selectbackground='#606060',
            selectforeground='white',
            normalbackground='#404040',
            normalforeground='white',
            headersbackground='#404040',
            headersforeground='white'
        )
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
                overage_text = "Aşım Yok"
            else:
                overage_text = f"{overage_date.strftime('%d.%m.%Y\n%H:%M:%S')}"
        else:
            overage_text = "--"
        
        time_remaining = end_date - now
        remaining_days = time_remaining.total_seconds() / (24 * 3600)
        daily_limit = remaining_mb / remaining_days if remaining_days > 0 else 0
        
        # Genel bilgiler sekmesindeki frame'leri güncelle
        info_labels = [
            f"{format_timedelta(timedelta(days=total_days))}",
            f"{daily_mb:.2f} MB",
            f"{average_download:.2f} MB",
            f"{profit_mb:.2f} MB",
            overage_text,
            f"{daily_limit:.2f} MB"
        ]
        
        for i, frame in enumerate(general_tab.winfo_children()):
            if isinstance(frame, ttk.LabelFrame):
                for label in frame.winfo_children():
                    if isinstance(label, ttk.Label):
                        label.configure(text=info_labels[i])
        
        # Hedef bilgilerini güncelle
        try:
            target_profit_mb = float(entry_target_profit.get())
            days_for_target_profit = (target_profit_mb - profit_mb) / daily_mb
            target_profit_date = now + timedelta(days=days_for_target_profit)
            label_days_for_profit.configure(
                text=f"{format_timedelta(timedelta(days=days_for_target_profit))}\n"
                     f"{target_profit_date.strftime('%d.%m.%Y %H:%M:%S')}"
            )
        except:
            label_days_for_profit.configure(text="--")
        
        try:
            target_limit_mb = float(entry_target_limit.get())
            days_for_target_limit = remaining_days - (remaining_mb / target_limit_mb)
            target_limit_date = now + timedelta(days=days_for_target_limit)
            label_days_for_limit.configure(
                text=f"{format_timedelta(timedelta(days=days_for_target_limit))}\n"
                     f"{target_limit_date.strftime('%d.%m.%Y %H:%M:%S')}"
            )
        except:
            label_days_for_limit.configure(text="--")
        
        root.after(100, update_labels)  # Her 100ms'de güncelle
        
    except ValueError:
        pass

# Arayüz tasarımı
root = tk.Tk()
root.title("Mobil İnternet Hesaplama")
root.geometry("800x750")

# Koyu tema ayarları
style = ttk.Style()
style.theme_use('clam')
style.configure('.', background='#2b2b2b', foreground='white')
style.configure('TFrame', background='#2b2b2b')
style.configure('TLabel', background='#2b2b2b', foreground='white')
style.configure('TButton', background='#404040', foreground='white')
style.configure('TNotebook', background='#2b2b2b', foreground='white')
style.configure('TNotebook.Tab', background='#404040', foreground='white', padding=[10, 2])
style.configure('TLabelframe', background='#2b2b2b', foreground='white')
style.configure('TLabelframe.Label', background='#2b2b2b', foreground='white')
style.configure('TEntry', 
               fieldbackground='#404040', 
               foreground='white',
               insertcolor='white')
style.configure('Dark.TSpinbox',
               fieldbackground='#404040',
               foreground='white',
               selectbackground='#606060',
               selectforeground='white')
style.map('TNotebook.Tab',
          background=[('selected', '#606060')],
          foreground=[('selected', 'white')])

root.configure(bg='#2b2b2b')

# Veri giriş frame'i
data_frame = ttk.LabelFrame(root, text="Veri Girişi")
data_frame.pack(fill='x', padx=10, pady=5)

# MB ve GB giriş frame'i
mb_gb_frame = ttk.Frame(data_frame)
mb_gb_frame.pack(fill='x', padx=5, pady=5)

remaining_frame = ttk.LabelFrame(mb_gb_frame, text="Kalan MB")
remaining_frame.pack(side='left', padx=5, fill='x', expand=True)
entry_remaining_mb = ttk.Entry(remaining_frame)
entry_remaining_mb.pack(padx=5, pady=5)

total_frame = ttk.LabelFrame(mb_gb_frame, text="Toplam GB")
total_frame.pack(side='left', padx=5, fill='x', expand=True)
entry_total_gb = ttk.Entry(total_frame)
entry_total_gb.pack(padx=5, pady=5)

# Tarih seçimi frame
date_frame = ttk.Frame(data_frame)
date_frame.pack(fill='x', padx=5, pady=5)

# Başlangıç ve bitiş tarihleri için frame'ler
start_frame = ttk.LabelFrame(date_frame, text="Başlangıç")
start_frame.pack(side='left', padx=5, fill='x', expand=True)
start_datetime_entry = DateTimeEntry(start_frame)
start_datetime_entry.pack(padx=5, pady=5)

end_frame = ttk.LabelFrame(date_frame, text="Bitiş")
end_frame.pack(side='left', padx=5, fill='x', expand=True)
end_datetime_entry = DateTimeEntry(end_frame)
end_datetime_entry.pack(padx=5, pady=5)

# Ana notebook (sekmeler) oluşturma
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=5)

# Genel bilgiler sekmesi
general_tab = ttk.Frame(notebook)
notebook.add(general_tab, text='Genel Bilgiler')

# Frame başlıkları
frame_titles = [
    "Toplam Süre", "Günlük Ortalama", "Ortalama İndirme",
    "Kâr Durumu", "Aşım Durumu", "Günlük Limit"
]

# 3x2 grid için frame'ler
for i in range(2):
    for j in range(3):
        idx = i * 3 + j
        frame = ttk.LabelFrame(general_tab, text=frame_titles[idx])
        frame.grid(row=i, column=j, padx=5, pady=5, sticky='nsew')
        # Frame'in minimum boyutunu ayarla
        frame.grid_propagate(False)
        frame.configure(width=200, height=150)
        # Label'ı frame'in ortasına yerleştir
        label = ttk.Label(frame, text="--", style='InfoLabel.TLabel')
        label.place(relx=0.5, rely=0.5, anchor='center')

# Grid yapılandırması
for i in range(2):
    general_tab.grid_rowconfigure(i, weight=1)
for j in range(3):
    general_tab.grid_columnconfigure(j, weight=1)

# Hedefler sekmesi
targets_tab = ttk.Frame(notebook)
notebook.add(targets_tab, text='Hedefler')

# Hedef ve sınır giriş frame'leri
input_frame = ttk.Frame(targets_tab)
input_frame.pack(fill='x', padx=5, pady=5)

target_frame = ttk.LabelFrame(input_frame, text="Hedef (MB)")
target_frame.pack(side='left', padx=5, fill='x', expand=True)
entry_target_profit = ttk.Entry(target_frame)
entry_target_profit.pack(padx=5, pady=5)

limit_frame = ttk.LabelFrame(input_frame, text="Sınır (MB/Gün)")
limit_frame.pack(side='left', padx=5, fill='x', expand=True)
entry_target_limit = ttk.Entry(limit_frame)
entry_target_limit.pack(padx=5, pady=5)

# Hedef ve sınır bilgi frame'leri
target_info_frame = ttk.Frame(targets_tab)
target_info_frame.pack(fill='both', expand=True, padx=5, pady=5)

# Hedef sayaç ve tarih frame'i
target_counter_frame = ttk.LabelFrame(target_info_frame, text="Hedefe Ulaşmak İçin")
target_counter_frame.pack(fill='x', padx=5, pady=5)
label_days_for_profit = ttk.Label(target_counter_frame, text="--", style='InfoLabel.TLabel')
label_days_for_profit.pack(padx=5, pady=15)

# Sınır sayaç ve tarih frame'i
limit_counter_frame = ttk.LabelFrame(target_info_frame, text="Sınıra Ulaşmak İçin")
limit_counter_frame.pack(fill='x', padx=5, pady=5)
label_days_for_limit = ttk.Label(limit_counter_frame, text="--", style='InfoLabel.TLabel')
label_days_for_limit.pack(padx=5, pady=15)

# Hesaplama butonu
button_calculate = ttk.Button(root, text="Hesapla", command=calculate)
button_calculate.pack(pady=10)

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

# Label stilleri için yeni konfigürasyon
style.configure('InfoLabel.TLabel', 
               font=('Arial', 16, 'bold'), 
               background='#2b2b2b', 
               foreground='white',
               anchor='center',
               justify='center')

root.mainloop()