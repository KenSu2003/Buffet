import pandas as pd

class SignalBacktester:
    def __init__(self, initial_balance=10000, position_size_ratio=0.1):
        """
        Initializes the backtester with starting balance and position size settings.
        """
        self.initial_balance = initial_balance
        self.position_size_ratio = position_size_ratio
        self.balance = initial_balance

    def simulate_trades(self, df):
        """
        Simulate trades based on signals and update the portfolio over time.

        Args:
            df (pd.DataFrame): The DataFrame containing market data and signals.

        Returns:
            pd.DataFrame: The updated DataFrame with profit/loss and balance tracking.
        """
        position = 0  # 1 for long, -1 for short, 0 for no position
        entry_price = 0
        df['Trade_PnL'] = 0  # Track PnL for each trade
        df['Balance'] = self.balance  # Track portfolio balance over time

        # Handle initial rows with NaN signals (either skip or treat as 'no trade')
        df['Signal'] = df['Signal'].fillna(0)  # Set NaN signals to 'no trade'

        for i in range(len(df)):
            close_price = df['close'].iloc[i]
            signal = df['Signal'].iloc[i]
            trade_size = self.balance * self.position_size_ratio

            if position == 0:  # No open position
                if signal > 0:  # Long signal
                    position = 1
                    entry_price = close_price
                elif signal < 0:  # Short signal
                    position = -1
                    entry_price = close_price

            elif position == 1:  # Long position
                if signal <= 0:  # Exit long position
                    pnl = (close_price - entry_price) * (trade_size / entry_price)
                    self.balance += pnl  # Update balance with profit or loss
                    df.at[df.index[i], 'Trade_PnL'] = pnl
                    position = 0  # Close position

            elif position == -1:  # Short position
                if signal >= 0:  # Exit short position
                    pnl = (entry_price - close_price) * (trade_size / entry_price)
                    self.balance += pnl  # Update balance with profit or loss
                    df.at[df.index[i], 'Trade_PnL'] = pnl
                    position = 0  # Close position

            # Update balance in the DataFrame
            df.at[df.index[i], 'Balance'] = self.balance

        return df


    def calculate_metrics(self, df):
        """
        Calculate key performance metrics such as total profit, drawdown, and ROI.

        Args:
            df (pd.DataFrame): The DataFrame with trading simulation results.

        Returns:
            dict: Performance metrics.
        """
        total_pnl = df['Trade_PnL'].sum()
        roi = (self.balance - self.initial_balance) / self.initial_balance * 100

        # Calculate drawdown
        balance_series = df['Balance'].cummax()
        drawdown_series = (df['Balance'] - balance_series) / balance_series
        max_drawdown = drawdown_series.min() * 100  # Convert to percentage

        return {
            'Total PnL': total_pnl,
            'ROI (%)': roi,
            'Max Drawdown (%)': max_drawdown
        }

if __name__ == "__main__":
    from paper_trading import datetime, TimeFrame, TimeFrameUnit
    from testing_tools import setup
    from tester import tester
    import strategies
    import time
    from classical_optimization import calculate_pnl, BasicOptimizer, SignalDependentOptimizer
    
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


    backtester = SignalBacktester(initial_balance=10000, position_size_ratio=0.1)
    strategy = strategies.Momentum(df)
    evaluated_df = strategy.evaluate_indicators()  # Generate signals using your strategy
    simulated_df = backtester.simulate_trades(evaluated_df)
    backtester = SignalBacktester(initial_balance=10000, position_size_ratio=0.1)
