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
        'target_limit': entry_target_limit.get(),
        'unit': unit_var.get()
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
                
                start_date = datetime.strptime(data['start_date'], "%d.%m.%Y %H:%M")
                end_date = datetime.strptime(data['end_date'], "%d.%m.%Y %H:%M")
                
                start_datetime_entry.date_picker.delete(0, tk.END)
                start_datetime_entry.date_picker.insert(0, start_date.strftime("%d.%m.%Y"))
                start_datetime_entry.time_entry.set_time(start_date.strftime("%H:%M"))
                
                end_datetime_entry.date_picker.delete(0, tk.END)
                end_datetime_entry.date_picker.insert(0, end_date.strftime("%d.%m.%Y"))
                end_datetime_entry.time_entry.set_time(end_date.strftime("%H:%M"))
                
                entry_remaining_mb.delete(0, tk.END)
                entry_remaining_mb.insert(0, data['remaining_mb'])
                entry_total_gb.delete(0, tk.END)
                entry_total_gb.insert(0, data['total_gb'])
                
                if 'target_profit' in data:
                    entry_target_profit.delete(0, tk.END)
                    entry_target_profit.insert(0, data['target_profit'])
                if 'target_limit' in data:
                    entry_target_limit.delete(0, tk.END)
                    entry_target_limit.insert(0, data['target_limit'])
                
                if 'unit' in data:
                    unit_var.set(data['unit'])
                
                calculate()
    except Exception as e:
        pass

class TimeEntry(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg='#2b2b2b')
        
        self.hour_var = tk.StringVar(value="00")
        self.minute_var = tk.StringVar(value="00")
        
        self.hour_spinbox = ttk.Spinbox(
            self, from_=0, to=23, width=2,
            format="%02.0f",
            textvariable=self.hour_var,
            wrap=True,
            style='Dark.TSpinbox'
        )
        self.hour_spinbox.pack(side=tk.LEFT)
        
        tk.Label(self, text=":", bg='#2b2b2b', fg='white').pack(side=tk.LEFT)
        
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
        
        self.date_picker = ttk.Entry(
            self, width=12,
            style='Dark.TEntry'
        )
        self.date_picker.pack(side=tk.LEFT, padx=5)
        
        self.time_entry = TimeEntry(self)
        self.time_entry.pack(side=tk.LEFT, padx=5)
    
    def get_datetime(self):
        date_str = self.date_picker.get()
        time_str = self.time_entry.get_time()
        return datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")

    def set_datetime(self, dt):
        self.date_picker.delete(0, tk.END)
        self.date_picker.insert(0, dt.strftime("%d.%m.%Y"))
        self.time_entry.set_time(dt.strftime("%H:%M"))

def format_timedelta(td):
    is_negative = td.total_seconds() < 0
    td = abs(td)
    
    total_seconds = int(td.total_seconds())
    days = total_seconds // (24 * 3600)
    remaining = total_seconds % (24 * 3600)
    hours = remaining // 3600
    remaining = remaining % 3600
    minutes = remaining // 60
    seconds = remaining % 60
    
    sign = "-" if is_negative else ""
    return f"{sign}{days}:{hours:02d}:{minutes:02d}:{seconds:02d}"

def calculate():
    try:
        start_date = start_datetime_entry.get_datetime()
        end_date = end_datetime_entry.get_datetime()
        remaining_mb = float(entry_remaining_mb.get())
        total_gb = float(entry_total_gb.get())
        
        save_data()
        
        total_days = (end_date - start_date).total_seconds() / (24 * 3600)
        total_mb = total_gb * 1024
        daily_mb = total_mb / total_days
        
        time_passed = datetime.now() - start_date
        days_passed = time_passed.total_seconds() / (24 * 3600)
        
        used_mb = total_mb - remaining_mb
        profit_mb = (daily_mb * days_passed) - used_mb
        profit_days = profit_mb / daily_mb
        
        time_remaining = end_date - datetime.now()
        remaining_days = time_remaining.total_seconds() / (24 * 3600)
        
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
        profit_mb = (daily_mb * days_passed) - used_mb
        profit_timedelta = timedelta(days=abs(profit_mb / daily_mb))
        
        if profit_mb < 0:
            profit_color = '#ff4444'
            days_to_zero = abs(profit_mb / daily_mb)
            zero_date = now + timedelta(days=days_to_zero)
            profit_text = f"{abs(profit_mb):.2f} MB"
            if abs(profit_mb) > 1024:
                profit_text += f"\n({abs(profit_mb/1024):.2f} GB)"
            profit_text += f"\n\n{format_timedelta(profit_timedelta)}\n{zero_date.strftime('%d.%m.%Y %H:%M:%S')}"
        else:
            profit_color = '#44ff44'
            profit_text = f"{profit_mb:.2f} MB"
            if profit_mb > 1024:
                profit_text += f"\n({profit_mb/1024:.2f} GB)"
            profit_text += f"\n\n{format_timedelta(profit_timedelta)}"
        
        unit = unit_var.get()
        
        # Geçen süre kontrolü
        if days_passed < 1 and unit == "Günlük":
            less_than_day = True
        else:
            less_than_day = False
        
        if unit == "Günlük":
            average_download = used_mb / days_passed if days_passed > 0 else 0
            daily_average = daily_mb
            unit_text = "MB/gün"
        else:
            hours_passed = time_passed.total_seconds() / 3600
            average_download = used_mb / hours_passed if hours_passed > 0 else 0
            daily_average = daily_mb / 24
            unit_text = "MB/saat"
        
        if less_than_day:
            unit_text = "MB/saat (< 1 gün)"
        
        if unit == "Günlük":
            if average_download > 0:
                days_until_overage = remaining_mb / average_download
                overage_date = now + timedelta(days=days_until_overage)
                overage_text = "Aşım Yok" if overage_date > end_date else f"{overage_date.strftime('%d.%m.%Y\n%H:%M:%S')}"
            else:
                overage_text = "--"
        else:
            hours_passed = time_passed.total_seconds() / 3600
            if average_download > 0:
                hours_until_overage = remaining_mb / average_download
                overage_date = now + timedelta(hours=hours_until_overage)
                overage_text = "Aşım Yok" if overage_date > end_date else f"{overage_date.strftime('%d.%m.%Y\n%H:%M:%S')}"
            else:
                overage_text = "--"
        
        time_remaining = end_date - now
        remaining_days = time_remaining.total_seconds() / (24 * 3600)
        remaining_hours = time_remaining.total_seconds() / 3600
        
        # Günlük limit hesaplama
        if unit == "Günlük" and not less_than_day:
            daily_limit = remaining_mb / remaining_days if remaining_days > 0 else 0
            daily_limit_text = f"{daily_limit:.2f} MB/gün"
        else:
            daily_limit = remaining_mb / remaining_hours if remaining_hours > 0 else 0
            daily_limit_text = f"{daily_limit:.2f} MB/saat"
            if less_than_day:
                daily_limit_text += " (< 1 gün)"
        
        info_labels = [
            profit_text,
            f"{average_download:.2f} {unit_text}",
            daily_limit_text,
            overage_text,
            f"{daily_average:.2f} {unit_text}",
            f"KALAN GÜN\n{format_timedelta(time_remaining)}\n\nTOPLAM GÜN\n{format_timedelta(timedelta(days=total_days))}\n\n%{(remaining_days/total_days)*100:.2f} kaldı"
        ]
        
        for i, frame in enumerate(general_tab.winfo_children()):
            if isinstance(frame, ttk.Frame):
                for label in frame.winfo_children():
                    if isinstance(label, ttk.Label):
                        if i == 0:
                            if label.cget("style") == "InfoLabel.TLabel":
                                label.configure(text=info_labels[i], foreground=profit_color)
                        else:
                            if label.cget("style") == "InfoLabel.TLabel":
                                label.configure(text=info_labels[i], foreground='white')
        
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
        
        try:
            remaining_mb_val = float(entry_remaining_mb.get())
            if remaining_mb_val > 1024:
                gb_val = remaining_mb_val / 1024
                label_remaining_gb.configure(text=f"({gb_val:.2f} GB)")
            else:
                label_remaining_gb.configure(text="")
        except:
            label_remaining_gb.configure(text="")
        
        root.after(100, update_labels)
        
    except ValueError:
        pass

# Arayüz tasarımı
root = tk.Tk()
root.title("Mobil İnternet Hesaplama")
root.geometry("800x750")

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

data_frame = ttk.Frame(root)
data_frame.pack(fill='x', padx=10, pady=5)

mb_gb_frame = ttk.Frame(data_frame)
mb_gb_frame.pack(fill='x', padx=5, pady=5)

ttk.Label(mb_gb_frame, text="Kalan MB").pack(side='left', padx=5)
entry_remaining_mb = ttk.Entry(mb_gb_frame)
entry_remaining_mb.pack(side='left', padx=5)
label_remaining_gb = ttk.Label(mb_gb_frame, text="")
label_remaining_gb.pack(side='left')

ttk.Label(mb_gb_frame, text="Toplam GB").pack(side='left', padx=5)
entry_total_gb = ttk.Entry(mb_gb_frame)
entry_total_gb.pack(side='left', padx=5)

date_frame = ttk.Frame(data_frame)
date_frame.pack(fill='x', padx=5, pady=5)

ttk.Label(date_frame, text="Başlangıç").pack(side='left', padx=5)
start_datetime_entry = DateTimeEntry(date_frame)
start_datetime_entry.pack(side='left', padx=5)

ttk.Label(date_frame, text="Bitiş").pack(side='left', padx=5)
end_datetime_entry = DateTimeEntry(date_frame)
end_datetime_entry.pack(side='left', padx=5)

unit_frame = ttk.Frame(data_frame)
unit_frame.pack(fill='x', padx=5, pady=5)

ttk.Label(unit_frame, text="Birim").pack(side='left', padx=5)
unit_var = tk.StringVar(value="Günlük")
unit_combobox = ttk.Combobox(unit_frame, textvariable=unit_var, values=["Günlük", "Saatlik"], state="readonly")
unit_combobox.pack(side='left', padx=5)

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=10, pady=5)

general_tab = ttk.Frame(notebook)
notebook.add(general_tab, text='Genel Bilgiler')

frame_titles = [
    "Kâr Durumu", "Geçmiş Ortalama İndirme", "Limit",
    "Tahmini Aşım Tarihi", "Paket Ortalaması", "Toplam Süre"
]

for i in range(2):
    for j in range(3):
        idx = i * 3 + j
        frame = ttk.Frame(general_tab)
        frame.grid(row=i, column=j, padx=5, pady=5, sticky='nsew')
        frame.grid_propagate(False)
        frame.configure(width=200, height=150)
        ttk.Label(frame, text=frame_titles[idx], style='TLabel').place(relx=0.5, rely=0.15, anchor='center')
        label = ttk.Label(frame, text="--", style='InfoLabel.TLabel')
        label.place(relx=0.5, rely=0.5, anchor='center')

for i in range(2):
    general_tab.grid_rowconfigure(i, weight=1)
for j in range(3):
    general_tab.grid_columnconfigure(j, weight=1)

targets_tab = ttk.Frame(notebook)
notebook.add(targets_tab, text='Hedefler')

input_frame = ttk.Frame(targets_tab)
input_frame.pack(fill='x', padx=5, pady=5)

target_frame = ttk.Frame(input_frame)
target_frame.pack(side='left', padx=5, fill='x', expand=True)
ttk.Label(target_frame, text="Kâr (MB)").pack(padx=5, pady=5)
entry_target_profit = ttk.Entry(target_frame)
entry_target_profit.pack(padx=5, pady=5)
label_days_for_profit = ttk.Label(target_frame, text="--", style='InfoLabel.TLabel')
label_days_for_profit.pack(padx=5, pady=5)

limit_frame = ttk.Frame(input_frame)
limit_frame.pack(side='left', padx=5, fill='x', expand=True)
ttk.Label(limit_frame, text="Sınır (MB/Gün)").pack(padx=5, pady=5)
entry_target_limit = ttk.Entry(limit_frame)
entry_target_limit.pack(padx=5, pady=5)
label_days_for_limit = ttk.Label(limit_frame, text="--", style='InfoLabel.TLabel')
label_days_for_limit.pack(padx=5, pady=5)

button_calculate = ttk.Button(root, text="Hesapla", command=calculate)
button_calculate.pack(pady=10)

def on_closing():
    try:
        save_data()
    except:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

load_data()

style.configure('InfoLabel.TLabel', 
               font=('Arial', 20, 'bold'), 
               background='#2b2b2b', 
               foreground='white',
               anchor='center',
               justify='center')

root.mainloop()