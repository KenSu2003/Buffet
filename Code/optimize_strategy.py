from bayes_opt import BayesianOptimization
import momentum_trading as momentum_trading
import strategy_tools

class BasicOptimization():
    def __init__(self, df, symbol, start_date, end_date, time_interval):
        self.symbol = symbol
        self.df = df
        self.start_date = start_date
        self.end_date = end_date
        self.time_interval = time_interval

    def objective(self, RSI_HIGH, RSI_LOW, POSITION_SIZE, TAKE_PROFIT, STOP_LOSS, RSI_WEIGHT=1, MACD_WEIGHT=1, BB_WEIGHT=1):
        RSI_HIGH = int(RSI_HIGH)
        RSI_LOW = int(RSI_LOW)
        POSITION_SIZE = int(POSITION_SIZE)
        TAKE_PROFIT = float(TAKE_PROFIT)
        STOP_LOSS = float(STOP_LOSS)
        RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT = RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT
        
        if RSI_HIGH <= RSI_LOW:
            return -9999

        momentum_trading.simulate_trades(self.df, RSI_HIGH, RSI_LOW, RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT)
        
        profit, roi = strategy_tools.calculate_pnl(self.df, TAKE_PROFIT, STOP_LOSS, POSITION_SIZE)
        
        return roi  # Directly maximize profit
    
    def optimize(self):
        pbounds = {
            'RSI_HIGH': (50, 100),
            'RSI_LOW': (0, 50),
            'POSITION_SIZE': (500, 2000),
            'TAKE_PROFIT': (1, 10),
            'STOP_LOSS': (1, 5),
            'RSI_WEIGHT': (0, 3),
            'MACD_WEIGHT': (0, 3),
            'BB_WEIGHT': (0, 3),
        }
        optimizer = BayesianOptimization(f=self.objective, pbounds=pbounds, verbose=2, random_state=1)
        optimizer.maximize(init_points=10, n_iter=100)
        
        return optimizer



'''
Rather than test everything.

Use machine learning by reflecting on the trades.

Learn which signals are positive (profitable) and which signals are negative (unprofitable). 

'''