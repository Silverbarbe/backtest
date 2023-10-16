# Global variables for the trading bot
API_KEY = 'your-api-key'  # Your API key to access Binance
API_SECRET = 'your-api-secret'  # Your API secret to access Binance
BINANCE = None  # This will store the connection to Binance
TRADING_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'DOTUSDT', 'LTCUSDT', 'LINKUSDT', 'UNIUSDT', 'SOLUSDT', 'THETAUSDT', 'XLMUSDT', 'VETUSDT', 'TRXUSDT', 'EOSUSDT']  # Trading pairs to follow
TRADE_INTERVALS = ['1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w']  # Time intervals
INITIAL_CAPITAL = 10000  # Initial capital amount

# Variables for position management
LEVERAGE = 20  # Leverage for margin trading
ORDER_TYPE = 'MARKET'  # Order type (MARKET, LIMIT, etc.)
ORDER_SIDE = 'BUY'  # Order side (BUY, SELL)
ORDER_TIMEOUT = 10  # Maximum duration to wait for an order execution
POSITION_AMOUNT = 100  # Position size in USDT
POSITION_TAKE_PROFIT = 0.01  # Target profit percentage for the position
POSITION_STOP_LOSS = 0.02  # Target loss percentage for the position
PRICE_TICK_SIZE = {}  # Dictionary to store the minimum price tick size for each trading pair
QUANTITY_TICK_SIZE = {}  # Dictionary to store the minimum quantity tick size for each trading pair

# Variables for technical analysis
INDICATOR_PERIOD = 14  # Period for technical indicators (RSI, SMA, etc.)
RSI_OVERBOUGHT_THRESHOLD = 70  # Overbought threshold for RSI
RSI_OVERSOLD_THRESHOLD = 30  # Oversold threshold for RSI

# Variables for technical indicators
MACD_FAST_PERIOD = 12  # Fast period for MACD
MACD_SLOW_PERIOD = 26  # Slow period for MACD
MACD_SIGNAL_PERIOD = 9  # Signal period for MACD
SMA_PERIODS = [7, 20, 50, 100, 200]  # Periods for Simple Moving Average (SMA)
EMA_PERIODS = [7, 20, 50, 100, 200]  # Periods for Exponential Moving Average (EMA)
BB_PERIOD = 20  # Period for Bollinger Bands
BB_STD = 2  # Standard deviation for Bollinger Bands
