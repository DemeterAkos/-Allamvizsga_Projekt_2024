import mysql.connector
import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkcalendar import DateEntry
from datetime import date
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import numpy as np

#Query select temporal global variable number For Export Selected Data query to CSV file
tmp_query_nr = 0

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

    try:
        conn = connect_to_database()
        update_status("✅ Connected to database", "green")

    except Exception as err:
        print(f"Database connection failed: {err}")
        update_status("❌ Database connection failed!", "red")
        messagebox.showerror("Error", f"Connection failed: {str(err)}")
        return pd.DataFrame()

    try:
        df = pd.read_sql(query, conn, params=params)
        update_status(f"📊 Query executed: {query}", "blue")
    except Exception as err:
        print(f"Query execution failed: {err}")
        messagebox.showerror("Error", f"Query execution failed: {str(err)}")
        update_status("⚠️Query execution failed!", "orange")
        df = pd.DataFrame() #Empty DataFrame, if query fails

    finally:
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

#Update Status_Bar txt
def update_status(text, color):
    status_bar.config(text=text, foreground=color)


#Get data at the touch of a button
#Functions declaration for buttuns event
def click_Get_All_Data():
    global tmp_query_nr
    # Make query select
    query = "SELECT * FROM sensor_data ORDER BY `Date Time` DESC"
    df = get_data(query)
    # Refresh table output
    create_table(df)
    tmp_query_nr = 1


def click_Get_Collision():
    global tmp_query_nr
    # Make query select
    df = get_data("SELECT * FROM sensor_data WHERE `Robot Collision` = 1 ORDER BY `Date Time` DESC")
    # Refresh table output
    create_table(df)

    tmp_query_nr = 2

def click_filter_by_direction(event = None):
    global tmp_query_nr
    #Get direction value from Input field
    direction = txt_Direction.get().strip()

    if direction:
        # Make query select
        query = "SELECT * FROM sensor_data WHERE `Control direction` = %s ORDER BY `Date Time` DESC"
        df = get_data(query,(direction,))
        # Refresh table output
        create_table(df)
        tmp_query_nr = 3
    else:
        print("Please enter a direction!")  # Error message

def click_filter_by_date():
    global tmp_query_nr
    start_date = cal_start.get_date().strftime("%Y-%m-%d")
    end_date = cal_end.get_date().strftime("%Y-%m-%d")
    # Make query select
    query = "SELECT * FROM sensor_data WHERE `Date Time` BETWEEN %s AND %s ORDER BY `Date Time` DESC"
    df = get_data(query, (start_date, end_date))
    # Refresh table output
    create_table(df)
    tmp_query_nr = 4

def click_filter_today():
    global tmp_query_nr
    # Get today's date
    today = date.today()

    # Modify query to filter only by the date part
    query = "SELECT * FROM sensor_data WHERE DATE(`Date Time`) = %s ORDER BY `Date Time` DESC"
    df = get_data(query, (today,))

    # Refresh table output
    create_table(df)
    tmp_query_nr = 5


def click_search_between_distance():
    global tmp_query_nr
    low_distance_value = txt_distance_low.get().strip()
    high_distance_value = txt_distance_high.get().strip()

    if low_distance_value and high_distance_value:  #If has value in Input field
        # Make query select
        query = "SELECT * FROM sensor_data WHERE `Obstacle Distance`BETWEEN %s AND %s ORDER BY `Obstacle Distance` DESC"
        df = get_data(query, (low_distance_value,high_distance_value))
        # Refresh table output
        create_table(df)
        tmp_query_nr = 6
    else:
        print("Please enter low and high distance value!")


def click_show_collision_distance_chart():
    global tmp_query_nr
    # Make query select
    query = "SELECT `Obstacle Distance` FROM sensor_data WHERE `Robot Collision` = 1"
    query_count = "SELECT Count(*) AS 'Total Collision' FROM sensor_data WHERE `Robot Collision` = 1"
    df = get_data(query)
    df1 = get_data(query_count)
    # Refresh table output
    create_table(df1)
    tmp_query_nr = 7

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
    global tmp_query_nr
    #Make query select
    query = "SELECT `Control Direction`, AVG(`Obstacle Distance`) AS Avg_Distance FROM sensor_data GROUP BY `Control Direction` ORDER BY Avg_Distance ASC;"
    df = get_data(query)
    create_table(df)
    tmp_query_nr = 8

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
    ax.set_xticklabels(df["Control Direction"], rotation=15)

    # Inserting a chart into the window
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def click_cillision_direction_switch_chart():
    global tmp_query_nr
    #Make query select
    query = "SELECT COUNT(*) AS Total_collision ,`Robot Collision Switch` FROM sensor_data GROUP BY `Robot Collision Switch`"
    df = get_data(query)
    create_table(df)
    tmp_query_nr = 9

    if df.empty:
        print("No data!")
        return

    df = df[df["Robot Collision Switch"] != ""]
    df = df[df["Robot Collision Switch"] != "None"]

    if df.empty:
        print("No valid collision data!")
        return

    # Create a window to display the chart
    chart_window = tk.Toplevel(root)
    chart_window.title("Collision Direction Switch Chart")
    chart_window.geometry("1000x600")
    chart_window.iconbitmap("favicon.ico")

    # Create Matplotlib Figure
    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)

    # Representation of data (Bar Chart)
    ax.bar(df["Robot Collision Switch"], df["Total_collision"], color="green", edgecolor="black")

    ax.set_title("Collision Direction Switch Chart",fontsize=12, fontweight="bold")
    ax.set_xlabel("Robot Collision Direction Switch", fontsize=10)
    ax.set_ylabel("Total collision", fontsize=10)
    ax.set_xticklabels(df["Robot Collision Switch"], rotation=15)

    # Inserting a chart into the window
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def click_show_collision_by_date():
    global tmp_query_nr
    # SQL query statement
    query_last_10 = """
        SELECT DATE_FORMAT(`Date Time`, '%Y-%m-%d %H:%i') AS Collision_Minute, 
               COUNT(*) AS Collision_Count 
        FROM sensor_data 
        WHERE `Robot Collision` = 1 
        GROUP BY Collision_Minute 
        ORDER BY Collision_Minute ASC 
        LIMIT 10;
    """

    query_total = """
        SELECT DATE_FORMAT(`Date Time`, '%Y-%m-%d %H:%i') AS Collision_Minute, 
               COUNT(*) AS Collision_Count 
        FROM sensor_data 
        WHERE `Robot Collision` = 1 
        GROUP BY Collision_Minute 
        ORDER BY Collision_Minute ASC;
    """

    df_last_10 = get_data(query_last_10)
    df_total = get_data(query_total)

    create_table(df_total)

    tmp_query_nr = 10

    if df_last_10.empty:
        print("No data!")
        return

    chart_window = tk.Toplevel(root)
    chart_window.title("Collision Statistics by Minute")
    chart_window.geometry("1200x600")
    chart_window.iconbitmap("favicon.ico")

    # Create Matplotlib Figure
    fig = Figure(figsize=(10, 5), dpi=100)
    ax = fig.add_subplot(111)

    # Representation of data (Bar Chart)
    ax.bar(df_last_10["Collision_Minute"], df_last_10["Collision_Count"], color="orange", edgecolor="black")

    ax.set_title("Collision Statistics by Minute", fontsize=12, fontweight="bold")
    ax.set_xlabel("Time per minutes", fontsize=10)
    ax.set_ylabel("Collision Count", fontsize=10)


    ax.set_xticks(range(len(df_last_10["Collision_Minute"])))
    ax.set_xticklabels(df_last_10["Collision_Minute"], rotation=15, ha="right", fontsize=8)


    for i, (minute, count) in enumerate(zip(df_last_10["Collision_Minute"], df_last_10["Collision_Count"])):
        ax.text(i, count, str(count), ha='center', va='bottom', fontsize=9, color="black")

    # Inserting a chart into the window
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def click_movement_distribution_pie_chart():
    global tmp_query_nr
    # SQL query select
    query = """
        SELECT `Control Direction`, 
               COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sensor_data) AS Percentage
        FROM sensor_data
        GROUP BY `Control Direction`
        ORDER BY Percentage DESC;
    """
    df = get_data(query)

    create_table(df)

    tmp_query_nr = 11

    if df.empty:
        print("No data available!")
        return

    #Create window fror chart
    chart_window = tk.Toplevel(root)
    chart_window.title("Movement Direction Distribution")
    chart_window.geometry("800x600")
    chart_window.iconbitmap("favicon.ico")


    fig = Figure(figsize=(6, 6), dpi=100)
    ax = fig.add_subplot(111)

    # Show pie chart
    ax.pie(df["Percentage"], labels=df["Control Direction"], autopct="%1.1f%%",
           colors=["blue", "red", "orange", "purple", "cyan"],
           startangle=140, wedgeprops={"edgecolor": "black"})

    ax.set_title("Movement Direction Percentage Distribution [%]", fontsize=12, fontweight="bold")

    # Inserting a chart into the window
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def click_export_table_to_csv():

    #CSV file data select field
    #Get all latest data query for csv
    if tmp_query_nr == 1:
        query = "SELECT * FROM sensor_data ORDER BY `Date Time` DESC"
        df = get_data(query)

    #Collision Datas for csv
    elif tmp_query_nr == 2:
        query = "SELECT * FROM sensor_data WHERE `Robot Collision` = 1 ORDER BY `Date Time` DESC"
        df = get_data(query)

    #Direction Data query for csv
    elif tmp_query_nr == 3:
        direction = txt_Direction.get().strip()
        query = "SELECT * FROM sensor_data WHERE `Control direction` = %s ORDER BY `Date Time` DESC"
        df = get_data(query, (direction,))

    #Datas between two date for csv
    elif tmp_query_nr == 4:
        start_date = cal_start.get_date().strftime("%Y-%m-%d")
        end_date = cal_end.get_date().strftime("%Y-%m-%d")
        # Make query select
        query = "SELECT * FROM sensor_data WHERE `Date Time` BETWEEN %s AND %s ORDER BY `Date Time` DESC"
        df = get_data(query, (start_date, end_date))

    #Today Datas query select for csv
    elif tmp_query_nr == 5:
        today = date.today()
        # Modify query to filter only by the date part
        query = "SELECT * FROM sensor_data WHERE DATE(`Date Time`) = %s ORDER BY `Date Time` DESC"
        df = get_data(query, (today,))

    #Datas between two obstacle distance value query select for csv
    elif tmp_query_nr == 6:
        low_distance_value = txt_distance_low.get().strip()
        high_distance_value = txt_distance_high.get().strip()
        query = "SELECT * FROM sensor_data WHERE `Obstacle Distance`BETWEEN %s AND %s ORDER BY `Obstacle Distance` DESC"
        df = get_data(query, (low_distance_value, high_distance_value))

    #Collision by distance statistic chart values for csv
    elif tmp_query_nr == 7:
        query_count = "SELECT Count(*) AS 'Total Collision' FROM sensor_data WHERE `Robot Collision` = 1"
        df = get_data(query_count)

    #Average obstacle distance by direction chart values for csv
    elif tmp_query_nr == 8:
        query = "SELECT `Control Direction`, AVG(`Obstacle Distance`) AS Avg_Distance FROM sensor_data GROUP BY `Control Direction` ORDER BY Avg_Distance ASC;"
        df = get_data(query)

    #Total collision by direction switches data query select for csv
    elif tmp_query_nr == 9:
        query = "SELECT COUNT(*) AS Total_collision ,`Robot Collision Switch` FROM sensor_data GROUP BY `Robot Collision Switch`"
        df = get_data(query)

    #Total collisions by date
    elif tmp_query_nr == 10:
        query = """
                SELECT DATE_FORMAT(`Date Time`, '%Y-%m-%d %H:%i') AS Collision_Minute, 
                       COUNT(*) AS Collision_Count
                FROM sensor_data 
                WHERE `Robot Collision` = 1 
                GROUP BY Collision_Minute 
                ORDER BY Collision_Minute ASC;
            """

        df = get_data(query)

    #Movement direction percentage statistic chart data query select to export csv
    elif tmp_query_nr == 11:
        query = """
                SELECT `Control Direction`, 
                       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sensor_data) AS Percentage
                FROM sensor_data
                GROUP BY `Control Direction`
                ORDER BY Percentage DESC;
            """
        df = get_data(query)

    if df.empty:
        messagebox.showerror("Error", "No data to export!")
        return

    # Open file save dialog
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All Files", "*.*")],
        title="Save CSV File"
    )

    # If the user did not choose a filename, we exit
    if not file_path:
        return

    try:
        # Save CSV file
        df.to_csv(file_path, index=False, encoding="utf-8")
        messagebox.showinfo("Success", f"Data exported successfully to:\n{file_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export data!\n{str(e)}")

###################################################################################################################

#Create Main application window
root = tk.Tk()
root.title("Robot Sensor Data")
root.geometry("1380x600")

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

BTN_search_between_distance = ttk.Button(button_frame, text="Search between obstacle distance", command=click_search_between_distance)
BTN_search_between_distance.grid(row=1, column=8, padx=3, pady=2, sticky="ew")

BTN_Show_Collision_Distance_Chart = ttk.Button(button_frame, text="Show Collision Chart", command=click_show_collision_distance_chart)
BTN_Show_Collision_Distance_Chart.grid(row=1, column=0, padx=3, pady=2, sticky="ew")

BTN_Show_AVG_Distance_By_direction = ttk.Button(button_frame, text="Show AVG Distance Chart", command=click_avg_distance_by_direction)
BTN_Show_AVG_Distance_By_direction.grid(row=1, column=1, padx=3, pady=2, sticky="ew")

BTN_Show_Collision_By_Date = ttk.Button(button_frame, text="Show Collision By Date Chart", command=click_show_collision_by_date)
BTN_Show_Collision_By_Date.grid(row=1, column=2, padx=3, pady=2, sticky="ew")

BTN_Show_Collision_Direction_Switch_Chart = ttk.Button(button_frame, text="Show Collision By Direction", command=click_cillision_direction_switch_chart)
BTN_Show_Collision_Direction_Switch_Chart.grid(row=1, column=3,padx=3, pady=2, sticky="ew")

BTN_Show_movement_distribution_pie_chart = ttk.Button(button_frame, text="Show movement distribution", command=click_movement_distribution_pie_chart)
BTN_Show_movement_distribution_pie_chart.grid(row=2, column=0,padx=3, pady=2, sticky="ew")

BTN_Export_Data_CSV = ttk.Button(button_frame, text="Export to CSV", command=click_export_table_to_csv)
BTN_Export_Data_CSV.grid(row=2, column=2, padx=3, pady=2, sticky="ew")


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

#Status Bar, status label
status_bar = ttk.Label(main_frame, text="🔄 Connecting to database...", anchor="w", font=("Arial", 10))
status_bar.grid(row=99, column=0, sticky="ew", padx=5, pady=5)


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

