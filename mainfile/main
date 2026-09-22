import os, datetime
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from loadcsv import load_csv, save_csv, CSV_FILE

entry, file_data  = {}, {}
def create_files():
    count = 0
    filetype = filetype_combo.get().strip()
    inpath = entry['inpath'].get().strip()
    outpath = entry['outpath'].get().strip()
    lab = entry['lab'].get().strip()
    ex = entry['ex'].get().strip()
    template = [[i[0], i[1].replace('{date}', entry['date'].get().strip())] for i in file_data[filetype]['text']]
    if not inpath or not outpath or not lab or not ex:
        messagebox.showerror('Error', 'All fields are required!')
        return
    if not os.path.isdir(inpath):
        messagebox.showerror('Error', f'Input path is not a directory:\n{inpath}')
        return
    try:
        lab, ex_count = int(lab), int(ex)
        if lab < 0 or ex_count < 0 or lab > 99 or ex_count > 99: raise ValueError
    except:
        messagebox.showerror('Error', 'Lab and Ex must be an non-negative integer <= 99')
        return
    if not os.path.exists(outpath):
        if not messagebox.askyesno('Warning', 'Creating a new directory for the path'): return
        try:
            os.makedirs(outpath)
            log(f'Created directory: {outpath}')
        except Exception as e:
            messagebox.showerror('Error', f'Could not create directory: {str(e)}')
            return
    for ex_num in range(1, ex_count + 1):
        fname = f"lab{lab:02d}ex{ex_num:02d}.{file_data[filetype]['type']}"
        src = os.path.join(inpath,  fname)
        dst = os.path.join(outpath, fname)
        if not os.path.isfile(src):
            log(f'Source file not found:\n{src}')
            continue
        try:
            with open(src, 'r', encoding='utf-8') as f: lines = f.readlines()
        except Exception as e:
            log(f'Could not read {src}:\n{str(e)}')
            continue
        found, count = 0, count + 1
        for i, line in enumerate(lines): 
            for j in range(len(template)): 
                if line.startswith(template[j][0]): 
                    lines[i] = template[j][0] + template[j][1]
                    found += 1
            if found == len(template): break
        try:
            with open(dst, 'w', encoding='utf-8') as f: f.writelines(lines)
        except Exception as e:
            messagebox.showerror('Error', f'Could not write {dst}:\n{str(e)}')
            return
        try:
            os.remove(src)
            log(f'Removed source file: {src}')
        except Exception as e: log(f'Warning: could not remove {src}: {str(e)}')
        log(f'Created {dst} with lines {found}')
    messagebox.showinfo('Success', f'Successfully processed {count} file(s).')
    return
def browse_file():
    '''讓用戶從電腦中選取一個檔案（作為輸出檔案）。'''
    filetype = filetype_combo.get().strip()
    ext = '.' + file_data[filetype]['type']
    try: filename = f"lab{int(entry['lab'].get().strip()):02d}ex{int(entry['ex'].get().strip()):02d}{ext}"
    except: filename = 'untitle' + ext
    default_dir = file_data[filetype]['inpath']
    types = [(ext, '*' + ext), ('All files', '*.*')]
    path = filedialog.asksaveasfilename(
        title='選擇輸出檔案',
        initialdir = default_dir if os.path.isdir(default_dir) else None,
        initialfile = filename,
        defaultextension = ext,
        filetypes = types
    )
    if path:
        entry['inpath'].delete(0, tk.END)
        entry['inpath'].insert(0, os.path.dirname(path))
        log(f'Selected file: {path}')
def on_type_change(event = None):
    filetype = filetype_combo.get()
    if filetype not in file_data: return
    for i in ['inpath', 'outpath']:
        entry[i].delete(0, tk.END)
        entry[i].insert(0, file_data[filetype][i])
    log(f'Selected type: {filetype}')
def refresh_types():
    filetype = [i for i, _ in file_data.items()]
    filetype_combo['values'] = filetype
    if file_data:
        filetype_combo.current(0)
        on_type_change()
def add_type():
    new_type = entry['new_type'].get().strip()
    new_inpath = entry['new_inpath'].get().strip()
    new_outpath = entry['new_outpath'].get().strip()
    new_text = entry['new_text'].get('1.0', tk.END).rstrip('\n')
    if not new_type or not new_inpath or not new_outpath or not new_text:
        messagebox.showerror('Error', 'All fields are required!')
        return
    if new_type in file_data:
        if not messagebox.askyesno('Warning', f"File type '{new_type}' already exists!\nOverwrite it?"): return
    file_data[new_type] = {'inpath': new_inpath, 'outpath': new_outpath, 'text': [i for i in new_text.split('\n')]}
    if save_csv(file_data):
        refresh_types()
        log(f'Added / updated file type: {new_type}')
        messagebox.showinfo('Success', f"File type '{new_type}' saved to {CSV_FILE}!")
        for i in labels: entry[i[0]].delete(0, tk.END)
        entry['new_text'].delete('1.0', tk.END)
def log(message):
    if not message: return
    status_text.config(state=tk.NORMAL)
    status_text.insert(tk.END, message + '\n')
    status_text.see(tk.END)
    status_text.config(state=tk.DISABLED)
    
# ------------------------------------------------------------------ 介面
root = tk.Tk()
root.title('Programming File Manager')
root.geometry('600x640')
root.resizable(0, 0)
root.wm_attributes('-topmost', 1)

main_frame = ttk.Frame(root, padding = '20')
main_frame.grid(row = 0, column = 0, sticky = (tk.W, tk.E, tk.N, tk.S))
root.columnconfigure(0, weight = 1)
root.rowconfigure(0, weight = 1)
main_frame.columnconfigure(0, weight = 1)
main_frame.columnconfigure(1, weight = 0)
main_frame.rowconfigure(2, weight = 1)

header_label = ttk.Label(main_frame, text = 'PROGRAMMING FILE MANAGER',
                         font = ('Arial', 16, 'bold'))
header_label.grid(row = 0, column = 0, columnspan = 2, pady = (0, 10))

notebook = ttk.Notebook(main_frame)
notebook.grid(row = 1, column = 0, columnspan = 2, sticky = (tk.W, tk.E))

# ---------------- 分頁一：建立檔案 ----------------
create_frame = ttk.Frame(notebook, padding = '15')
notebook.add(create_frame, text = '建立檔案')
create_frame.columnconfigure(1, weight = 1)

labels = [['檔案類型:'], ['輸入檔案:'], ['輸出路徑'], ['日期:'], ['Lab:'], ['Number of ex:']]

ttk.Label(create_frame, text = labels[0][0]).grid(row = 0, column = 0, sticky = tk.W, pady = 5)
filetype_combo = ttk.Combobox(create_frame, state = 'readonly', width = 30)
filetype_combo.grid(row = 0, column = 1, columnspan = 2, sticky = (tk.W, tk.E), pady = 5)
filetype_combo.bind('<<ComboboxSelected>>', on_type_change)

ttk.Label(create_frame, text = labels[1][0]).grid(row = 1, column = 0, sticky = tk.W, pady = 5)
entry['inpath'] = ttk.Entry(create_frame, width = 30)
entry['inpath'].grid(row = 1, column = 1, sticky = (tk.W, tk.E), pady = 5)
browse_btn = ttk.Button(create_frame, text = '瀏覽…', command = browse_file)
browse_btn.grid(row = 1, column = 2, padx = (5, 0), pady = 5)

ttk.Label(create_frame, text = labels[2][0]).grid(row = 2, column = 0, sticky = tk.W, pady = 5)
entry['outpath'] = ttk.Entry(create_frame, width = 30)
entry['outpath'].grid(row = 2, column = 1, columnspan = 2, sticky = (tk.W, tk.E), pady = 5)

ttk.Label(create_frame, text = labels[3][0]).grid(row = 3, column = 0, sticky = tk.W, pady = 5)
entry['date'] = ttk.Entry(create_frame, width = 30)
entry['date'].grid(row = 3, column = 1, columnspan = 2, sticky = (tk.W, tk.E), pady = 5)
entry['date'].insert(0, datetime.date.today().strftime('%d/%m/%Y'))

ttk.Label(create_frame, text = labels[4][0]).grid(row = 4, column = 0, sticky = tk.W, pady = 5)
entry['lab'] = ttk.Entry(create_frame, width = 30)
entry['lab'].grid(row = 4, column = 1, columnspan = 2, sticky = (tk.W, tk.E), pady = 5)
entry['lab'].insert(0, 1)

ttk.Label(create_frame, text = labels[5][0]).grid(row = 5, column = 0, sticky = tk.W, pady = 5)
entry['ex'] = ttk.Entry(create_frame, width = 30)
entry['ex'].grid(row = 5, column = 1, columnspan = 2, sticky = (tk.W, tk.E), pady = 5)
entry['ex'].insert(0, 2)

create_btn = ttk.Button(create_frame, text = 'Create File', command = create_files)
create_btn.grid(row = 6, column = 0, columnspan = 3, pady = 20)

# ---------------- 分頁二：新增模式 ----------------
add_frame = ttk.Frame(notebook, padding = '15')
notebook.add(add_frame, text = '新增模式')
add_frame.columnconfigure(1, weight = 1)
add_frame.rowconfigure(2, weight = 1)
labels = [['new_type', '檔案類型:'], ['new_inpath', '默認輸入路徑:'], ['new_outpath', '默認輸出路徑:']]
for i in range(3):
    ttk.Label(add_frame, text = labels[i][1]).grid(row = i, column = 0, sticky = tk.W, pady = 5)
    entry[labels[i][0]] = ttk.Entry(add_frame, width = 30)
    entry[labels[i][0]].grid(row = i, column = 1, columnspan = 2, sticky = (tk.W, tk.E), pady = 5)
    
ttk.Label(add_frame, text='文字:').grid(row = 3, column=0, sticky=(tk.W, tk.N), pady=5)
entry['new_text'] = tk.Text(add_frame, height = 12, width = 45)
entry['new_text'].grid(row = 3, column = 1, columnspan = 2, sticky = (tk.W, tk.E, tk.N, tk.S), pady = 5)
add_text_scroll = ttk.Scrollbar(add_frame, orient=tk.VERTICAL,
                                command=entry['new_text'].yview)
add_text_scroll.grid(row = 3, column=3, sticky=(tk.N, tk.S), pady=5)
entry['new_text'].configure(yscrollcommand=add_text_scroll.set)

add_btn = ttk.Button(add_frame, text='新增檔案類型', command=add_type)
add_btn.grid(row=4, column=0, columnspan=3, pady=20)

# ---------------- 狀態顯示區 ----------------
status_text = tk.Text(main_frame, height=8, width=60, state=tk.DISABLED)
status_text.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=status_text.yview)
scrollbar.grid(row=2, column=1, sticky=(tk.N, tk.S), pady=(15, 0))
status_text.configure(yscrollcommand=scrollbar.set)

# ------------------------------------------------------------------ 啟動
msg, file_data = load_csv()
if msg: log(msg)
refresh_types()
root.mainloop()
