import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
import json
import os

# Global değişkenler
packages = []
current_package_index = None

# Veri kaydetme ve yükleme fonksiyonları
def save_data():
    if current_package_index is not None:
        pkg = packages[current_package_index]
        pkg['start_date'] = start_datetime_entry.get_datetime().strftime("%d.%m.%Y %H:%M")
        pkg['end_date'] = end_datetime_entry.get_datetime().strftime("%d.%m.%Y %H:%M")
        pkg['remaining_mb'] = entry_remaining_mb.get()
        pkg['total_gb'] = entry_total_gb.get()
        pkg['target_profit'] = entry_target_profit.get()
        pkg['target_limit'] = entry_target_limit.get()
        pkg['unit'] = unit_var.get()
        pkg['active_hours'] = entry_active_hours.get()
        try:
            with open('internet_data.json', 'w') as f:
                json.dump(packages, f)
        except Exception as e:
            messagebox.showerror("Hata", "Veriler kaydedilirken hata oluştu!")

def load_data():
    try:
        if os.path.exists('internet_data.json'):
            with open('internet_data.json', 'r') as f:
                global packages
                packages = json.load(f)
                update_package_combobox()
                if packages:
                    select_package(0)
                else:
                    clear_input_fields()
                update_button_states()
    except Exception as e:
        pass

# TimeEntry sınıfı
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

# DateTimeEntry sınıfı
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

# Yardımcı fonksiyonlar
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
    if current_package_index is not None:
        try:
            start_date = start_datetime_entry.get_datetime()
            end_date = end_datetime_entry.get_datetime()
            remaining_mb = float(entry_remaining_mb.get())
            total_gb = float(entry_total_gb.get())
            active_hours = float(entry_active_hours.get())
            if active_hours <= 0:
                raise ValueError("Aktif saatler sıfır veya negatif olamaz.")
            
            save_data()
            update_labels()
            
        except ValueError as e:
            messagebox.showerror("Hata", f"Lütfen tüm alanları doğru formatta doldurun: {str(e)}")

def update_labels():
    try:
        if current_package_index is None:
            return
        start_date = start_datetime_entry.get_datetime()
        end_date = end_datetime_entry.get_datetime()
        remaining_mb = float(entry_remaining_mb.get())
        total_gb = float(entry_total_gb.get())
        active_hours_per_day = float(entry_active_hours.get())
        now = datetime.now()
        
        total_days = (end_date - start_date).total_seconds() / (24 * 3600)
        total_mb = total_gb * 1024
        daily_mb = total_mb / total_days if total_days > 0 else 0
        
        time_passed = now - start_date
        days_passed = time_passed.total_seconds() / (24 * 3600)
        
        used_mb = total_mb - remaining_mb
        profit_mb = (daily_mb * days_passed) - used_mb
        profit_timedelta = timedelta(days=abs(profit_mb / daily_mb)) if daily_mb > 0 else timedelta(0)
        
        if profit_mb < 0:
            profit_color = '#ff4444'
            days_to_zero = abs(profit_mb / daily_mb) if daily_mb > 0 else 0
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
        
        if days_passed < 1 and unit == "Günlük":
            less_than_day = True
        else:
            less_than_day = False
        
        if unit == "Günlük":
            average_download = used_mb / days_passed if days_passed > 0 else 0
            daily_average = daily_mb
            unit_text = "MB/gün"
            if average_download > 0:
                days_until_overage = remaining_mb / average_download
                overage_date = now + timedelta(days=days_until_overage)
                overage_text = "Aşım Yok" if overage_date > end_date else f"{overage_date.strftime('%d.%m.%Y\n%H:%M:%S')}"
            else:
                overage_text = "--"
            time_remaining = end_date - now
            remaining_days = time_remaining.total_seconds() / (24 * 3600)
            daily_limit = remaining_mb / remaining_days if remaining_days > 0 else 0
            daily_limit_text = f"{daily_limit:.2f} MB/gün"
        else:  # Saatlik
            total_active_hours = total_days * active_hours_per_day
            passed_active_hours = days_passed * active_hours_per_day
            time_remaining = end_date - now
            remaining_days = time_remaining.total_seconds() / (24 * 3600)
            remaining_active_hours = remaining_days * active_hours_per_day
            
            average_download = used_mb / passed_active_hours if passed_active_hours > 0 else 0
            daily_average = total_mb / total_active_hours if total_active_hours > 0 else 0
            unit_text = "MB/saat"
            if average_download > 0:
                hours_until_overage = remaining_mb / average_download
                overage_date = now + timedelta(hours=hours_until_overage)
                overage_text = "Aşım Yok" if overage_date > end_date else f"{overage_date.strftime('%d.%m.%Y\n%H:%M:%S')}"
            else:
                overage_text = "--"
            daily_limit = remaining_mb / remaining_active_hours if remaining_active_hours > 0 else 0
            daily_limit_text = f"{daily_limit:.2f} MB/saat"
        
        if less_than_day:
            unit_text = "MB/saat\n(< 1 gün)"
            daily_limit_text += "\n(< 1 gün)" if unit == "Saatlik" else ""
        
        info_labels = [
            profit_text,
            f"{average_download:.2f} {unit_text}",
            daily_limit_text,
            overage_text,
            f"{daily_average:.2f} {unit_text}",
            f"KALAN GÜN\n{format_timedelta(time_remaining)}\n\nTOPLAM GÜN\n{format_timedelta(timedelta(days=total_days))}\n\n%{(remaining_days/total_days)*100:.2f} kaldı" if total_days > 0 else "N/A"
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
            days_for_target_profit = (target_profit_mb - profit_mb) / daily_mb if daily_mb > 0 else 0
            target_profit_date = now + timedelta(days=days_for_target_profit)
            label_days_for_profit.configure(
                text=f"{format_timedelta(timedelta(days=days_for_target_profit))}\n"
                     f"{target_profit_date.strftime('%d.%m.%Y %H:%M:%S')}"
            )
        except:
            label_days_for_profit.configure(text="--")
        
        try:
            target_limit_mb = float(entry_target_limit.get())
            days_for_target_limit = remaining_days - (remaining_mb / target_limit_mb) if target_limit_mb > 0 else 0
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

# Paket yönetimi fonksiyonları
def add_package():
    name = simpledialog.askstring("Yeni Paket", "Paket adını girin:")
    if name and name not in [pkg['name'] for pkg in packages]:
        new_package = {
            'name': name,
            'start_date': datetime.now().strftime("%d.%m.%Y %H:%M"),
            'end_date': (datetime.now() + timedelta(days=30)).strftime("%d.%m.%Y %H:%M"),
            'remaining_mb': '0',
            'total_gb': '0',
            'target_profit': '0',
            'target_limit': '0',
            'unit': 'Günlük',
            'active_hours': '14'
        }
        packages.append(new_package)
        update_package_combobox()
        package_combobox.set(name)
        select_package(len(packages) - 1)
        update_button_states()
    else:
        messagebox.showerror("Hata", "Bu isimde bir paket zaten var veya isim boş.")

def remove_package():
    global current_package_index
    if current_package_index is not None:
        del packages[current_package_index]
        current_package_index = None
        update_package_combobox()
        if packages:
            select_package(0)
        else:
            clear_input_fields()
        update_button_states()

def update_package_combobox():
    package_names = [pkg['name'] for pkg in packages]
    package_combobox['values'] = package_names
    if packages:
        package_combobox.set(packages[current_package_index]['name'] if current_package_index is not None else packages[0]['name'])
    else:
        package_combobox.set('')

def select_package(index):
    global current_package_index
    current_package_index = index
    pkg = packages[index]
    start_datetime_entry.set_datetime(datetime.strptime(pkg['start_date'], "%d.%m.%Y %H:%M"))
    end_datetime_entry.set_datetime(datetime.strptime(pkg['end_date'], "%d.%m.%Y %H:%M"))
    entry_remaining_mb.delete(0, tk.END)
    entry_remaining_mb.insert(0, pkg['remaining_mb'])
    entry_total_gb.delete(0, tk.END)
    entry_total_gb.insert(0, pkg['total_gb'])
    entry_target_profit.delete(0, tk.END)
    entry_target_profit.insert(0, pkg['target_profit'])
    entry_target_limit.delete(0, tk.END)
    entry_target_limit.insert(0, pkg['target_limit'])
    entry_active_hours.delete(0, tk.END)
    entry_active_hours.insert(0, pkg.get('active_hours', '14'))
    unit_var.set(pkg['unit'])
    calculate()

def on_package_select(event):
    selection = package_combobox.get()
    if selection:
        index = [pkg['name'] for pkg in packages].index(selection)
        select_package(index)

def clear_input_fields():
    start_datetime_entry.set_datetime(datetime.now())
    end_datetime_entry.set_datetime(datetime.now() + timedelta(days=30))
    entry_remaining_mb.delete(0, tk.END)
    entry_remaining_mb.insert(0, '0')
    entry_total_gb.delete(0, tk.END)
    entry_total_gb.insert(0, '0')
    entry_target_profit.delete(0, tk.END)
    entry_target_profit.insert(0, '0')
    entry_target_limit.delete(0, tk.END)
    entry_target_limit.insert(0, '0')
    entry_active_hours.delete(0, tk.END)
    entry_active_hours.insert(0, '14')
    unit_var.set('Günlük')
    for frame in general_tab.winfo_children():
        if isinstance(frame, ttk.Frame):
            for label in frame.winfo_children():
                if isinstance(label, ttk.Label) and label.cget("style") == "InfoLabel.TLabel":
                    label.configure(text="--")
    label_days_for_profit.configure(text="--")
    label_days_for_limit.configure(text="--")
    label_remaining_gb.configure(text="")

def update_button_states():
    if packages:
        button_calculate.state(['!disabled'])
        remove_package_button.state(['!disabled'])
    else:
        button_calculate.state(['disabled'])
        remove_package_button.state(['disabled'])

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
style.map('TButton',
          background=[('active', '#606060')],
          foreground=[('active', 'white')])
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
style.configure('TCombobox',
                fieldbackground='#404040',
                background='#404040',
                foreground='white',
                arrowcolor='white',
                selectbackground='#606060',
                selectforeground='white')
style.map('TCombobox',
          fieldbackground=[('readonly', '#404040')],
          background=[('readonly', '#404040')],
          foreground=[('readonly', 'white')])
style.map('TNotebook.Tab',
          background=[('selected', '#606060')],
          foreground=[('selected', 'white')])

root.configure(bg='#2b2b2b')

# Üst frame'ler
left_frame = ttk.Frame(root)
left_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)

center_frame = ttk.Frame(root)
center_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=5)

right_frame = ttk.Frame(root)
right_frame.grid(row=0, column=2, sticky='nsew', padx=10, pady=5)

# Grid yapılandırması
root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=0)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)
root.grid_columnconfigure(2, weight=1)

# Sol taraf - Paket yönetimi
ttk.Label(left_frame, text="Paketler:").pack(side='top', anchor='w', padx=5, pady=2)
package_combobox = ttk.Combobox(left_frame, state="readonly")
package_combobox.pack(side='top', fill='x', padx=5, pady=2)
package_combobox.bind("<<ComboboxSelected>>", on_package_select)
add_package_button = ttk.Button(left_frame, text="Yeni Paket Ekle", command=add_package)
add_package_button.pack(side='top', fill='x', padx=5, pady=2)
remove_package_button = ttk.Button(left_frame, text="Paketi Sil", command=remove_package)
remove_package_button.pack(side='top', fill='x', padx=5, pady=2)

# Orta taraf - Veri girişi
remaining_mb_frame = ttk.Frame(center_frame)
remaining_mb_frame.pack(fill='x', padx=5, pady=2)
ttk.Label(remaining_mb_frame, text="Kalan MB").pack(side='left', padx=5)
entry_remaining_mb = ttk.Entry(remaining_mb_frame)
entry_remaining_mb.pack(side='left', padx=5)
label_remaining_gb = ttk.Label(remaining_mb_frame, text="")
label_remaining_gb.pack(side='left')

total_gb_frame = ttk.Frame(center_frame)
total_gb_frame.pack(fill='x', padx=5, pady=2)
ttk.Label(total_gb_frame, text="Toplam GB").pack(side='left', padx=5)
entry_total_gb = ttk.Entry(total_gb_frame)
entry_total_gb.pack(side='left', padx=5)

start_frame = ttk.Frame(center_frame)
start_frame.pack(fill='x', padx=5, pady=2)
ttk.Label(start_frame, text="Başlangıç").pack(side='left', padx=5)
start_datetime_entry = DateTimeEntry(start_frame)
start_datetime_entry.pack(side='left', padx=5)

end_frame = ttk.Frame(center_frame)
end_frame.pack(fill='x', padx=5, pady=2)
ttk.Label(end_frame, text="Bitiş").pack(side='left', padx=5)
end_datetime_entry = DateTimeEntry(end_frame)
end_datetime_entry.pack(side='left', padx=5)

# Sağ taraf - Ek ayarlar
unit_frame = ttk.Frame(right_frame)
unit_frame.pack(fill='x', padx=5, pady=2)
ttk.Label(unit_frame, text="Birim").pack(side='left', padx=5)
unit_var = tk.StringVar(value="Günlük")
unit_combobox = ttk.Combobox(unit_frame, textvariable=unit_var, values=["Günlük", "Saatlik"], state="readonly")
unit_combobox.pack(side='left', padx=5)

active_hours_frame = ttk.Frame(right_frame)
active_hours_frame.pack(fill='x', padx=5, pady=2)
ttk.Label(active_hours_frame, text="Aktif Saatler").pack(side='left', padx=5)
entry_active_hours = ttk.Entry(active_hours_frame)
entry_active_hours.pack(side='left', padx=5)
entry_active_hours.insert(0, '14')

# Notebook
notebook = ttk.Notebook(root)
notebook.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=10, pady=5)

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

button_calculate = ttk.Button(root, text="Kaydet", command=calculate)
button_calculate.grid(row=2, column=0, columnspan=3, pady=10)

def on_closing():
    try:
        save_data()
    except:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Başlangıç ayarları
load_data()

style.configure('InfoLabel.TLabel', 
               font=('Arial', 20, 'bold'), 
               background='#2b2b2b', 
               foreground='white',
               anchor='center',
               justify='center')

root.mainloop()