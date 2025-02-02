import numpy as np
from joblib import Parallel, delayed
from bayes_opt import BayesianOptimization
import pandas as pd

class Momentum:
    def __init__(self, df, rsi_high=70, rsi_low=30, rsi_weight=1, macd_weight=1, bb_weight=1):
        self.df = df
        self.rsi_high = rsi_high
        self.rsi_low = rsi_low
        self.rsi_weight = rsi_weight
        self.macd_weight = macd_weight
        self.bb_weight = bb_weight

    def calc_RSI(self, window=14):
        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        self.df['RSI'] = 100 - (100 / (1 + rs))

        # Signal generation based on RSI thresholds
        self.df['RSI_signal'] = 0
        self.df.loc[self.df['RSI'] > self.rsi_high, 'RSI_signal'] = -1  # Overbought, Sell signal
        self.df.loc[self.df['RSI'] < self.rsi_low, 'RSI_signal'] = 1   # Oversold, Buy signal

    def calc_MACD(self, short_window=12, long_window=26, signal_window=9):
        short_ema = self.df['close'].ewm(span=short_window, adjust=False).mean()
        long_ema = self.df['close'].ewm(span=long_window, adjust=False).mean()
        self.df['MACD'] = short_ema - long_ema
        self.df['Signal_line'] = self.df['MACD'].ewm(span=signal_window, adjust=False).mean()

        # Generate MACD signal
        self.df['MACD_signal'] = 0
        self.df.loc[self.df['MACD'] > self.df['Signal_line'], 'MACD_signal'] = 1  # Bullish
        self.df.loc[self.df['MACD'] < self.df['Signal_line'], 'MACD_signal'] = -1  # Bearish

    def calc_BB(self, window=20, num_std=2):
        sma = self.df['close'].rolling(window=window).mean()
        std = self.df['close'].rolling(window=window).std()
        self.df['BB_upper'] = sma + (num_std * std)
        self.df['BB_lower'] = sma - (num_std * std)

        # Bollinger Band signal: Buy if price near lower band, sell near upper band
        self.df['BB_diverging'] = 0
        self.df.loc[self.df['close'] < self.df['BB_lower'], 'BB_diverging'] = 1   # Buy signal
        self.df.loc[self.df['close'] > self.df['BB_upper'], 'BB_diverging'] = -1  # Sell signal

    def evaluate_indicators(self):
        self.calc_RSI()
        self.calc_MACD()
        self.calc_BB()
        return self.df

def simulate_trades(df, rsi_weight=1, macd_weight=1, bb_weight=1):
    df = df.dropna(subset=['RSI_signal', 'MACD_signal', 'BB_diverging'])  # Ensure signals exist
    df['Signal'] = 0  # Initialize Signal

    for i in range(len(df)):
        signal_value = (
            df.at[df.index[i], 'RSI_signal'] * rsi_weight +
            df.at[df.index[i], 'MACD_signal'] * macd_weight +
            df.at[df.index[i], 'BB_diverging'] * bb_weight
        )
        df.at[df.index[i], 'Signal'] = float(signal_value)
    
    return df


def calculate_pnl(data, trade_size, profit_target_pct, stop_loss_pct):
        """
        Calculate the profit and loss (PnL) and respect take-profit and stop-loss.
        """
        position = 0  # 1 for long, -1 for short, 0 for no position
        entry_price = 0
        profits = []
        cumulative_profits = [0]  # To track cumulative profit over time

        for i in range(len(data)):
            close_price = data['close'].iloc[i]

            if position == 0:  # No open position, check for entry signal
                if data['Signal'].iloc[i] > 0:  # Long signal
                    position = 1
                    entry_price = close_price
                elif data['Signal'].iloc[i] < 0:  # Short signal
                    position = -1
                    entry_price = close_price

            elif position == 1:  # Long position
                if close_price >= entry_price * (1 + profit_target_pct / 100):  # Take profit
                    pnl = (close_price - entry_price) * (trade_size / entry_price)
                    profits.append(pnl)
                    cumulative_profits.append(cumulative_profits[-1] + pnl)
                    position = 0  # Close position
                elif close_price <= entry_price * (1 - stop_loss_pct / 100):  # Stop loss
                    pnl = (close_price - entry_price) * (trade_size / entry_price)
                    profits.append(pnl)
                    cumulative_profits.append(cumulative_profits[-1] + pnl)
                    position = 0  # Close position

            elif position == -1:  # Short position
                if close_price <= entry_price * (1 - profit_target_pct / 100):  # Take profit
                    pnl = (entry_price - close_price) * (trade_size / entry_price)
                    profits.append(pnl)
                    cumulative_profits.append(cumulative_profits[-1] + pnl)
                    position = 0  # Close position
                elif close_price >= entry_price * (1 + stop_loss_pct / 100):  # Stop loss
                    pnl = (entry_price - close_price) * (trade_size / entry_price)
                    profits.append(pnl)
                    cumulative_profits.append(cumulative_profits[-1] + pnl)
                    position = 0  # Close position

        # Calculate maximum drawdown
        cumulative_profits = np.array(cumulative_profits)
        peak = np.maximum.accumulate(cumulative_profits)
        epsilon = 1e-10  # To prevent divide-by-zero
        drawdown = (cumulative_profits - peak) / (peak + epsilon)

        max_drawdown = drawdown.min() if len(drawdown) > 0 else 0
        return sum(profits), sum(profits) / trade_size, max_drawdown


class BasicOptimizer:
    def __init__(self, df):
        """
        Initializes the BasicOptimizer with historical data and trading parameters.

        Args:
            df (pd.DataFrame): The data frame containing historical price data.
        """
        self.df = df
        self.optimized_position_size = 0
        self.optimized_rsi_high = 0
        self.optimized_rsi_low = 0
        self.optimized_stop_loss = 0
        self.optimized_take_profit = 0
        self.optimized_rsi_weight = 0
        self.optimized_macd_weight = 0
        self.optimized_bb_weight = 0

    def calculate_penalty(self, rsi_high, rsi_low, take_profit, stop_loss):
        """
        Adds penalties for unrealistic parameter combinations.
        """
        if rsi_high <= rsi_low or stop_loss >= take_profit:
            return -9999  # Strong penalty
        return 0

    def composite_score(self, roi, max_drawdown):
        """
        Combines ROI and drawdown into a composite objective score.
        """
        return 0.7 * roi - 0.3 * max_drawdown

    def simulate_trades_parallel(self, df, num_splits=4):
        """
        Parallelizes the simulation of trades to speed up processing.
        """
        chunks = np.array_split(df, num_splits)
        results = Parallel(n_jobs=-1)(delayed(simulate_trades)(chunk) for chunk in chunks)
        return pd.concat(results)

    def calculate_drawdown(cumulative_profits):
        peak = np.maximum.accumulate(cumulative_profits)
        peak[peak == 0] = np.nan  # Prevent divide by zero errors
        drawdown = (cumulative_profits - peak) / peak
        drawdown = np.nan_to_num(drawdown, nan=0)  # Convert NaNs to 0 to avoid issues in optimization
        return drawdown.min()

    def objective(self, position_size, rsi_high, rsi_low, take_profit, stop_loss, rsi_weight=1, macd_weight=1, bb_weight=1):
        """
        The objective function for Bayesian Optimization, evaluating the trading strategy.
        """
        rsi_high, rsi_low = int(rsi_high), int(rsi_low)
        position_size = int(position_size)
        take_profit, stop_loss = float(take_profit), float(stop_loss)

        # Return large penalty if the RSI thresholds or take-profit/stop-loss are invalid
        if rsi_high <= rsi_low or take_profit <= stop_loss:
            return -9999

        # Evaluate strategy and simulate trades
        strategy = Momentum(self.df, rsi_high=rsi_high, rsi_low=rsi_low, rsi_weight=rsi_weight,
                            macd_weight=macd_weight, bb_weight=bb_weight)
        evaluated_df = strategy.evaluate_indicators()
        evaluated_df = simulate_trades(evaluated_df, rsi_weight, macd_weight, bb_weight)

        # Calculate profit, ROI, and drawdown
        profit, roi, max_drawdown = calculate_pnl(evaluated_df, position_size, take_profit, stop_loss)
        if np.isnan(roi) or np.isnan(max_drawdown):
            return -9999  # Penalize bad outcomes

        return 0.7 * roi - 0.3 * max_drawdown  # Composite score: ROI and drawdown balance

    def optimize(self):
        """
        Optimizes the trading strategy parameters using Bayesian Optimization.
        """
        pbounds = {
            'rsi_high': (50, 100),
            'rsi_low': (0, 50),
            'position_size': (500, 10000),
            'take_profit': (1, 100),
            'stop_loss': (1, 10),
            'rsi_weight': (0, 3),
            'macd_weight': (0, 3),
            'bb_weight': (0, 3),
        }
        optimizer = BayesianOptimization(f=self.objective, pbounds=pbounds, verbose=0, random_state=1)
        optimizer.maximize(init_points=10, n_iter=100)

        best_params = optimizer.max['params']
        self.optimized_position_size = best_params['position_size']
        self.optimized_rsi_high = best_params['rsi_high']
        self.optimized_rsi_low = best_params['rsi_low']
        self.optimized_stop_loss = best_params['stop_loss']
        self.optimized_take_profit = best_params['take_profit']
        self.optimized_rsi_weight = best_params['rsi_weight']
        self.optimized_macd_weight = best_params['macd_weight']
        self.optimized_bb_weight = best_params['bb_weight']

        return best_params
    
    def get_optimized_parameters(self):
        """
        Retrieves the optimized parameters.
        """
        return (self.optimized_position_size, self.optimized_rsi_high, self.optimized_rsi_low, 
                self.optimized_take_profit, self.optimized_stop_loss, self.optimized_rsi_weight, 
                self.optimized_macd_weight, self.optimized_bb_weight)


import numpy as np
from bayes_opt import BayesianOptimization
import pandas as pd

class SignalDependentOptimizer:
    def __init__(self, df):
        """
        Initializes the optimizer with historical data and trading parameters.
        """
        self.df = df
        self.optimized_position_size = 0
        self.optimized_rsi_high = 0
        self.optimized_rsi_low = 0
        self.optimized_rsi_weight = 0
        self.optimized_macd_weight = 0
        self.optimized_bb_weight = 0
        
        self.optimized_take_profit = 0
        self.optimized_stop_loss = 0

    def calculate_pnl(self, data, trade_size):
        """
        Calculate profit based solely on entry/exit signals and trade size.
        """
        position = 0  # 1 for long, -1 for short, 0 for no position
        entry_price = 0
        total_pnl = 0

        for i in range(len(data)):
            close_price = data['close'].iloc[i]

            if position == 0:  # No open position, check for entry
                if data['Signal'].iloc[i] > 0:  # Long signal
                    position = 1
                    entry_price = close_price
                elif data['Signal'].iloc[i] < 0:  # Short signal
                    position = -1
                    entry_price = close_price

            elif position == 1:  # Long position
                if data['Signal'].iloc[i] <= 0:  # Exit long position
                    pnl = (close_price - entry_price) * (trade_size / entry_price)
                    total_pnl += pnl
                    position = 0  # Close position

            elif position == -1:  # Short position
                if data['Signal'].iloc[i] >= 0:  # Exit short position
                    pnl = (entry_price - close_price) * (trade_size / entry_price)
                    total_pnl += pnl
                    position = 0  # Close position

        return total_pnl

    def objective(self, position_size, rsi_high, rsi_low, rsi_weight=1, macd_weight=1, bb_weight=1):
        """
        The objective function for Bayesian Optimization, evaluating the trading strategy.
        """
        rsi_high, rsi_low = int(rsi_high), int(rsi_low)
        position_size = int(position_size)

        # Return a large penalty if the RSI thresholds are invalid
        if rsi_high <= rsi_low:
            return -9999

        # Evaluate strategy and simulate trades
        strategy = Momentum(self.df, rsi_high=rsi_high, rsi_low=rsi_low, rsi_weight=rsi_weight,
                            macd_weight=macd_weight, bb_weight=bb_weight)
        evaluated_df = strategy.evaluate_indicators()
        evaluated_df = simulate_trades(evaluated_df, rsi_weight, macd_weight, bb_weight)

        # Calculate profit based on signals and return it as the optimization target
        total_pnl = self.calculate_pnl(evaluated_df, position_size)

        return total_pnl

    def optimize(self):
        """
        Optimizes the trading strategy parameters using Bayesian Optimization.
        """
        pbounds = {
            'rsi_high': (50, 100),
            'rsi_low': (0, 50),
            'position_size': (500, 10000),
            'rsi_weight': (0, 3),
            'macd_weight': (0, 3),
            'bb_weight': (0, 3),
        }
        optimizer = BayesianOptimization(f=self.objective, pbounds=pbounds, verbose=0, random_state=1)
        optimizer.maximize(init_points=10, n_iter=100)

        best_params = optimizer.max['params']
        self.optimized_position_size = best_params['position_size']
        self.optimized_rsi_high = best_params['rsi_high']
        self.optimized_rsi_low = best_params['rsi_low']
        self.optimized_rsi_weight = best_params['rsi_weight']
        self.optimized_macd_weight = best_params['macd_weight']
        self.optimized_bb_weight = best_params['bb_weight']

        return best_params

    def get_optimized_parameters(self):
        """
        Retrieves the optimized parameters.
        """
        return (self.optimized_position_size, self.optimized_rsi_high, self.optimized_rsi_low, 
                self.optimized_take_profit, self.optimized_stop_loss, self.optimized_rsi_weight, 
                self.optimized_macd_weight, self.optimized_bb_weight)
    

if __name__ == "__main__":
    from paper_trading import datetime, TimeFrame, TimeFrameUnit
    from testing_tools import setup
    from tester import tester
    import time
    
    # Set Environment
    symbol = 'BTC/USD'
    type = 'crypto'
    start_time = datetime(2022,12,1)
    end_time = datetime(2024,12,31)
    time_interval = TimeFrame(4,TimeFrameUnit.Hour)
    df = setup(symbol, type, start_time, end_time, time_interval)

    
    # Setup Optimizer
    setup_start_time = time.perf_counter()              # Start timer
    # optimizer = BasicOptimizer(df)
    optimizer = SignalDependentOptimizer(df)
    setup_end_time = time.perf_counter()                # End timer

    setup_elapsed_time = setup_end_time - setup_start_time
    print(f"Time to setup optimizer: {setup_elapsed_time} seconds")


    # Optimize Parameters
    optimization_start_time = time.perf_counter()       # Start timer
    optimized_parameters = optimizer.optimize()
    optimization_end_time = time.perf_counter()         # End timer
    optimization_elapsed_time =  optimization_end_time -  optimization_start_time
    print(f"Time to optimize parameter: {optimization_elapsed_time} seconds")    

    run_time = setup_elapsed_time+optimization_elapsed_time
    print(f"Total Run Time: {run_time}")

    # Test Optimized Parameters
    print(f"\nOptimized Parameters: {optimized_parameters}\n")
    optimized_position_size, optimized_rsi_high, optimized_rsi_low, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight = optimizer.get_optimized_parameters()
    optimized_tester = tester(symbol, type, start_time, end_time, time_interval, optimized_rsi_high, optimized_rsi_low, optimized_position_size, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight)
    optimized_df = optimized_tester.test()
    optimized_pnl, optimized_roi, drawdown = calculate_pnl(optimized_df, optimized_position_size, optimized_take_profit, optimized_stop_loss)
    print(f"Optimized PnL: ${optimized_pnl:.2f}\t({optimized_roi*100:.2f}%)")
    
