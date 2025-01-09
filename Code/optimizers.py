from bayes_opt import BayesianOptimization
from strategies import Momentum
from testing_tools import simulate_trades, calculate_pnl

class BasicOptimizer():
    def __init__(self, df, symbol, start_date, end_date, time_interval):
        """
        Initializes the BasicOptimizer with historical data and trading parameters.

        Args:
            df (pd.DataFrame): The data frame containing historical price data.
            symbol (str): The trading symbol (e.g., 'BTC/USD').
            start_date (str): The start date for the optimization period.
            end_date (str): The end date for the optimization period.
            time_interval (str): The time interval for the data (e.g., '15min').
        """
        self.symbol = symbol
        self.df = df
        self.start_date = start_date
        self.end_date = end_date
        self.time_interval = time_interval

        self.optimized_position_size = 0
        self.optimized_rsi_high = 0
        self.optimized_rsi_low = 0
        self.optimized_stop_loss = 0
        self.optimized_take_profit = 0

        self.optimized_rsi_weight = 0
        self.optimized_macd_weight = 0
        self.optimized_bb_weight = 0


    def objective(self, position_size, rsi_high, rsi_low, take_profit, stop_loss, rsi_weight=1, macd_weight=1, bb_weight=1):
        """
        The objective function for Bayesian Optimization, which evaluates the trading strategy.

        Args:
            position_size (int): The size of the trading position.
            rsi_high (int): The high RSI threshold.
            rsi_low (int): The low RSI threshold.
            take_profit (float): The take profit threshold.
            stop_loss (float): The stop loss threshold.
            rsi_weight (float, optional): The weight for the RSI indicator. Default is 1.
            macd_weight (float, optional): The weight for the MACD indicator. Default is 1.
            bb_weight (float, optional): The weight for the Bollinger Bands indicator. Default is 1.

        Returns:
            float: The return on investment (ROI) from the simulated trades.
        """
        rsi_high = int(rsi_high)
        rsi_low = int(rsi_low)
        position_size = int(position_size)
        take_profit = float(take_profit)
        stop_loss = float(stop_loss)
        rsi_weight, macd_weight, bb_weight = rsi_weight, macd_weight, bb_weight
        
        if rsi_high <= rsi_low:
            return -9999

        strategy = Momentum(self.df, rsi_high=rsi_high, rsi_low=rsi_low, rsi_weight=1, macd_weight=1, bb_weight=1)
        self.df = strategy.evaluate_indicators()
        self.df = simulate_trades(self.df)    # implement strategy, determine BUY/SELL signal    
        
        profit, roi = calculate_pnl(self.df, position_size, take_profit, stop_loss)
        
        return roi  # Directly maximize profit
    
    def optimize(self):
        """
        Optimizes the trading strategy parameters using Bayesian Optimization.

        Returns:
            dict: A dictionary of the optimized parameters.
        """
        pbounds = {                 # should change dynamically
            'rsi_high': (50, 100),
            'rsi_low': (0, 50),
            # 'position_size': (500, 2000),
            'position_size': (500, 10000),
            # 'take_profit': (1, 10),
            # 'stop_loss': (1, 5),
            'take_profit': (1, 100),
            'stop_loss': (1, 10),
            # 'take_profit': (1, 20),
            # 'stop_loss': (1, 10),
            # 'take_profit': (1, 100),
            # 'stop_loss': (1, 100),
            'rsi_weight': (0, 3),
            'macd_weight': (0, 3),
            'bb_weight': (0, 3),
        }
        optimizer = BayesianOptimization(f=self.objective, pbounds=pbounds, verbose=0, random_state=1)
        optimizer.maximize(init_points=10, n_iter=100)

        self.optimized_position_size = optimizer.max['params'].get('position_size')
        self.optimized_rsi_high = optimizer.max['params'].get('rsi_high')
        self.optimized_rsi_low = optimizer.max['params'].get('rsi_low')
        self.optimized_stop_loss = optimizer.max['params'].get('stop_loss')
        self.optimized_take_profit = optimizer.max['params'].get('take_profit')

        self.optimized_rsi_weight = optimizer.max['params'].get('rsi_weight')
        self.optimized_macd_weight = optimizer.max['params'].get('macd_weight')
        self.optimized_bb_weight = optimizer.max['params'].get('bb_weight')
        
        return optimizer.max['params']

    def get_optimized_parameters(self):
        """
        Retrieves the optimized parameters.

        Returns:
            tuple: A tuple containing the optimized parameters.
        """
        return (self.optimized_position_size, self.optimized_rsi_high, self.optimized_rsi_low, 
                self.optimized_take_profit, self.optimized_stop_loss, self.optimized_rsi_weight, 
                self.optimized_macd_weight, self.optimized_bb_weight)


# ———————————————————— Test ——————————————————————

if __name__ == "__main__":
    None

'''
Rather than test everything.

Use machine learning by reflecting on the trades.

Learn which signals are positive (profitable) and which signals are negative (unprofitable). 

'''