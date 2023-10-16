import execution_module_backtest
from execution_module_backtest import closed_trades, PORTFOLIO_VALUES

def get_analysis_data():
    # Retrieving already calculated metrics
    total_pnl = execution_module_backtest.PNL_TOTAL
    final_capital = execution_module_backtest.ACCOUNT_BALANCE
    initial_capital = execution_module_backtest.INITIAL_CAPITAL

    # Calculation of additional metrics based on backtest data
    winning_trades = 0
    losing_trades = 0
    max_profit = 0
    max_loss = 0
    total_win_pnl = 0
    total_loss_pnl = 0
    sell_short_trades = 0
    buy_long_trades = 0
    total_sell_short_pnl = 0
    total_buy_long_pnl = 0

    # Assuming trades are stored in a list
    for trade in closed_trades:
        pnl = trade['pnl']
        if pnl > 0:
            winning_trades += 1
            total_win_pnl += pnl
            if pnl > max_profit:
                max_profit = pnl
        elif pnl < 0:
            losing_trades += 1
            total_loss_pnl += pnl
            if pnl < max_loss:
                max_loss = pnl
        
        if trade['trading_signal'] == 'SELL_SHORT':
            sell_short_trades += 1
            total_sell_short_pnl += trade['pnl']
        elif trade['trading_signal'] == 'BUY_LONG':
            buy_long_trades += 1
            total_buy_long_pnl += trade['pnl']

    win_rate = winning_trades / (winning_trades + losing_trades) if (winning_trades + losing_trades) != 0 else 0

    analysis_data = {
        'total_pnl': total_pnl,
        'final_capital': final_capital,
        'initial_capital': initial_capital,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'max_profit': max_profit,
        'max_loss': max_loss,
        'total_win_pnl': total_win_pnl,
        'total_loss_pnl': total_loss_pnl,
        'win_rate': win_rate,
        'sell_short_trades': sell_short_trades,
        'buy_long_trades': buy_long_trades,
        'total_sell_short_pnl': total_sell_short_pnl,
        'total_buy_long_pnl': total_buy_long_pnl,
        'portfolio_values': PORTFOLIO_VALUES,
    }

    # Calculation of return
    portfolio_return = (final_capital - initial_capital) / initial_capital * 100

    # Calculation of average profit
    total_trades = winning_trades + losing_trades
    avg_profit = total_pnl / total_trades if total_trades != 0 else 0

    # Calculation of Max Drawdown
    max_value = float("-inf")
    max_drawdown = 0
    for value in PORTFOLIO_VALUES:
        if value > max_value:
            max_value = value
        drawdown = (max_value - value) / max_value
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    analysis_data.update({
        'portfolio_return': portfolio_return,
        'avg_profit': avg_profit,
        'max_drawdown': max_drawdown
    })

    return analysis_data