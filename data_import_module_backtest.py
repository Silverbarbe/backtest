import import_library_module_backtest as lib
import global_variable_module_backtest as gv
from datetime import datetime
from dateutil.relativedelta import relativedelta

BASE_URL = 'https://api.binance.com/api/v3/klines'  # Base URL for Binance API endpoint

asset_prices = []  # List to store asset prices
df_global = None  # Global dataframe to store all data

def get_start_time(interval, num_candles):
    # Mapping of interval string to time unit
    interval_map = {
        '1m': 'minutes',
        '5m': 'minutes',
        '15m': 'minutes',
        '30m': 'minutes',
        '1h': 'hours',
        '4h': 'hours',
        '1d': 'days',
        '1w': 'weeks'
    }

    unit = interval_map.get(interval)  # Get time unit from interval_map based on interval string
    if unit is None:
        print(f"Invalid interval: {interval}")
        return None

    quantity = int(interval[:-1])  # Extract quantity from interval string
    total = quantity * num_candles  # Calculate total time span

    now = datetime.now()  # Get current datetime
    args = {unit: total}  # Create argument dictionary for relativedelta function

    start_time = now - relativedelta(**args)  # Calculate start time by subtracting total time span from current datetime
    return start_time  # Return the calculated start time

def import_data_from_binance(symbol, interval, num_candles):
    limit = 1000  # Limit for number of candles to be retrieved per request
    all_data = []  # List to store all retrieved data

    start_time = get_start_time(interval, num_candles)  # Get start time using get_start_time function
    if start_time is None:
        print("Invalid interval or num_candles")
        return None, None, None

    start_time = int(start_time.timestamp() * 1000)  # Convert start time to milliseconds
    end_time = int(datetime.now().timestamp() * 1000)  # Convert current time to milliseconds

    while True:
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time,
            'limit': limit
        }  # Parameters for Binance API request

        try:
            response = lib.requests.get(BASE_URL, params=params)  # Send GET request to Binance API using BASE_URL and params
            response.raise_for_status()  # Check for HTTP errors
        except lib.RequestException as e:  # Handle RequestException
            lib.logging.error(f"Failed to retrieve data from Binance API for {symbol} due to {e}")
            lib.logging.error(f"Params: {params}")
            return None  # Return None if exception occurs

        data = response.json()  # Parse JSON response to a Python dictionary

        if len(data) < 1:  # Check if data is empty
            lib.logging.warning(f"No data returned from Binance API for {symbol}")
            lib.logging.warning(f"Params: {params}")
            return None  # Return None if data is empty

        all_data += data  # Append retrieved data to all_data list

        if len(data) < limit:  # Check if retrieved data is less than the limit, indicating end of data
            break  # Exit loop if end of data reached

        start_time = data[-1][0] + 1  # Update start_time for next request
        lib.time.sleep(0.05)  # Pause for a short duration before next request to avoid overwhelming the API

    # Create a DataFrame from all_data with specified column names
    df = lib.pd.DataFrame(
        all_data,
        columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                 'taker_buy_quote_asset_volume', 'ignore'])
    # Convert timestamp to datetime, and price and volume columns to float
    df['timestamp'] = lib.pd.to_datetime(df['timestamp'], unit='ms')
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)

    # Save the data to a CSV file
    df.to_csv(f'{symbol}_{interval}_historical_data.csv', index=False)

    global asset_prices  # Declare asset_prices as global
    asset_prices.extend(df['close'].tolist())  # Extend asset_prices list with close prices from df
    global df_global  # Declare df_global as global
    df_global = df  # Assign df to df_global

    # Log info message indicating successful data import and save
    lib.logging.info(f"Data successfully imported and saved for {symbol} from {start_time} to {end_time}")
    return df, start_time, end_time  # Return DataFrame, start_time, and end_time
