from bayes_opt import BayesianOptimization, Events
import momentum_trading as momentum_trading
import strategy_tools
import yfinance as yf

class optimization():

    def __init__(self, 
                 symbol, 
                 start_date, end_date, time_interval):
        
        self.symbol = symbol

        # Time (time-period, time-interval)
        self.start_date = start_date
        self.end_date = end_date
        self.time_interval = time_interval


    def objective(self, RSI_HIGH, RSI_LOW, POSITION_SIZE, TAKE_PROFIT, STOP_LOSS):
        # Adjust types as Bayesian Optimization works with float
        RSI_HIGH = int(RSI_HIGH)
        RSI_LOW = int(RSI_LOW)
        POSITION_SIZE = int(POSITION_SIZE)
        TAKE_PROFIT = float(TAKE_PROFIT)
        STOP_LOSS = float(STOP_LOSS)
        RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT = 1, 1, 1

        # Enforce the constraint that RSI_HIGH must be greater than RSI_LOW
        if RSI_HIGH <= RSI_LOW:
            return -9999  # Return a very low number to indicate an invalid set of parameters

        # Load data
        symbol = self.symbol
        start_date = self.start_date
        end_date = self.end_date
        interval = self.time_interval
        df = strategy_tools.setup(symbol,start_date,end_date,interval)
        df = momentum_trading.trade(df, RSI_HIGH, RSI_LOW, RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT)
        
        # Calculate profitability
        profit, roi = strategy_tools.calculate_pnl(df, TAKE_PROFIT, STOP_LOSS, POSITION_SIZE)
        return roi  # Directly maximize profit
    
    def optimize(self):
        # Define parameter bounds
        pbounds = {
            'RSI_HIGH': (50, 100),
            'RSI_LOW': (0, 50),
            'POSITION_SIZE': (500, 2000),
            'TAKE_PROFIT': (1, 10),
            'STOP_LOSS': (1, 5)
        }

        optimizer = BayesianOptimization(
            f=self.objective,
            pbounds=pbounds,
            random_state=1,
            verbose=0
        )

        optimizer.maximize(
            init_points=10,
            n_iter=40,
        )

        return optimizer

        
optimizer = optimization('AMD', '2020-01-01', '2020-12-31', '1d').optimize()
print("Best parameters:", optimizer.max['params'])
print(f"Best profitability: {optimizer.max['target']*100:.2f}%")