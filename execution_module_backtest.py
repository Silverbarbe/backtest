#Importations modules
from global_variable_module_backtest import *
from strategy_module_backtest import get_trading_signal
from data_import_module_backtest import import_data_from_binance

# Inner variables within the execution module
AVAILABLE_CAPITAL = INITIAL_CAPITAL
ACCOUNT_BALANCE = INITIAL_CAPITAL
PNL_TOTAL = 0
PNL_LATENT_TOTAL = 0
PORTFOLIO_VALUES = [ACCOUNT_BALANCE]  # start with inital capital 
TAKER_FEE = 0.0004
SLIPPAGE = 0.0002
TOTAL_COST = TAKER_FEE + SLIPPAGE

# Calculate the postion_size for each trade
def calculate_position_size():
    return POSITION_AMOUNT * LEVERAGE

# Calculate the TP and SL for each position, the level of TP/SL is in the global variables module
def calculate_TP_SL(price, trading_signal):
    TP = price * (1 + POSITION_TAKE_PROFIT) if trading_signal == 'BUY_LONG' else price * (1 - POSITION_TAKE_PROFIT)
    SL = price * (1 - POSITION_STOP_LOSS) if trading_signal == 'BUY_LONG' else price * (1 + POSITION_STOP_LOSS)
    return TP, SL

active_trades = []
closed_trades = []

#Calculate PNL considering the inner variables
def calculate_pnl(trade, closing_price):
    entry_price = trade['entry_price']
    position_size = trade['size']
    trading_signal = trade['trading_signal']
    
    cost_multiplier = 1 - TOTAL_COST if trading_signal == 'BUY_LONG' else 1 + TOTAL_COST

    if trading_signal == 'BUY_LONG':
        pnl = (closing_price / (entry_price * cost_multiplier) - 1) * position_size
    elif trading_signal == 'SELL_SHORT':
        pnl = (1 - closing_price / (entry_price * cost_multiplier)) * position_size
    else:
        pnl = 0  # IF no new position then PNL = 0

    return pnl

# Define latent PNL 
def calculate_latent_pnl(position, current_price):
    entry_price = position['entry_price']
    position_size = position['size']
    trading_signal = position['trading_signal']
    
    if trading_signal == 'BUY_LONG':
        latent_pnl = (current_price / entry_price - 1) * position_size
    elif trading_signal == 'SELL_SHORT':
        latent_pnl = (1 - current_price / entry_price) * position_size
    else:
        latent_pnl = 0  

    return latent_pnl

def execute_trade(df, symbol, interval, num_candles, index):
    global ACCOUNT_BALANCE, PNL_TOTAL, PNL_LATENT_TOTAL, AVAILABLE_CAPITAL, closed_trades

    df, start_time, end_time = import_data_from_binance(symbol, interval, num_candles)
    trading_signal = get_trading_signal(symbol, interval, df, index, num_candles)
    price = df.iloc[index]['close']
    high_price = df.iloc[index]['high']
    low_price = df.iloc[index]['low']
    real_position_size = POSITION_AMOUNT  # Position_size
    position_size_with_leverage = real_position_size * LEVERAGE  # Position_size * Leverage
    TP, SL = calculate_TP_SL(price, trading_signal)
    opening_time = df.iloc[index]['timestamp']

    trades_to_close = []

    #Check the the trades closed and calcul the PNL
    for trade in active_trades:
        if trade['symbol'] == symbol:
            # Verification of TP and SL
            if trade['trading_signal'] == 'BUY_LONG':
                if low_price <= trade['sl'] or high_price >= trade['tp'] or trading_signal == 'SELL_SHORT':
                    trade['closing_price'] = trade['sl'] if low_price <= trade['sl'] else (trade['tp'] if high_price >= trade['tp'] else price)
                    trades_to_close.append(trade)
            elif trade['trading_signal'] == 'SELL_SHORT':
                if high_price >= trade['sl'] or low_price <= trade['tp'] or trading_signal == 'BUY_LONG':
                    trade['closing_price'] = trade['sl'] if high_price >= trade['sl'] else (trade['tp'] if low_price <= trade['tp'] else price)
                    trades_to_close.append(trade)

            # Vérification condition closed after 10 openend candlestick
            if trade['opening_time'] in df.index:
                time_since_trade_open = index - df.index.get_loc(trade['opening_time'])
                print(f"Trade opened at {trade['opening_time']} and current time is {df.iloc[index]['timestamp']}. Time since trade open: {time_since_trade_open} candles. Latent PNL: {trade['latent_pnl']}")  # Log pour le diagnostic
                if time_since_trade_open > 10:
                    print(f"Trade has been open for more than 10 candles. Checking PNL...")  # Log for diagnostic
                    if trade['latent_pnl'] > 0:
                        trade['closing_reason'] = "10 candles in profit"
                        trade['closing_price'] = price
                        trades_to_close.append(trade)
                    elif trade['latent_pnl'] < 0:
                        trade['closing_reason'] = "10 candles in loss"
                        trade['closing_price'] = price
                        trades_to_close.append(trade)
            
            # Calcul Latent PNL 
            trade['latent_pnl'] = calculate_latent_pnl(trade, price)

    # Check the closed trades
    for trade in trades_to_close:
        reason = trade.get('closing_reason', "")
        if not reason:
            if low_price <= trade['sl']:
                reason = "SL hit"
            elif high_price >= trade['tp']:
                reason = "TP hit"
            elif trading_signal in ['SELL_SHORT', 'BUY_LONG']:
                reason = "Change in trading signal"

        print(f"Closing trade {trade['trading_signal']} pour {symbol} au prix {trade['closing_price']} due to {reason}")
        trade_pnl = calculate_pnl(trade, trade['closing_price'])
        PNL_TOTAL += trade_pnl
        trade['pnl'] = trade_pnl
        closed_trades.append(trade)
        active_trades.remove(trade)
        trade['latent_pnl'] = 0

    # Calcul the PNL closed
    PNL_LATENT_TOTAL = sum(calculate_latent_pnl(trade, price) for trade in active_trades)
    # MAJ of open Positions
    real_positions_amount = sum(trade['real_size'] for trade in active_trades)
    AVAILABLE_CAPITAL = INITIAL_CAPITAL - real_positions_amount + PNL_TOTAL + PNL_LATENT_TOTAL
    # MAJ account balance
    ACCOUNT_BALANCE = INITIAL_CAPITAL + PNL_TOTAL + PNL_LATENT_TOTAL

    # Add the portfolio value to the balance account
    PORTFOLIO_VALUES.append(ACCOUNT_BALANCE)

    # Trade Execution
    if trading_signal in ['BUY_LONG', 'SELL_SHORT']:
        adjusted_price = price * (1 + TOTAL_COST) if trading_signal == 'BUY_LONG' else price * (1 - TOTAL_COST)
        print(f"Exécution de {trading_signal} pour {symbol} au prix ajusté {adjusted_price} (Prix du marché : {price}) avec une taille de {position_size_with_leverage} (TP: {TP}, SL: {SL})")
        trade = {
            'symbol': symbol,
            'interval': interval,
            'trading_signal': trading_signal,
            'entry_price': adjusted_price,
            'tp': TP,
            'sl': SL,
            'real_size': real_position_size, 
            'size': position_size_with_leverage,  
            'opening_time': opening_time,
            'pnl': None,
            'closing_price': None,
            'latent_pnl': 0
        }
        active_trades.append(trade)
    else:
        print(f"Holding position for {symbol}")

    return active_trades, closed_trades