import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import threading
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Datamanager:
     def __init__(self,csv_filename,data):
          self.csv_filename = csv_filename
          self.data=data

     def transferdata(self):
      """
        Reads sales data from a CSV file, processes it to compare retail and warehouse sales,
        identifies top 5 items by retail sales, and stores the results in a SQLite database.

        Tables created in SQLite:
        - item_descpription_compare: Contains item description, total retail/warehouse sales,
        and which one is higher.
        - top_5_alcohols: Contains top 5 items by total retail sales.

        Handles:
        - File not found
        - Empty CSV
        - SQLite operational errors
        - Permission issues
    """
      try:
          self.data = pd.read_csv(self.csv_filename)     
          group = self.data.groupby(self.data["ITEM DESCRIPTION"])[["RETAIL SALES","WAREHOUSE SALES"]].sum().reset_index()
          #axis = 1 means result will be written row wise
          group["THEMOST"] = group.apply(lambda row: "Retail wins" if row["RETAIL SALES"] > row["WAREHOUSE SALES"] else "Warehouse wins",axis=1)
         

          newgroup = self.data.groupby(self.data["ITEM DESCRIPTION"])["RETAIL SALES"].sum().reset_index()
          top_five = newgroup.sort_values(by="RETAIL SALES",ascending=False).head(5)

          connect = sqlite3.connect("salesdata.db") 
       
          group.to_sql("item_descpription_compare",connect,if_exists="replace",index=False)
          top_five.to_sql("top_5_alcohols",connect,if_exists="replace",index=False)
          connect.close()
          
          print("Data successfully transferred to SQLite.")
      except FileNotFoundError:
             print("CSV not found.")
      except pd.errors.EmptyDataError:
             print("CSV file is empty.")
      except sqlite3.OperationalError as e:
             print(f"sql lite error:{e}.")
      except PermissionError:
             print("Permission denied when accessing the db file.")
     
     def run_transfer_threaded(self):
          """
            Runs the `transferdata` method in a separate thread to avoid blocking the main thread.
            Useful in GUI applications (e.g., Tkinter) to keep the interface responsive while data is processed.
          """
          thread = threading.Thread(target=self.transferdata)
          thread.start()
       

class Graphmanager:
     #bar
     def show_bar(self,ax):  
       """
            Displays a bar chart comparing the number of items where either retail or warehouse sales are higher.

            Connects to the 'salesdata.db' database and counts how many items are labeled as
            "Retail wins" vs "Warehouse wins" in the 'item_descpription_compare' table.

            Parameters:
            - ax: A matplotlib Axes object where the bar chart will be drawn.

            Exceptions handled:
            - sqlite3.OperationalError: e.g., table not found, syntax error in SQL.
            - sqlite3.IntegrityError: e.g., constraint violations.
            - sqlite3.ProgrammingError: e.g., misuse of the API.
       """
       try:
          connection = sqlite3.connect("salesdata.db")  
          cursor = connection.cursor()
          cursor.execute("select COUNT(*) from item_descpription_compare WHERE THEMOST='Retail wins';")
          retail_info = cursor.fetchone()[0]
          cursor.execute("select COUNT(*) from item_descpription_compare WHERE THEMOST='Warehouse wins';")
          warehouse_info = cursor.fetchone()[0]
          connection.close()
          data = list()
          data.append(retail_info)
          data.append(warehouse_info)
          labels = ["total Retail sales","total Warehouse sales"]
          
          ax.bar(labels,data,color=["blue","orange"])     
          ax.set_title("Retail against Warehouse sales")
          ax.set_ylabel("Count")
       except sqlite3.OperationalError as e:
           print("Operational error:", e)
       except sqlite3.IntegrityError as e:
           print("Constraint failed:", e)
       except sqlite3.ProgrammingError as e:
           print("Programming error:", e)
         

         
     #pie chart plot
     def show_pie(self,ax):
       """
            Displays a pie chart showing the distribution of retail sales among the top 5 alcohol items.

            Connects to the 'salesdata.db' database and retrieves data from the 'top_5_alcohols' table.
            Each slice of the pie chart represents one item's share of total retail sales.

            Parameters:
            - ax: A matplotlib Axes object where the pie chart will be drawn.

            Exceptions handled:
            - sqlite3.OperationalError: e.g., table not found, SQL syntax issues.
            - sqlite3.IntegrityError: e.g., data constraint violations.
            - sqlite3.ProgrammingError: e.g., incorrect use of SQLite API.
            """
       try:
          connection = sqlite3.connect("salesdata.db")
          cursor = connection.cursor()
          cursor.execute("select * from top_5_alcohols;")
          top_info = cursor.fetchall()
          connection.close()
         
          labels = [row[0] for row in top_info]
          sales = [row[1] for row in top_info]
          
          ax.clear()
          ax.pie(sales,labels=labels,autopct="%1.1f%%")
          ax.set_title("Top 5 alcohols - Sales")
       except sqlite3.OperationalError as e:
           print("Operational error:", e)
       except sqlite3.IntegrityError as e:
           print("Constraint failed:", e)
       except sqlite3.ProgrammingError as e:
           print("Programming error:", e)
           
        
     #histogram    
     def show_histogram(self,ax):
       """
        Displays a  histogram showing the distribution of retail and warehouse sales.

        Connects to the 'salesdata.db' database and retrieves retail and warehouse sales data
        from the 'item_descpription_compare' table. Plots a  histogram on a logarithmic scale.

        Parameters:
        - ax: A matplotlib Axes object where the histogram will be drawn.

        Exceptions handled:
        - sqlite3.OperationalError: e.g., table not found, SQL syntax issues.
        - sqlite3.IntegrityError: e.g., data constraint violations.
        - sqlite3.ProgrammingError: e.g., incorrect use of SQLite API.
       """  
       try:
          connection = sqlite3.connect("salesdata.db")
          cursor = connection.cursor()
          cursor.execute("SELECT [RETAIL SALES] FROM item_descpription_compare")
          sales = [row[0] for row in cursor.fetchall()]
          cursor.execute("SELECT [WAREHOUSE SALES] FROM item_descpription_compare")
          sales1 = [row[0] for row in cursor.fetchall()]
          connection.close()

         
         
          ax.hist([sales, sales1], bins=10, color=['green', 'blue'], edgecolor='black', stacked=True, log=True, label=['retail sales', 'warehouse sales'])
          ax.set_title("Distribution of Retail and Warehouse sales")
          ax.set_xlabel("Sales Range")
          ax.set_ylabel("Frequency")
          ax.legend()
       except sqlite3.OperationalError as e:
           print("Operational error:", e)
       except sqlite3.IntegrityError as e:
           print("Constraint failed:", e)
       except sqlite3.ProgrammingError as e:
           print("Programming error:", e)
          
        
    
     def show_horizontal_bar(self,ax):
       """
            Displays a horizontal bar chart of the top 5 alcohol items by retail sales.

            Connects to the 'salesdata.db' database and retrieves data from the 'top_5_alcohols' table.
            Each bar represents one item's total retail sales.

            Parameters:
            - ax: A matplotlib Axes object where the bar chart will be drawn.

            Exceptions handled:
            - sqlite3.OperationalError: e.g., table not found, SQL syntax issues.
            - sqlite3.IntegrityError: e.g., data constraint violations.
            - sqlite3.ProgrammingError: e.g., incorrect use of SQLite API.
       """
       try:
          connection = sqlite3.connect("salesdata.db")
          cursor = connection.cursor()
          cursor.execute("SELECT * FROM top_5_alcohols")
          top_info = cursor.fetchall()
          connection.close()

          labels = [row[0] for row in top_info]
          sales = [row[1] for row in top_info]

         
          ax.bar(labels, sales, color='purple')
          ax.set_title("Top 5 Alcohols by Retail Sales")
          ax.set_xlabel("Retail Sales")
          ax.set_ylabel("Item")
          ax.margins(x=0.1)

         
          ax.set_xticklabels(labels, rotation=45, ha='right')
       except sqlite3.OperationalError as e:
           print("Operational error:", e)
       except sqlite3.IntegrityError as e:
           print("Constraint failed:", e)
       except sqlite3.ProgrammingError as e:
           print("Programming error:", e)
          
        
    
     def show_scatter(self,ax):
       """
            Displays a scatter plot comparing retail and warehouse sales for each item.

            Connects to the 'salesdata.db' database and retrieves paired [RETAIL SALES] and [WAREHOUSE SALES]
            values from the 'item_descpription_compare' table. Each point represents one item's sales comparison.

            Parameters:
            - ax: A matplotlib Axes object where the scatter plot will be drawn.

            Exceptions handled:
            - sqlite3.OperationalError: e.g., table not found, SQL syntax issues.
            - sqlite3.IntegrityError: e.g., data constraint violations.
            - sqlite3.ProgrammingError: e.g., incorrect use of SQLite API.
       """
       try:
          connection = sqlite3.connect("salesdata.db")
          cursor = connection.cursor()
          cursor.execute("SELECT [RETAIL SALES], [WAREHOUSE SALES] FROM item_descpription_compare")
          data = cursor.fetchall()
          connection.close()

          retail = [row[0] for row in data]
          warehouse = [row[1] for row in data]

        
          ax.scatter(retail, warehouse, color='red')
          ax.set_title("Retail and Warehouse Sales")
          ax.set_xlabel("Retail Sales")
          ax.set_ylabel("Warehouse Sales")
          ax.grid(True)
       except sqlite3.OperationalError as e:
           print("Operational error:", e)
       except sqlite3.IntegrityError as e:
           print("Constraint failed:", e)
       except sqlite3.ProgrammingError as e:
           print("Programming error:", e)
          
        
     
     def show_stacked_bar_top5(self,ax):
       """
            Displays a bar chart of the top 5 alcohol items based on retail sales.

            Retrieves [ITEM DESCRIPTION] and [RETAIL SALES] from the 'top_5_alcohols' table
            in the 'salesdata.db' SQLite database and plots a simple (non-stacked) bar chart.

            Parameters:
            - ax: A matplotlib Axes object where the chart will be drawn.

            Notes:
            - This is labeled as a "stacked" bar chart, but it only shows retail sales.
            If warehouse sales are also needed, an actual stacked bar should be implemented.
            
            Exceptions handled:
            - sqlite3.OperationalError: e.g., table or column does not exist.
            - sqlite3.IntegrityError: e.g., database constraint failure.
            - sqlite3.ProgrammingError: e.g., cursor misuse.
    """
       try:
          connection = sqlite3.connect("salesdata.db")
          cursor = connection.cursor()
          cursor.execute("SELECT [ITEM DESCRIPTION], [RETAIL SALES] FROM top_5_alcohols")
          data = cursor.fetchall()
          connection.close()

          items = [row[0] for row in data]
          retail = [row[1] if row[1] is not None else 0 for row in data]

         
          ax.bar(items, retail, label='Retail Sales', color='skyblue')
          ax.set_title("Top 5 Alcohols: Stacked by Retail")
          ax.set_xlabel("Items")
          ax.set_ylabel("Sales")
          ax.tick_params(axis='x', labelrotation=45, labelsize=8)
          ax.margins(x=0.1)
          ax.legend()
       except sqlite3.OperationalError as e:
           print("Operational error:", e)
       except sqlite3.IntegrityError as e:
           print("Constraint failed:", e)
       except sqlite3.ProgrammingError as e:
           print("Programming error:", e)
       


class Form:
   
   def __init__(self, root): 
        """
        Initializes the main GUI for the Sales Visualizer app using Tkinter and Matplotlib.

        Components:
        - Two combo boxes for selecting different types of graphs
        (Top 5 Alcohols and Retail vs Warehouse stats).
        - A Matplotlib canvas embedded in the GUI to display the selected chart.

        Parameters:
        - root: The main Tkinter window (tk.Tk instance).
    """
        self.root = root
        self.root.title("Sales Visualizer")

        self.graph = Graphmanager()

        # Combobox 1
        tk.Label(root, text="Top 5 Alcohols Stats").grid(row=0, column=0, padx=10, pady=5)
        self.combo1 = ttk.Combobox(root, values=["Pie Chart", "Horizontal Bar", "Stacked Bar"])
        self.combo1.grid(row=0, column=1)
        self.combo1.bind("<<ComboboxSelected>>", self.handle_combo1)

        # Combobox 2
        tk.Label(root, text="Retail vs Warehouse Stats").grid(row=1, column=0, padx=10, pady=5)
        self.combo2 = ttk.Combobox(root, values=["Bar Chart", "Scatter Plot", "Histogram"])
        self.combo2.grid(row=1, column=1)
        self.combo2.bind("<<ComboboxSelected>>", self.handle_combo2)

        # Matplotlib figure and canvas
        self.figure = plt.Figure(figsize=(10, 10), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().grid(row=2, column=0, columnspan=2, pady=20)

   def handle_combo1(self, event):
     """
    Handles selection changes in the first combo box (Top 5 Alcohols Stats).

    Based on the user's selection, it:
    - Clears the current Matplotlib figure
    - Adds a new subplot
    - Calls the appropriate graph method from Graphmanager
    - Redraws the chart on the canvas

    Parameters:
    - event: The event object passed by the Tkinter event system.

    Exception Handling:
    - RuntimeError: GUI-related errors, such as drawing to a destroyed canvas.
    - tk.TclError: Tkinter-specific issues, like widget access after destruction.
    - TypeError: Bound function called without required parameters or invalid selection.
    - AttributeError: Issues accessing figure or graph methods.
    """
     try:
        self.figure.clf()  
        ax = self.figure.add_subplot(111)
        
        selected = self.combo1.get()
        if selected == "Pie Chart":
            self.graph.show_pie(ax)
        elif selected == "Horizontal Bar":            
            self.graph.show_horizontal_bar(ax)
        elif selected == "Stacked Bar":              
            self.graph.show_stacked_bar_top5(ax)

        self.figure.tight_layout()
        self.figure.subplots_adjust(bottom=0.25) 
        self.canvas.draw()
     except RuntimeError:
          print("GUI hangs")
     except tk.TclError:
          print("destroyed widget before update")
     except TypeError:
          print("need event param in bound function/no item selected/string in combobox was none")
     except AttributeError:
          print("not cleared figure/blank figure")

   def handle_combo2(self, event):
     """
    Handles selection changes in the second combo box (Retail vs Warehouse Stats).

    Based on the user's selection, it:
    - Clears the current Matplotlib figure
    - Adds a new subplot
    - Calls the appropriate graph method from Graphmanager
    - Redraws the chart on the canvas

    Parameters:
    - event: The event object passed by the Tkinter event system.

    Exception Handling:
    - RuntimeError: GUI-related errors, such as drawing to a destroyed canvas.
    - tk.TclError: Tkinter-specific issues, like widget access after destruction.
    - TypeError: Bound function called without required parameters or invalid selection.
    - AttributeError: Issues accessing figure or graph methods.
    """
     try:
        self.figure.clf()  
        ax = self.figure.add_subplot(111)
        
        selected = self.combo2.get()
        if selected == "Bar Chart":
          
            self.graph.show_bar(ax)
        elif selected == "Scatter Plot":
          
            self.graph.show_scatter(ax)
        elif selected == "Histogram":
           
            self.graph.show_histogram(ax)
        self.figure.tight_layout()
        self.figure.subplots_adjust(bottom=0.25) 
        self.canvas.draw() 
     except RuntimeError:
          print("GUI hangs")
     except tk.TclError:
          print("destroyed widget before update")
     except TypeError:
          print("need event param in bound function/no item selected/string in combobox was none")
     except AttributeError:
          print("not cleared figure/blank figure")



          

     
#main program
class MainController(Datamanager, Graphmanager, Form):
     def __init__(self):
          """
            Initializes the application by:
            - Creating an empty DataFrame
            - Initializing a Datamanager to load and transfer CSV data to SQLite in a background thread
            - Setting up the main Tkinter window and starting the GUI event loop

            Exception handling covers common I/O and GUI errors.
          """
          try:  
            df = pd.DataFrame()
         
            my_obj = Datamanager("Data.csv",df)
            my_obj.run_transfer_threaded()

            root = tk.Tk()
            form = Form(root)
            root.mainloop()
          except FileNotFoundError:
                print("CSV not found.")
          except pd.errors.EmptyDataError:
                print("empty csv file")
          except PermissionError:
                print("not permission to I/O file")
          except RuntimeError:
                print("GUI hangs")
          except tk.TclError:
                print("destroyed widget before update")


Program = MainController()

