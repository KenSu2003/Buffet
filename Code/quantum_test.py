import numpy as np
from quantum_core import QuantumOptimizerWithCustomKernel
from strategies import Momentum
from testing_tools import simulate_trades, calculate_pnl


class OptimizerWithDynamicBounds:
    def __init__(self, pbounds, historical_data):
        """
        Initializes the optimizer with dynamic parameter bounds.

        Args:
            pbounds (dict): Dictionary containing parameter bounds (min, max) for each optimization variable.
            historical_data (pd.DataFrame): The historical price data for backtesting.
        """
        self.pbounds = pbounds
        self.bounds = np.array([list(b) for b in pbounds.values()])
        self.historical_data = historical_data

    def run_quantum_optimization(self):
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

        print("\nOptimized Parameters:")
        for param, value in optimized_params.items():
            print(f"{param}: {value}")
        print(f"Best Objective Value (ROI): {best_value}")

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


# Test code
if __name__ == "__main__":
    import pandas as pd

    # Dynamic parameter bounds
    pbounds = {
        'rsi_high': (50, 100),
        'rsi_low': (0, 50),
        'position_size': (500, 10000),
        'take_profit': (1, 100),
        'stop_loss': (1, 10),
        'rsi_weight': (0, 3),
        'macd_weight': (0, 3),
        'bb_weight': (0, 3)
    }

    # Example historical data (replace with real historical price data)
    historical_data = pd.DataFrame({
        'timestamp': pd.date_range(start='2022-01-01', periods=100, freq='D'),
        'close': np.random.uniform(50000, 60000, size=100),
        'rsi': np.random.uniform(10, 90, size=100)
    })

    # Initialize and run the optimizer with dynamic bounds
    optimizer = OptimizerWithDynamicBounds(pbounds, historical_data)
    optimized_parameters = optimizer.run_quantum_optimization()
