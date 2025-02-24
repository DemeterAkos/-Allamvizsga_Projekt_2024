import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import date
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np


#MySQL database connection
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
    #Delete existing table, if any
    for widget in table_frame.winfo_children():
        widget.destroy()

    #Create a table
    tree = ttk.Treeview(table_frame, columns=list(df.columns), show="headings")

    #Setting columns
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=120,stretch=tk.YES)

    #Add data to the table
    for index, row in df.iterrows():
        tree.insert("", tk.END, values=list(row))

    tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    # Add a horizontal scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(fill=tk.Y, side=tk.LEFT)

    tree.configure(yscrollcommand=scrollbar.set)

#Get data at the touch of a button
#Functions declaration for buttuns event
def click_Get_All_Data():
    # Make query select
    query = "SELECT * FROM sensor_data"
    df = get_data(query)
    # Refresh table output
    create_table(df)

def click_Get_Collision():
    # Make query select
    df = get_data("SELECT * FROM sensor_data WHERE `Robot Collision` = 1")
    # Refresh table output
    create_table(df)

def click_filter_by_direction(event = None):
    #Get direction value from Input field
    direction = txt_Direction.get().strip()

    if direction:
        # Make query select
        query = "SELECT * FROM sensor_data WHERE `Control direction` = %s"
        df = get_data(query,(direction,))
        # Refresh table output
        create_table(df)
    else:
        print("Please enter a direction!")  # Error message

def click_filter_by_date():
    start_date = cal_start.get_date().strftime("%Y-%m-%d")
    end_date = cal_end.get_date().strftime("%Y-%m-%d")
    # Make query select
    query = "SELECT * FROM sensor_data WHERE `Date Time` BETWEEN %s AND %s"
    df = get_data(query, (start_date, end_date))
    # Refresh table output
    create_table(df)

def click_filter_today():
    #Get today date
    today = date.today()
    #Make query select
    query = "SELECT * FROM sensor_data WHERE `Date Time` = %s"
    df = get_data(query,(today,))
    #Refresh table output
    create_table(df)

def click_search_between_distance():
    low_distance_value = txt_distance_low.get().strip()
    high_distance_value = txt_distance_high.get().strip()

    if low_distance_value and high_distance_value:  #If has value in Input field
        # Make query select
        query = "SELECT * FROM sensor_data WHERE `Obstacle Distance`BETWEEN %s AND %s ORDER BY `Obstacle Distance` DESC"
        df = get_data(query, (low_distance_value,high_distance_value))
        # Refresh table output
        create_table(df)
    else:
        print("Please enter low and high distance value!")


def click_show_collision_distance_chart():
    # Make query select
    query = "SELECT `Obstacle Distance` FROM sensor_data WHERE `Robot Collision` = 1"
    query_count = "SELECT Count(*) AS 'Total Collision' FROM sensor_data WHERE `Robot Collision` = 1"
    df = get_data(query)
    df1 = get_data(query_count)
    # Refresh table output
    create_table(df1)

    if df.empty:
        print("No collision data!")
        return

    # Create a window to display the chart
    chart_window = tk.Toplevel(root)
    chart_window.title("Collision Distance Chart")
    chart_window.geometry("1000x400")
    chart_window.iconbitmap("favicon.ico")

    # Create Matplotlib Figure
    fig = Figure(figsize=(6, 4), dpi=100)
    ax = fig.add_subplot(111)

    # 20 cm steps between min and max values
    min_val = int(df["Obstacle Distance"].min() // 20 * 20)  # Lowest value rounded
    max_val = int(df["Obstacle Distance"].max() // 20 * 20 + 20)  # Highest value rounded
    bins = np.arange(min_val, max_val + 20, 20)  # 20 cm intervals

    # Representation of data
    ax.hist(df["Obstacle Distance"], bins=bins, color="blue", edgecolor="black")
    ax.set_title("Obstacle Distance During Collisions")
    ax.set_xlabel("Distance (cm)")
    ax.set_ylabel("Frequency")

    ax.set_xticks(np.arange(min_val,max_val + 50,50))

    # Inserting a chart into the window
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def click_avg_distance_by_direction():
    #Make query select
    query = "SELECT `Control Direction`, AVG(`Obstacle Distance`) AS Avg_Distance FROM sensor_data GROUP BY `Control Direction` ORDER BY Avg_Distance ASC;"
    df = get_data(query)
    create_table(df)

    if df.empty:
        print("No data!")
        return

    # Create a window to display the chart
    chart_window = tk.Toplevel(root)
    chart_window.title("Average obstacle distance by direction Chart")
    chart_window.geometry("1000x600")
    chart_window.iconbitmap("favicon.ico")

    # Create Matplotlib Figure
    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)

    # Representation of data (Bar Chart)
    ax.bar(df["Control Direction"], df["Avg_Distance"], color="purple", edgecolor="black")

    ax.set_title("Average obstacle distance by direction of movement",fontsize=12, fontweight="bold")
    ax.set_xlabel("Control Direction", fontsize=10)
    ax.set_ylabel("Average Obstacle Distance (cm)", fontsize=10)
    ax.set_xticklabels(df["Control Direction"], rotation=45)

    # Inserting a chart into the window
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def click_show_collision_by_date():
    query_last_10 = "SELECT DATE(`Date Time`) AS Collision_Date, COUNT(*) AS Collision_Count FROM sensor_data WHERE `Robot Collision` = 1 GROUP BY Collision_Date ORDER BY Collision_Date ASC LIMIT 10;"
    query_total = "SELECT DATE(`Date Time`) AS Collision_Date, COUNT(*) AS Collision_Count FROM sensor_data WHERE `Robot Collision` = 1 GROUP BY Collision_Date ORDER BY Collision_Date ASC;"
    df_last_10 = get_data(query_last_10)
    df_total = get_data(query_total)

    create_table(df_total)

    if df_last_10.empty:
        print("No data!")
        return

    # Create a window to display the chart
    chart_window = tk.Toplevel(root)
    chart_window.title("Temporal collision statistics")
    chart_window.geometry("1000x600")
    chart_window.iconbitmap("favicon.ico")

    # Create Matplotlib Figure
    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)

    # Representation of data (Bar Chart)
    ax.bar(df_last_10["Collision_Date"],df_last_10["Collision_Count"], color="orange", edgecolor="black")

    ax.set_title("Temporal collision statistics", fontsize=12, fontweight="bold")
    ax.set_xlabel("Collision Date", fontsize=10)
    ax.set_ylabel("Collision Count", fontsize=10)
    ax.set_xticklabels([])

    # Add dynamic labels (date and collision count) above the points
    for i, (date, count) in enumerate(zip(df_last_10["Collision_Date"], df_last_10["Collision_Count"])):
        ax.text(date, count, f"{date.strftime('%Y-%m-%d')}\n{count}",
                ha='center', va='bottom', fontsize=9, color="black")

    # Inserting a chart into the window
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


#Create Main application window
root = tk.Tk()
root.title("Robot Sensor Data")
root.geometry("1300x600")

# Add an icon to the window
root.iconbitmap("roboticon.ico")

# Window Main Frame declaration
main_frame = ttk.Frame(root)
main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=0, column=0, columnspan=3, padx=3, pady=2, sticky="nsew")

# Create buttons
BTN_GetAll_Data = ttk.Button(button_frame, text="  Get All Latest Data   ", command=click_Get_All_Data)
BTN_GetAll_Data.grid(row=0, column=0, padx=3, pady=2, sticky="ew")

BTN_GetCollision_Data = ttk.Button(button_frame, text="Search by Collision Data", command=click_Get_Collision)
BTN_GetCollision_Data.grid(row=0, column=1, padx=3, pady=2, sticky="ew")

BTN_Filter_by_direction = ttk.Button(button_frame, text="Filter datas by Direction", command=click_filter_by_direction)
BTN_Filter_by_direction.grid(row=0, column=2, padx=3, pady=2, sticky="ew")

BTN_filter_date = ttk.Button(button_frame, text="Filter by Date", command=click_filter_by_date)
BTN_filter_date.grid(row=0, column=8, padx=3, pady=2, sticky="ew")

BTN_Filter_Today = ttk.Button(button_frame,text="Today",command=click_filter_today)
BTN_Filter_Today.grid(row=0,column=9, padx=3, pady=2, sticky="ew")

BTN_search_between_distance = ttk.Button(button_frame, text="Search between distance", command=click_search_between_distance)
BTN_search_between_distance.grid(row=1, column=8, padx=3, pady=2, sticky="ew")

BTN_Show_Collision_Distance_Chart = ttk.Button(button_frame, text="Show Collision Chart", command=click_show_collision_distance_chart)
BTN_Show_Collision_Distance_Chart.grid(row=1, column=0, padx=3, pady=2, sticky="ew")

BTN_Show_AVG_Distance_By_direction = ttk.Button(button_frame, text="Show AVG Distance Chart", command=click_avg_distance_by_direction)
BTN_Show_AVG_Distance_By_direction.grid(row=1, column=1, padx=3, pady=2, sticky="ew")

BTN_Show_Collision_By_Date = ttk.Button(button_frame, text="Show Collision By Date Chart", command=click_show_collision_by_date)
BTN_Show_Collision_By_Date.grid(row=1, column=2, padx=3, pady=2, sticky="ew")


#Input Text field for robot movement dirrection filter ex:(FORWARD,BACKWARD,STOP,LEFT,RIGHT)
#Entry text control for movements input text field
def on_entry_click(event, entry, default_text):
    if entry.get() == default_text:
        entry.delete(0, "end")
        entry.config(fg="black")

def on_focus_out(event, entry, default_text):
    if entry.get() == "":
        entry.insert(0, default_text)
        entry.config(fg="gray")

txt_Direction = tk.Entry(button_frame, width=20)
txt_Direction.insert(0,"Enter direction here")
txt_Direction.config(foreground="gray")
txt_Direction.grid(row=0, column=3, padx=5, pady=2, sticky="ew")

txt_Direction.bind("<FocusIn>", lambda event, e=txt_Direction, t="Enter direction here": on_entry_click(event, e, t))
txt_Direction.bind("<FocusOut>", lambda event, e=txt_Direction, t="Enter direction here": on_focus_out(event, e, t))
txt_Direction.bind("<Return>", click_filter_by_direction)

#Filter between two object distance value ex:(minVal = 100, maxVal = 200) -> Object distance datas between 100 and 200 cm.
#low value, minimal value

ttk.Label(button_frame, text="Low value:").grid(row=1, column=4, padx=3, pady=2)

txt_distance_low = tk.Entry(button_frame,width=25)
txt_distance_low.insert(0,"Enter low distance value")
txt_distance_low.config(foreground="gray")
txt_distance_low.grid(row=1,column=5,padx=3, pady=2, sticky="ew")

txt_distance_low.bind("<FocusIn>", lambda event, e=txt_distance_low, t="Enter low distance value": on_entry_click(event, e, t))
txt_distance_low.bind("<FocusOut>", lambda event, e=txt_distance_low, t="Enter low distance value": on_focus_out(event, e, t))


#high value, maximum value
ttk.Label(button_frame, text="High value:").grid(row=1, column=6, padx=3, pady=2)

txt_distance_high = tk.Entry(button_frame,width=25)
txt_distance_high.insert(0,"Enter high distance value")
txt_distance_high.config(foreground="gray")
txt_distance_high.grid(row=1,column=7,padx=3, pady=2, sticky="ew")

txt_distance_high.bind("<FocusIn>", lambda event, e=txt_distance_high, t="Enter high distance value": on_entry_click(event, e, t))
txt_distance_high.bind("<FocusOut>", lambda event, e=txt_distance_high, t="Enter high distance value": on_focus_out(event, e, t))

#Filter datas by Date bettwen the Start and End date
#Filter by Date Strat date
ttk.Label(button_frame, text="Start Date:").grid(row=0, column=4, padx=3, pady=2)
cal_start = DateEntry(button_frame, width=12, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
cal_start.grid(row=0, column=5, padx=3, pady=2, sticky="ew")

#Filter by Date End date
ttk.Label(button_frame, text="End Date:").grid(row=0, column=6, padx=3, pady=2)
cal_end = DateEntry(button_frame, width=12, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
cal_end.grid(row=0, column=7, padx=3, pady=2, sticky="ew")


#Data table field
table_frame = ttk.Frame(main_frame)
table_frame.grid(row=1, column=0, columnspan=3, sticky="nsew")

#Enable window calibration
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(1, weight=1)

#Main cycle start

if __name__ == '__main__':
    root.mainloop()

