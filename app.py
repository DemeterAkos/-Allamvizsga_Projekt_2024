import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

# 📌 MySQL adatbázis kapcsolat
def connect_to_database():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="robotsensorsmeasurment_db"
    )
    return conn

def get_data(query,params=()):
    conn = connect_to_database()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def create_table(df):
    # 📌 Meglévő táblázat törlése, ha van
    for widget in table_frame.winfo_children():
        widget.destroy()

    # 📌 Táblázat létrehozása
    tree = ttk.Treeview(table_frame, columns=list(df.columns), show="headings")

    # 📌 Oszlopok beállítása
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=120,stretch=tk.YES)

    # 📌 Adatok hozzáadása a táblázathoz
    for index, row in df.iterrows():
        tree.insert("", tk.END, values=list(row))

    tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    # 📌 Hozzáadunk egy vízszintes görgetősávot
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(fill=tk.Y, side=tk.LEFT)

    tree.configure(yscrollcommand=scrollbar.set)

# 📌 Adatok lekérése gombnyomásra
def click_Get_All_Data():
    query = "SELECT * FROM sensor_data"
    df = get_data(query)
    create_table(df)

def click_Get_Collision():
    df = get_data("SELECT * FROM sensor_data WHERE `Robot Collision` = 1")
    create_table(df)

def click_filter_by_direction():
    direction = txt_Direction.get().strip()  # Eltávolítja az esetleges felesleges szóközöket

    if direction:  # Csak akkor futtassuk, ha van érték megadva
        query = "SELECT * FROM sensor_data WHERE `Control direction` = %s"
        df = get_data(query,(direction,))  # Paraméterezett lekérdezés
        create_table(df)
    else:
        print("Please enter a direction!")  # Hibaüzenet konzolon

def click_filter_by_date():
    start_date = cal_start.get_date()
    end_date = cal_end.get_date()

    query = "SELECT * FROM sensor_data WHERE `Date Time` BETWEEN %s AND %s"
    df = get_data(query, (start_date, end_date))
    create_table(df)

def click_search_between_distance():
    low_distance_value = txt_distance_low.get().strip()
    high_distance_value = txt_distance_high.get().strip()

    if low_distance_value and high_distance_value:  # Csak akkor futtassuk, ha van érték megadva
        query = "SELECT * FROM sensor_data WHERE `Obstacle Distance`BETWEEN %s AND %s ORDER BY `Obstacle Distance` DESC"
        df = get_data(query, (low_distance_value,high_distance_value))  # Paraméterezett lekérdezés
        create_table(df)
    else:
        print("Please enter low and high distance value!")  # Hibaüzenet konzolon

# 📌 Tkinter ablak létrehozása
root = tk.Tk()
root.title("Robot Sensor Data")
root.geometry("1250x600")

# Add an icon to the window
root.iconbitmap("roboticon.ico")

# 📌 Fő keret létrehozása
main_frame = ttk.Frame(root)
main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# 📌 Gombok kerete
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=0, column=0, columnspan=3, pady=10)

BTN_GetAll_Data = ttk.Button(button_frame, text="Get All Latest Data", command=click_Get_All_Data)
BTN_GetAll_Data.grid(row=0, column=0, padx=10)

BTN_GetCollision_Data = ttk.Button(button_frame, text="Search for Collision Data", command=click_Get_Collision)
BTN_GetCollision_Data.grid(row=0, column=1, padx=10)


BTN_Filter_by_direction = ttk.Button(button_frame, text="Filter datas by Direction", command=click_filter_by_direction)
BTN_Filter_by_direction.grid(row=0, column=2, padx=10)

BTN_filter_date = ttk.Button(button_frame, text="Filter by Date", command=click_filter_by_date)
BTN_filter_date.grid(row=0, column=8, padx=10)

BTN_search_between_distance = ttk.Button(button_frame, text="Search between distance", command=click_search_between_distance)
BTN_search_between_distance.grid(row=1, column=8, padx=10)

#Text field robot movement dirrection filter
#Placeholders control
def add_placeholder(event):
    """Ha az Entry üres, beszúrja a placeholder szöveget."""
    if not txt_Direction.get():
        txt_Direction.insert(0, "Enter text here...")
        txt_Direction.config(foreground="grey")  # Szürke színnel jelzi a placeholdert

def remove_placeholder(event):
    """Ha az Entry tartalmazza a placeholder szöveget, törli azt."""
    if txt_Direction.get() == "Enter text here...":
        txt_Direction.delete(0, tk.END)
        txt_Direction.config(foreground="black")  # Fekete szín a normál beviteli szöveghez


txt_Direction = ttk.Entry(button_frame, width=20)
txt_Direction.insert(0,"Enter direction here")
txt_Direction.config(foreground="grey")
txt_Direction.grid(row=0, column=3, padx=10)

txt_Direction.bind("<FocusIn>", remove_placeholder)
txt_Direction.bind("<FocusOut>", add_placeholder)

#Filter between two object distance
#low value
ttk.Label(button_frame, text="Low value:").grid(row=1, column=4, padx=5)
txt_distance_low = ttk.Entry(button_frame,width=25)
txt_distance_low.insert(0,"Enter low distance value")
txt_distance_low.config(foreground="gray")
txt_distance_low.grid(row=1,column=5,padx=5)

#high value
ttk.Label(button_frame, text="High value:").grid(row=1, column=6, padx=5)
txt_distance_high = ttk.Entry(button_frame,width=25)
txt_distance_high.insert(0,"Enter high distance value")
txt_distance_high.config(foreground="gray")
txt_distance_high.grid(row=1,column=7,padx=5)

#Filter by Date Strat date
ttk.Label(button_frame, text="Start Date:").grid(row=0, column=4, padx=5)
cal_start = DateEntry(button_frame, width=12, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
cal_start.grid(row=0, column=5, padx=5)

#Filter by Date End date
ttk.Label(button_frame, text="End Date:").grid(row=0, column=6, padx=5)
cal_end = DateEntry(button_frame, width=12, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
cal_end.grid(row=0, column=7, padx=5)

# 📌 Táblázat helye
table_frame = ttk.Frame(main_frame)
table_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

# 📌 Ablak méretezés engedélyezése
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(1, weight=1)

# 📌 Fő ciklus indítása
root.mainloop()
