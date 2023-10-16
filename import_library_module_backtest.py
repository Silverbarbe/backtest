import pandas as pd  # For data manipulation and analysis
import numpy as np  # For mathematical operations
import requests  # For HTTP requests
import logging  # For logging
import pytz  # For timezone management
import cvxpy as cp  # For linear and convex programming
from typing import List  # For type annotations
from datetime import datetime, timedelta  # For date and time manipulation
from textblob import TextBlob  # For sentiment analysis
from ta.trend import MACD, SMAIndicator, EMAIndicator  # For trend indicators
from ta.volatility import BollingerBands, AverageTrueRange  # For volatility indicators
from ta.momentum import RSIIndicator  # For momentum indicator (RSI)
from concurrent.futures import ThreadPoolExecutor  # For concurrent task execution
from pypfopt import EfficientFrontier, objective_functions  # For portfolio optimization
from pypfopt import risk_models  # For risk models
from pypfopt import expected_returns  # For expected returns
import ccxt  # For interaction with cryptocurrency exchange platforms
import backtrader  # For backtesting and algorithmic trading
import talib  # For technical indicators (TA-Lib)
import tensorflow as tf  # For machine learning with TensorFlow
import torch  # For machine learning with PyTorch
import matplotlib.pyplot as plt  # For data visualization with Matplotlib
import plotly.graph_objects as go  # For data visualization with Plotly
import requests  # For HTTP requests
from requests.exceptions import RequestException  # For handling request exceptions
import time  # For time-related tasks
