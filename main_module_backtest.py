import threading
import queue
import logging
import execution_module_backtest
from import_library_module_backtest import *
from global_variable_module_backtest import TRADING_SYMBOLS, TRADE_INTERVALS
from data_import_module_backtest import import_data_from_binance
from strategy_module_backtest import get_trading_signal

from tkinter import Tk, ttk, Text, Scrollbar

logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Backtest:
    def __init__(self, root, backtest_output, positions_treeview, num_candles, intervals=None, symbols=None):
        self.num_candles = int(num_candles)
        self.intervals = intervals if intervals else ['1m']
        self.trading_symbols = symbols if symbols else TRADING_SYMBOLS
        self.running = False
        self.queue = queue.Queue()
        self.root = root
        self.thread = threading.Thread(target=self.main_loop)
        self.backtest_output = backtest_output
        self.positions_treeview = positions_treeview
        self.open_positions = []
        self.open_position_ids = {}
        self.closed_positions_ids = set()

    def start(self):
        self.running = True
        self.thread.start()
        # self.root.after(30000, self.update_ui)  # Update every 30 seconds

    def update_ui(self):
        # 1. Remove all existing entries
        self.positions_treeview.delete(*self.positions_treeview.get_children())

        # 2. Insert closed positions from the queue
        while not self.queue.empty():
            position = self.queue.get()
            position_values = " ".join(str(value) for value in position.values())
            self.positions_treeview.insert('', 'end', values=position)
            self.backtest_output.insert('end', f"Closed position: Symbol: {position_values['symbol']}, Opening Time: {position_values['opening_time']}\n")
            self.backtest_output.see('end')

        # 3. Insert open positions from self.open_positions
        for open_position in self.open_positions:

            # Directly insert the dictionary as values
            self.positions_treeview.insert('', 'end', values=open_position)

        if self.running:
            self.root.after(30000, self.update_ui)

    def main_loop(self):
        for symbol in self.trading_symbols:
            for interval in self.intervals:
                if not self.running:
                    break

                df, _, _ = import_data_from_binance(symbol, interval, self.num_candles)
                if df is not None:
                    self.backtest_output.insert('end', f"{symbol} data imported successfully for interval {interval}.\n")
                    self.backtest_output.see('end')  # Scroll to the end of the text area
                    for index, row in df.iterrows():
                        if not self.running:
                            break
                        trading_signal = get_trading_signal(symbol, interval, df, index, self.num_candles)
                        self.backtest_output.insert('end', f"Trading signal for {symbol} ({interval}): {trading_signal}\n")
                        self.backtest_output.see('end')  # Scroll to the end of the text area

                        open_positions, closed_positions = execution_module_backtest.execute_trade(df, symbol, interval, self.num_candles, index)

                        self.open_positions = open_positions

                        for closed_position in closed_positions:
                            trade_id = closed_position['symbol'] + closed_position['interval']
                            if trade_id not in self.closed_positions_ids:
                                self.closed_positions_ids.add(trade_id)
                                if trade_id in self.open_position_ids:
                                    del self.open_position_ids[trade_id]
                                self.queue.put(closed_position)
                            else:
                                logging.info(f"Duplicate closed position detected: {trade_id}")

                else:
                    self.backtest_output.insert('end', f"Failed to import {symbol} data for interval {interval}.\n")
                    self.backtest_output.see('end')  # Scroll to the end of the text area

    def stop(self):
        self.running = False

if __name__ == "__main__":
    num_candles_input = "1000"
    root = Tk()
    backtest_output = Text(root, height=20, width=100)
    backtest_output.pack()

    backtest = Backtest(root, backtest_output=backtest_output, num_candles=num_candles_input)
    backtest.start()