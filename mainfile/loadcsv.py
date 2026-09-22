import os, csv, json
from tkinter import messagebox
from prompt import DEFAULT_ROWS
CSV_FILE = 'file_types.csv'
HEADER   = ['文件類型', '默認輸出路徑', '文字']
def save_csv(file_data):
    '''把 file_types / file_data 寫回 CSV 檔。'''
    try:
        with open(CSV_FILE, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)
            for i, j in file_data.items(): 
                writer.writerow([i, j['type'], j['inpath'], j['outpath'], json.dumps(j['text'], ensure_ascii = False)])
        return 1
    except Exception as e: messagebox.showerror('Error', f'Could not save CSV: {str(e)}')
    return 0
def load_csv():
    file_data = {}
    if not os.path.exists(CSV_FILE):
        if save_csv(DEFAULT_ROWS): return f'Created default CSV: {CSV_FILE}', DEFAULT_ROWS
        return 'Cannot found and create filetype.CSV', DEFAULT_ROWS
    try:
        with open(CSV_FILE, 'r', encoding='utf-8-sig', newline='') as f: rows = list(csv.reader(f))
        for row in rows:
            name = row[0].strip()
            if len(row) < 3 or not name or name == HEADER[0]: continue
            file_data[name] = {'type': row[1], 'inpath': row[2], 'outpath': row[3], 'text': json.loads(row[4])}
        if not file_data: messagebox.showwarning('Warning', 'No file type found in the CSV file!')
        return f'Loaded {len(file_data)} file type(s) from {CSV_FILE}', file_data
    except Exception as e: messagebox.showerror('Error', f'Could not read CSV: {str(e)}')
    return '', file_data
