import tkinter as tk
from tkinter import ttk, Tk, Text, Listbox, Menubutton, Menu, IntVar, NO, W, RIGHT, Y
from PIL import ImageTk, Image
import sys
from ttkthemes import ThemedTk
from main_module_backtest import Backtest
from global_variable_module_backtest import *
import global_variable_module_backtest as global_vars
import data_import_module_backtest as data_import
from data_import_module_backtest import asset_prices  # Importez asset_prices
from data_import_module_backtest import df_global
import execution_module_backtest
import analyses_module_backtest
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import mplfinance as mpf
import pandas as pd
import os

# Creating the main window
root = ThemedTk(theme="aqua")
root.title("Trading Bot")

# Creating the tab bar
tab_control = ttk.Notebook(root)

# Home tab
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Home')

# Main tab
tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text='Main')

# Closed positions tab
tab3 = ttk.Frame(tab_control)
tab_control.add(tab3, text='Closed Positions')

# Analysis tab
tab5 = ttk.Frame(tab_control)
tab_control.add(tab5, text='Analysis')

# Variables modification tab
tab4 = ttk.Frame(tab_control)
tab_control.add(tab4, text='Settings')

tab_control.pack(expand=1, fill='both')

#----------------------------------------------------------------------------------------------------------------------------

# Main Tab
welcome_label = ttk.Label(tab1, text="Welcome to LH Backtest", font=("Arial", 24))
welcome_label.pack(pady=10)

# Charger l'image
image = Image.open('LH_logo.png')

# Réduire la taille de l'image (par exemple, réduire de moitié)
new_width = int(image.width / 2)
new_height = int(image.height / 2)
image = image.resize((new_width, new_height))

photo = ImageTk.PhotoImage(image)
image_label = ttk.Label(tab1, image=photo)
image_label.image = photo
image_label.pack()

def quit_app():
    global backtest
    if backtest is not None:
        backtest.stop()
        backtest.running = False  # Ensure that the backtest is no longer running
    if update_ui_ref:
        root.after_cancel(update_ui_ref)
    if update_all_values_ref:
        root.after_cancel(update_all_values_ref)
    if refresh_ref:
        tab3.after_cancel(refresh_ref)
    root.destroy()
    sys.exit(0)

# Adding a button to exit the application
exit_button = ttk.Button(tab1, text="Exit Application", command=quit_app)
exit_button.pack(pady=20)

#------------------------------------------------------------------------------------------------------------------------------

# Main Tab 
main_frame = ttk.Frame(tab2)
main_frame.pack(fill='both', expand=1)

# Left frame
left_frame = ttk.Frame(main_frame)
left_frame.pack(side='left', fill='both', expand=True)

global backtest
backtest = None  # Set backtest to None initially
global update_ui_ref, update_all_values_ref, refresh_ref
update_ui_ref = None
update_all_values_ref = None
refresh_ref = None

def start_stop_backtest():
    global backtest, update_ui_ref
    num_candles_input = candle_entry.get()  # Retrieve the number of candles from the entry
    num_candles = int(num_candles_input)  # Convert to integer

    if backtest is not None and backtest.running:
        backtest.stop()
        backtest = None  # Set backtest to None after stopping
    else:
        # Get the selected intervals and symbols
        selected_intervals = [k for k, v in time_intervals.items() if v.get()]
        selected_symbols = [k for k, v in trading_symbols.items() if v.get()]
        # Initialize Backtest with the selected intervals and symbols, num_candles, and the output widgets
        backtest = Backtest(root, backtest_output=backtest_output, positions_treeview=positions_treeview, num_candles=num_candles, intervals=selected_intervals, symbols=selected_symbols)
        backtest.start()
        update_ui_ref = root.after(1000, update_ui)  # Begin the update_ui loop once the backtest has started

def get_selected_symbol():
    for symbol, var in trading_symbols.items():
        if var.get() == 1:
            return symbol
    return None  # No symbol is selected

def get_selected_interval():
    for interval, var in time_intervals.items():
        if var.get() == 1:
            return interval
    return None  # No interval is selected

def update_ui():
    # Update the positions treeview from the queue
    if backtest is not None:
        # Clear existing open positions from the TreeView
        positions_treeview.delete(*positions_treeview.get_children())

        # Update closed positions (assuming backtest.queue stores closed positions)
        while not backtest.queue.empty():
            closed_position = backtest.queue.get()
            backtest_output.insert('end', f"Closed position: Symbol: {closed_position['symbol']}, Opening Time: {closed_position['opening_time']}\n")
            backtest_output.see('end')  # Scroll to the end of the text area

        # Update open positions by calling update_open_positions function
        update_open_positions()
        update_analysis_labels()

        # Get the selected symbol and interval
        selected_symbol = get_selected_symbol()
        selected_interval = get_selected_interval()
        if selected_symbol and selected_interval:
            plot_portfolio_graph(selected_symbol, selected_interval)
        else:
            plot_portfolio_graph()  # If no symbol or interval is selected, plot the default portfolio graph

        # Call update_ui again after 1 second if the backtest is still running
        if backtest.running:
            root.after(1000, update_ui)
        else:
            root.after_cancel(update_ui_ref)

backtest_button = ttk.Button(left_frame, text="Start / End the Backtest", command=start_stop_backtest)
backtest_button.pack(pady=10)

# Create a dict where keys are the time intervals and the values are IntVar that keep track of whether the interval is selected
time_intervals = {"1m": tk.IntVar(), "5m": tk.IntVar(), "15m": tk.IntVar(), "30m": tk.IntVar(), "1h": tk.IntVar(), "4h": tk.IntVar(), "1d": tk.IntVar(), "1w": tk.IntVar()}
trading_symbols = {symbol: tk.IntVar() for symbol in TRADING_SYMBOLS} # Creating a dict for symbols

time_label = ttk.Label(left_frame, text="Select time interval")
time_label.pack()

# Create a menu with checkbutton items for intervals
time_menu = tk.Menubutton(left_frame, text="Intervals", relief="raised")
time_menu.pack()
time_menu.menu = tk.Menu(time_menu, tearoff=False)
time_menu["menu"] = time_menu.menu

# Add each time interval as a checkbutton item
for interval in time_intervals:
    time_menu.menu.add_checkbutton(label=interval, variable=time_intervals[interval])

# Create a menu with checkbutton items for symbols
symbol_label = ttk.Label(left_frame, text="Select symbols")
symbol_label.pack()
symbol_menu = tk.Menubutton(left_frame, text="Symbols", relief="raised")
symbol_menu.pack()
symbol_menu.menu = tk.Menu(symbol_menu, tearoff=False)
symbol_menu["menu"] = symbol_menu.menu

# Add each symbol as a checkbutton item
for symbol in trading_symbols:
    symbol_menu.menu.add_checkbutton(label=symbol, variable=trading_symbols[symbol])

candle_label = ttk.Label(left_frame, text="Number of candles to trace")
candle_label.pack()
candle_entry = ttk.Entry(left_frame)
candle_entry.pack()

positions_label = ttk.Label(left_frame, text="Current positions")
positions_label.pack()

# Function to update open positions
def update_open_positions():
    # Remove all existing entries
    for item in positions_treeview.get_children():
        positions_treeview.delete(item)

    # Use the list of active trades from the execution module
    open_positions = execution_module_backtest.active_trades

    # Insert open positions into the TreeView
    for position in open_positions:
        positions_treeview.insert('', 'end', values=(
            position['symbol'], position['interval'], position['trading_signal'], '{:.2f}'.format(position['size']),
            '{:.4f}'.format(position['entry_price']), '{:.4f}'.format(position['sl']), '{:.4f}'.format(position['tp']),
            position['opening_time'].strftime("%Y-%m-%d %H:%M"),  # Remove seconds
            '{:.2f}'.format(position['latent_pnl']),
        ))

# Use the list of active trades from the execution module
open_positions = execution_module_backtest.active_trades

# Create a TreeView for open positions
positions_treeview = ttk.Treeview(left_frame)
positions_treeview.pack(side='top', fill='both', expand=True)

# Setting up columns
positions_treeview['columns'] = ('Symbol', 'Interval', 'Trade Type', 'Size', 'Entry Price', 'Stop Loss', 'Take Profit', 'Opening Time', 'Latent PNL')

# Setting up headers
positions_treeview.column('#0', width=0, stretch=NO)
positions_treeview.column('Symbol', anchor=W, width=60)
positions_treeview.column('Interval', anchor=W, width=60)
positions_treeview.column('Trade Type', anchor=W, width=90)
positions_treeview.column('Size', anchor=W, width=60)
positions_treeview.column('Entry Price', anchor=W, width=80)
positions_treeview.column('Stop Loss', anchor=W, width=60)
positions_treeview.column('Take Profit', anchor=W, width=60)
positions_treeview.column('Opening Time', anchor=W, width=100)
positions_treeview.column('Latent PNL', anchor=W, width=60)

# Setting up column names
positions_treeview.heading('#0', text='', anchor=W)
positions_treeview.heading('Symbol', text='Symbol', anchor=W)
positions_treeview.heading('Interval', text='Interval', anchor=W)
positions_treeview.heading('Trade Type', text='Trade Type', anchor=W)
positions_treeview.heading('Size', text='Size', anchor=W)
positions_treeview.heading('Entry Price', text='Entry Price', anchor=W)
positions_treeview.heading('Stop Loss', text='Stop Loss', anchor=W)
positions_treeview.heading('Take Profit', text='Take Profit', anchor=W)
positions_treeview.heading('Opening Time', text='Opening Time', anchor=W)
positions_treeview.heading('Latent PNL', text='Latent PNL', anchor=W)

# Create a scrollbar if needed for positions_treeview
open_positions_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=positions_treeview.yview)
open_positions_scrollbar.pack(side=RIGHT, fill=Y)
positions_treeview.configure(yscrollcommand=open_positions_scrollbar.set)

# Right Frame
right_frame = ttk.Frame(main_frame)
right_frame.pack(side='right', fill='both', expand=True)

# Defining necessary functions

def update_gains_losses_and_final_capital():
    pnl_latent = execution_module_backtest.PNL_LATENT_TOTAL
    pnl_realized = execution_module_backtest.PNL_TOTAL
    initial_balance = global_vars.INITIAL_CAPITAL  # Assuming INITIAL_CAPITAL is the initial capital

    final_balance = initial_balance + pnl_latent + pnl_realized
    execution_module_backtest.ACCOUNT_BALANCE = final_balance  # Update the global variable, if necessary

    gains_losses_value_label['text'] = '{:.2f}'.format(pnl_latent)
    realized_gains_losses_value_label['text'] = '{:.2f}'.format(pnl_realized)
    final_capital_value_label['text'] = '{:.2f}'.format(final_balance)

def update_available_capital():
    # Get the available capital from the execution module
    available_capital = execution_module_backtest.AVAILABLE_CAPITAL

    # Update the display in the user interface
    available_capital_value_label['text'] = '{:.2f}'.format(available_capital)

# Frame for capital information
capital_frame = ttk.Frame(right_frame)
capital_frame.pack(side='top', fill='x', pady=5)  # Fill horizontally

initial_capital_frame = ttk.Frame(capital_frame)
initial_capital_frame.pack(side='top', fill='x')
initial_capital_label = ttk.Label(initial_capital_frame, text="Initial Capital")
initial_capital_label.pack(side='left')

# Display the value of the initial capital from the INITIAL_CAPITAL variable
initial_capital_value_label = ttk.Label(initial_capital_frame, text=str(global_vars.INITIAL_CAPITAL))
initial_capital_value_label.pack(side='left')

# Frame for available capital
available_capital_frame = ttk.Frame(capital_frame)
available_capital_frame.pack(side='top', fill='x')
available_capital_label = ttk.Label(available_capital_frame, text="Available Capital")
available_capital_label.pack(side='left')
available_capital_value_label = ttk.Label(available_capital_frame, text="10000")  # Default value
available_capital_value_label.pack(side='left')

gains_losses_frame = ttk.Frame(capital_frame)
gains_losses_frame.pack(side='top', fill='x')
gains_losses_label = ttk.Label(gains_losses_frame, text="Latent Gains and Losses")
gains_losses_label.pack(side='left')
gains_losses_value_label = ttk.Label(gains_losses_frame, text="0")  # Modify the value as needed
gains_losses_value_label.pack(side='left')

realized_gains_losses_frame = ttk.Frame(capital_frame)
realized_gains_losses_frame.pack(side='top', fill='x')
realized_gains_losses_label = ttk.Label(realized_gains_losses_frame, text="Realized Gains and Losses")
realized_gains_losses_label.pack(side='left')
realized_gains_losses_value_label = ttk.Label(realized_gains_losses_frame, text="0")  # Default value
realized_gains_losses_value_label.pack(side='left')

final_capital_frame = ttk.Frame(capital_frame)
final_capital_frame.pack(side='top', fill='x')
final_capital_label = ttk.Label(final_capital_frame, text="Final Capital")
final_capital_label.pack(side='left')
final_capital_value_label = ttk.Label(final_capital_frame, text="100000")  # Modify the value as needed
final_capital_value_label.pack(side='left')

backtest_label = ttk.Label(right_frame, text="Ongoing Backtest")
backtest_label.pack()

# Adding Text widget for backtest display
backtest_output = Text(right_frame)
backtest_output.pack(fill='both', expand=True)  # Fill both horizontally and vertically

# Redirecting standard output to Text widget
class IORedirector(object):
    def __init__(self, text_area):
        self.text_area = text_area

class StdoutRedirector(IORedirector):
    def write(self, str):
        self.text_area.insert('end', str)
        self.text_area.see('end')
    
    def flush(self):
        pass

sys.stdout = StdoutRedirector(backtest_output)

# You can call this function when you need to update the user interface with the latest values
def update_all_values():
    global update_all_values_ref
    update_gains_losses_and_final_capital()
    update_available_capital()

    # Schedule a new call to this function after 2 seconds
    update_all_values_ref = root.after(2000, update_all_values)

#----------------------------------------------------------------------------------------------------------------------------
# Closed Positions Tab

def update_closed_positions():
    # Delete all existing entries
    for item in closed_positions_treeview.get_children():
        closed_positions_treeview.delete(item)

    # Use the list of closed trades from the execution module
    closed_positions = execution_module_backtest.closed_trades

    # Insert the closed positions into the TreeView
    for position in closed_positions:
        closed_positions_treeview.insert('', 'end', values=(
            position['symbol'], position['interval'], position['trading_signal'], '{:.2f}'.format(position['size']),
            '{:.4f}'.format(position['entry_price']), '{:.4f}'.format(position['sl']), '{:.4f}'.format(position['tp']),
            position['opening_time'],
            '{:.4f}'.format(position['closing_price']), '{:.2f}'.format(position['pnl'])
        ))

# Add this function to update realized gains and losses
def update_realized_gains_losses():
    realized_pnl = 0
    for item in closed_positions_treeview.get_children():
        trade = closed_positions_treeview.item(item)
        pnl = float(trade['values'][-1])  # retrieve the PNL from the last column
        realized_pnl += pnl

    realized_gains_losses_value_label['text'] = str(realized_pnl)

# Creating a TreeView inside the Closed Positions tab
closed_positions_treeview = ttk.Treeview(tab3)
closed_positions_treeview.pack(side='top', fill='both', expand=True)

# Configuring the columns
closed_positions_treeview['columns'] = ('Symbol', 'Interval', 'Trade Type', 'Size', 'Entry Price', 'Stop Loss', 'Take Profit', 'Opening Time', 'Closing Price', 'PNL')

# Configuring the headers
closed_positions_treeview.column('#0', width=0, stretch=NO)
closed_positions_treeview.column('Symbol', anchor=W, width=100)
closed_positions_treeview.column('Interval', anchor=W, width=100)
closed_positions_treeview.column('Trade Type', anchor=W, width=120)
closed_positions_treeview.column('Size', anchor=W, width=80)
closed_positions_treeview.column('Entry Price', anchor=W, width=120)
closed_positions_treeview.column('Stop Loss', anchor=W, width=100)
closed_positions_treeview.column('Take Profit', anchor=W, width=100)
closed_positions_treeview.column('Opening Time', anchor=W, width=140)
closed_positions_treeview.column('Closing Price', anchor=W, width=150)
closed_positions_treeview.column('PNL', anchor=W, width=140)

# Configuring the column names
closed_positions_treeview.heading('#0', text='', anchor=W)
closed_positions_treeview.heading('Symbol', text='Symbol', anchor=W)
closed_positions_treeview.heading('Interval', text='Interval', anchor=W)
closed_positions_treeview.heading('Trade Type', text='Trade Type', anchor=W)
closed_positions_treeview.heading('Size', text='Size', anchor=W)
closed_positions_treeview.heading('Entry Price', text='Entry Price', anchor=W)
closed_positions_treeview.heading('Stop Loss', text='Stop Loss', anchor=W)
closed_positions_treeview.heading('Take Profit', text='Take Profit', anchor=W)
closed_positions_treeview.heading('Opening Time', text='Opening Time', anchor=W)
closed_positions_treeview.heading('Closing Price', text='Closing Price', anchor=W)
closed_positions_treeview.heading('PNL', text='PNL', anchor=W)

# Create a scrollbar if needed
scrollbar = ttk.Scrollbar(tab3, orient="vertical", command=closed_positions_treeview.yview)
scrollbar.pack(side=RIGHT, fill=Y)
closed_positions_treeview.configure(yscrollcommand=scrollbar.set)

# Calls the update function every 10 seconds
def refresh():
    global refresh_ref
    update_gains_losses_and_final_capital()
    update_closed_positions()
    update_realized_gains_losses()
    refresh_ref = tab3.after(10000, refresh)  # 10000 milliseconds = 10 seconds

# Start refreshing
refresh()

#----------------------------------------------------------------------------------------------------------------------------
# Analysis Tab

def update_analysis_labels():
    data = analyses_module_backtest.get_analysis_data()
    total_trades_label.config(text=f"Total trades: {data['winning_trades'] + data['losing_trades']}")
    total_pnl_label.config(text=f"Total PnL: {data['total_pnl']}")
    initial_capital_label.config(text=f"Initial Capital: {data['initial_capital']}")
    final_capital_label.config(text=f"Final Capital: {data['final_capital']}")
    win_rate_label.config(text=f"Win Rate: {data['win_rate'] * 100:.2f}%")
    max_profit_label.config(text=f"Max Profit: {data['max_profit']}")
    max_drawdown_label.config(text="Max drawdown: N/A")  # If you don't calculate the max drawdown
    winning_trades_label.config(text=f"Winning Trades: {data['winning_trades']}")
    losing_trades_label.config(text=f"Losing Trades: {data['losing_trades']}")
    total_win_pnl_label.config(text=f"Total Win PnL: {data['total_win_pnl']}")
    total_loss_pnl_label.config(text=f"Total Loss PnL: {data['total_loss_pnl']}")
    sell_short_trades_label.config(text=f"Short Sell Trades: {data['sell_short_trades']}")
    buy_long_trades_label.config(text=f"Long Buy Trades: {data['buy_long_trades']}")
    total_sell_short_pnl_label.config(text=f"Total Short Sell PnL: {data['total_sell_short_pnl']}")
    total_buy_long_pnl_label.config(text=f"Total Long Buy PnL: {data['total_buy_long_pnl']}")
    portfolio_returns_label.config(text=f"Portfolio Return: {data['portfolio_return']:.2f}%")
    avg_profit_label.config(text=f"Average Profit: {data['avg_profit']:.2f}")
    max_drawdown_label.config(text=f"Max drawdown: {data['max_drawdown'] * 100:.2f}%")  # Multiply by 100 for a percentage

# Creating the interface
analysis_frame = ttk.Frame(tab5)
analysis_frame.pack(fill='both', expand=1)

# Left frame (Analysis)
left_frame_analysis = ttk.Frame(analysis_frame)
left_frame_analysis.pack(side='left', fill='both', expand=True)

# Right frame (Graph)
right_frame_analysis = ttk.Frame(analysis_frame)
right_frame_analysis.pack(side='right', fill='both', expand=True)


# Get data from CSV file to retrieve the candlestick chart
def get_data_from_csv(symbol, interval):
    file_name = f'{symbol}_{interval}_historical_data.csv'
    
    # Check if the file exists and is not empty
    if not os.path.exists(file_name) or os.path.getsize(file_name) == 0:
        print(f"The file {file_name} is empty or does not exist.")
        return None

    df = pd.read_csv(file_name)
    df['timestamp'] = pd.to_datetime(df['timestamp'])  # Convert the timestamp column to datetime
    df.set_index('timestamp', inplace=True)  # Set the timestamp column as index
    return df

# Use a Seaborn style
sns.set_theme()

# Enlarge the figure
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), gridspec_kw={'height_ratios': [2, 1]})

# Add the real graph
canvas = FigureCanvasTkAgg(fig, master=right_frame_analysis)
canvas.get_tk_widget().pack(side='top', fill='both', expand=1)

# Global variable to track the number of candles already plotted
num_candles_plotted = 0

def plot_portfolio_graph(symbol, interval):
    global ax1, ax2, num_candles_plotted

    # Get data from CSV
    df = get_data_from_csv(symbol, interval)

    # If df is None (due to a file reading error or other), exit the function
    if df is None:
        return

    # Update the portfolio graph
    ax1.clear()
    portfolio_values = analyses_module_backtest.get_analysis_data()['portfolio_values']
    sns.lineplot(data=portfolio_values, ax=ax1, linewidth=2, label="Portfolio")

    # Plot candles progressively
    df_to_plot = df.iloc[:num_candles_plotted+1]  # Take all candles up to the current candle
    ax2.clear()
    mpf.plot(df_to_plot, type='candle', ax=ax2, volume=False, style='yahoo', warn_too_much_data=10000)

    # Update the number of candles plotted
    if num_candles_plotted < len(df) - 1:
        num_candles_plotted += 1

    # Configure the title and labels with larger font size for ax1
    ax1.set_title("Portfolio Evolution", fontsize=16)
    ax1.set_xlabel("Time", fontsize=14)
    ax1.set_ylabel("Value", fontsize=14)
    ax1.tick_params(labelsize=12)

    # Update the canvas
    canvas.draw()

# Label style (adjust according to your preferences)
LABEL_FONT = ("Arial", 10)
HEADER_FONT = ("Arial", 12, "bold")

def create_label_group(frame, title_text, *labels):
    title = ttk.Label(frame, text=title_text, font=HEADER_FONT, foreground="blue")  # You can change the color
    title.pack(pady=10)
    for label in labels:
        label.pack(anchor='w', padx=20)
    ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)

# Frame for Capital Information
capital_frame = ttk.Frame(left_frame_analysis)
capital_frame.pack(pady=10, padx=10, fill='x')
initial_capital_label = ttk.Label(capital_frame, text="Initial Capital:")
final_capital_label = ttk.Label(capital_frame, text="Final Capital:")
portfolio_returns_label = ttk.Label(capital_frame, text="Portfolio Returns:")
create_label_group(capital_frame, "Capital Information:", initial_capital_label, final_capital_label, portfolio_returns_label)

# Frame for Transaction Details
transactions_frame = ttk.Frame(left_frame_analysis)
transactions_frame.pack(pady=10, padx=10, fill='x')
total_trades_label = ttk.Label(transactions_frame, text="Total Trades:")
winning_trades_label = ttk.Label(transactions_frame, text="Winning Trades:")
losing_trades_label = ttk.Label(transactions_frame, text="Losing Trades:")
sell_short_trades_label = ttk.Label(transactions_frame, text="Short Sell Trades:")
buy_long_trades_label = ttk.Label(transactions_frame, text="Long Buy Trades:")
create_label_group(transactions_frame, "Transaction Details:", total_trades_label, winning_trades_label, losing_trades_label, sell_short_trades_label, buy_long_trades_label)

# Frame for PnL Information
pnl_frame = ttk.Frame(left_frame_analysis)
pnl_frame.pack(pady=10, padx=10, fill='x')
total_pnl_label = ttk.Label(pnl_frame, text="Total PnL:")
total_win_pnl_label = ttk.Label(pnl_frame, text="Total Win PnL:")
total_loss_pnl_label = ttk.Label(pnl_frame, text="Total Loss PnL:")
total_sell_short_pnl_label = ttk.Label(pnl_frame, text="Total Short Sell PnL:")
total_buy_long_pnl_label = ttk.Label(pnl_frame, text="Total Long Buy PnL:")
create_label_group(pnl_frame, "PnL Information:", total_pnl_label, total_win_pnl_label, total_loss_pnl_label, total_sell_short_pnl_label, total_buy_long_pnl_label)

# Frame for Performance Details
performance_frame = ttk.Frame(left_frame_analysis)
performance_frame.pack(pady=10, padx=10, fill='x')
win_rate_label = ttk.Label(performance_frame, text="Win Rate:")
avg_profit_label = ttk.Label(performance_frame, text="Average Profit:")
max_profit_label = ttk.Label(performance_frame, text="Max Profit:")
max_drawdown_label = ttk.Label(performance_frame, text="Max Drawdown:")
create_label_group(performance_frame, "Performance Details:", win_rate_label, avg_profit_label, max_profit_label, max_drawdown_label)

#----------------------------------------------------------------------------------------------------------------------------

# Tab for Modifying Variables
param_frame = ttk.Frame(tab4)
param_frame.pack(fill='both', expand=1)

# Left Frame (List of Categories)
left_frame_param = ttk.Frame(param_frame)
left_frame_param.pack(side='left', fill='both', expand=True)

categories_label = ttk.Label(left_frame_param, text="Categories")
categories_label.pack()
categories_listbox = tk.Listbox(left_frame_param)
categories_listbox.pack(fill='both', expand=True)

categories = ["Binance API Configuration", "Trading Preferences"]
for category in categories:
    categories_listbox.insert(tk.END, category)

# Right Frame (Variable Details)
right_frame_param = ttk.Frame(param_frame)
right_frame_param.pack(side='right', fill='both', expand=True)

variables_label = ttk.Label(right_frame_param, text="Details")
variables_label.pack()

variables_frame = ttk.Frame(right_frame_param)
variables_frame.pack()

def on_category_select(event):
    selected_category = categories_listbox.get(categories_listbox.curselection())
    for widget in variables_frame.winfo_children():
        widget.destroy()

    if selected_category == "Binance API Configuration":
        api_key_label = ttk.Label(variables_frame, text='API Key:')
        api_key_label.pack()
        api_key_var = tk.StringVar()
        api_key_var.set(global_vars.API_KEY)
        api_key_entry = ttk.Entry(variables_frame, textvariable=api_key_var, show="*")
        api_key_entry.pack()
        api_key_var.trace('w', lambda *args: setattr(global_vars, 'API_KEY', api_key_var.get()))

        api_secret_label = ttk.Label(variables_frame, text='API Secret:')
        api_secret_label.pack()
        api_secret_var = tk.StringVar()
        api_secret_var.set(global_vars.API_SECRET)
        api_secret_entry = ttk.Entry(variables_frame, textvariable=api_secret_var, show="*")
        api_secret_entry.pack()
        api_secret_var.trace('w', lambda *args: setattr(global_vars, 'API_SECRET', api_secret_var.get()))

        backtest_url_label = ttk.Label(variables_frame, text='Backtest URL:')
        backtest_url_label.pack()
        backtest_url_var = tk.StringVar()
        backtest_url_var.set(data_import.BASE_URL)  # Assuming base_url is defined in data_import_module_backtest
        backtest_url_entry = ttk.Entry(variables_frame, textvariable=backtest_url_var)
        backtest_url_entry.pack()
        backtest_url_var.trace('w', lambda *args: setattr(data_import, 'BACKTEST_URL', backtest_url_var.get()))

    elif selected_category == "Trading Preferences":
        leverage_label = ttk.Label(variables_frame, text='Leverage:')
        leverage_label.pack()
        leverage_var = tk.StringVar()
        leverage_var.set(str(global_vars.LEVERAGE))
        leverage_combobox = ttk.Combobox(variables_frame, textvariable=leverage_var, values=[str(i) for i in range(1, 21)])
        leverage_combobox.pack()
        leverage_combobox.bind('<<ComboboxSelected>>', lambda event: setattr(global_vars, 'LEVERAGE', int(leverage_var.get())))

        position_amount_label = ttk.Label(variables_frame, text='Position Amount:')
        position_amount_label.pack()
        position_amount_var = tk.StringVar()
        position_amount_var.set(str(global_vars.POSITION_AMOUNT))
        position_amount_entry = ttk.Entry(variables_frame, textvariable=position_amount_var)
        position_amount_entry.pack()
        position_amount_var.trace('w', lambda *args: setattr(global_vars, 'POSITION_AMOUNT', float(position_amount_var.get())))

        position_take_profit_label = ttk.Label(variables_frame, text='Take Profit:')
        position_take_profit_label.pack()
        position_take_profit_var = tk.StringVar()
        position_take_profit_var.set(str(global_vars.POSITION_TAKE_PROFIT))
        position_take_profit_entry = ttk.Entry(variables_frame, textvariable=position_take_profit_var)
        position_take_profit_entry.pack()
        position_take_profit_var.trace('w', lambda *args: setattr(global_vars, 'POSITION_TAKE_PROFIT', float(position_take_profit_var.get())))

        position_stop_loss_label = ttk.Label(variables_frame, text='Stop Loss:')
        position_stop_loss_label.pack()
        position_stop_loss_var = tk.StringVar()
        position_stop_loss_var.set(str(global_vars.POSITION_STOP_LOSS))
        position_stop_loss_entry = ttk.Entry(variables_frame, textvariable=position_stop_loss_var)
        position_stop_loss_entry.pack()
        position_stop_loss_var.trace('w', lambda *args: setattr(global_vars, 'POSITION_STOP_LOSS', float(position_stop_loss_var.get())))

categories_listbox.bind('<<ListboxSelect>>', on_category_select)

#----------------------------------------------------------------------------------------------------------------------------

update_all_values()
update_analysis_labels()

# Lancer le GUI
root.mainloop()