import numpy as np
from bayes_opt import BayesianOptimization
from strategies import Momentum
from quantum_core import QuantumOptimizerWithCustomKernel
from testing_tools import simulate_trades, calculate_pnl

class BasicOptimizer():
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
            'position_size': (500, 10000),
            'take_profit': (1, 100),
            'stop_loss': (1, 10),
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


class QuantumOptimizer:
    def __init__(self, historical_data):
        """
        Initializes the optimizer with dynamic parameter bounds.

        Args:
            pbounds (dict): Dictionary containing parameter bounds (min, max) for each optimization variable.
            historical_data (pd.DataFrame): The historical price data for backtesting.
        """
        self.pbounds = {
            'rsi_high': (0, 100),
            'rsi_low': (0, 100),
            'position_size': (0, 10000),
            'take_profit': (1, 100),
            'stop_loss': (1, 100),
            'rsi_weight': (0, 3),
            'macd_weight': (0, 3),
            'bb_weight': (0, 3)
        }
        self.bounds = np.array([list(b) for b in self.pbounds.values()])
        self.historical_data = historical_data

        self.optimized_position_size = 0
        self.optimized_rsi_high = 0
        self.optimized_rsi_low = 0
        self.optimized_stop_loss = 0
        self.optimized_take_profit = 0

        self.optimized_rsi_weight = 0
        self.optimized_macd_weight = 0
        self.optimized_bb_weight = 0

    def optimize(self):
        """
        Run the quantum optimizer to determine optimal trading parameters.

        Returns:
            dict: Optimized parameters and their corresponding values.
        """
        feature_dimension = len(self.pbounds)

        # Generate initial guesses randomly within bounds
        initial_data = np.array([
            [np.random.uniform(low, high) for low, high in self.bounds] for _ in range(3)
        ])

        # Initialize the Quantum Optimizer
        optimizer = QuantumOptimizerWithCustomKernel(feature_dimension, self.bounds)

        # Assign the objective function for evaluation
        optimizer.objective_function = self.objective_function

        # Run the optimization process
        best_params, best_value = optimizer.optimize(initial_data)

        # Map optimized parameters back to their names
        optimized_params = {param: best_params[i] for i, param in enumerate(self.pbounds.keys())}

        self.optimized_position_size = optimized_params.get('position_size')
        self.optimized_rsi_high = optimized_params.get('rsi_high')
        self.optimized_rsi_low = optimized_params.get('rsi_low')
        self.optimized_stop_loss = optimized_params.get('stop_loss')
        self.optimized_take_profit = optimized_params.get('take_profit')

        self.optimized_rsi_weight = optimized_params.get('rsi_weight')
        self.optimized_macd_weight = optimized_params.get('macd_weight')
        self.optimized_bb_weight = optimized_params.get('bb_weight')

        # print("\nOptimized Parameters:")
        # for param, value in optimized_params.items():
        #     print(f"{param}: {value}")
        # print(f"Best Objective Value (ROI): {best_value}")

        return optimized_params

    def objective_function(self, params):
        """
        Objective function that evaluates the given parameters by running a backtest.

        Args:
            params (list): List of parameter values.
        Returns:
            float: The ROI from backtesting.
        """
        # Map parameter values to their names
        param_dict = {name: params[i] for i, name in enumerate(self.pbounds.keys())}

        # Extract the parameters for the trading strategy
        rsi_high = int(param_dict['rsi_high'])
        rsi_low = int(param_dict['rsi_low'])
        position_size = int(param_dict['position_size'])
        take_profit = float(param_dict['take_profit'])
        stop_loss = float(param_dict['stop_loss'])
        rsi_weight = param_dict.get('rsi_weight', 1)
        macd_weight = param_dict.get('macd_weight', 1)
        bb_weight = param_dict.get('bb_weight', 1)

        # Penalize invalid parameter combinations
        if rsi_high <= rsi_low:
            return -9999  # Large negative penalty to avoid invalid combinations

        # Evaluate the trading strategy using Momentum indicators
        strategy = Momentum(self.historical_data, rsi_high=rsi_high, rsi_low=rsi_low, 
                            rsi_weight=rsi_weight, macd_weight=macd_weight, bb_weight=bb_weight)
        evaluated_df = strategy.evaluate_indicators()

        # Simulate trades based on strategy
        evaluated_df = simulate_trades(evaluated_df)

        # Calculate profit and ROI
        profit, roi = calculate_pnl(evaluated_df, position_size, take_profit, stop_loss)

        # Return the ROI as the objective value
        return roi

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

    print(datetime.now())

    # Setup Optimizer
    setup_start_time = time.perf_counter()
    
    optimizer = BasicOptimizer(df)
    # optimizer = QuantumOptimizer(df)
    
    setup_end_time = time.perf_counter()
    setup_elapsed_time = setup_end_time - setup_start_time
    print(f"Time to setup optimizer: {setup_elapsed_time} seconds")

    # Optimize Parameters
    optimization_start_time = time.perf_counter()

    optimized_parameters = optimizer.optimize()
    
    optimization_end_time = time.perf_counter()
    
    print(f"\nOptimized Parameters: {optimized_parameters}\n")

    optimization_elapsed_time =  optimization_end_time -  optimization_start_time
    print(f"Time to optimize parameter: {optimization_elapsed_time} seconds")

    run_time = setup_elapsed_time+optimization_elapsed_time
    print(f"Total Run Time: {run_time}")

    # Test Optimized Parameters
    optimized_position_size, optimized_rsi_high, optimized_rsi_low, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight = optimizer.get_optimized_parameters()
    optimized_tester = tester(symbol, type, start_time, end_time, time_interval, optimized_rsi_high, optimized_rsi_low, optimized_position_size, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight)
    optimized_df = optimized_tester.test()
    optimized_pnl, optimized_roi = calculate_pnl(optimized_df, optimized_position_size, optimized_take_profit, optimized_stop_loss, )
    print(f"Optimized PnL: ${optimized_pnl:.2f}\t({optimized_roi*100:.2f}%)")
    
    print(datetime.now())

'''
Rather than test everything.

Use machine learning by reflecting on the trades.

Learn which signals are positive (profitable) and which signals are negative (unprofitable). 

'''