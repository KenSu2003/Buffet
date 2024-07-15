from bayes_opt import BayesianOptimization
from strategies import Momentum
import testing_tools as tools

class BasicOptimizer():
    def __init__(self, df, symbol, start_date, end_date, time_interval):
        self.symbol = symbol
        self.df = df
        self.start_date = start_date
        self.end_date = end_date
        self.time_interval = time_interval

        self.optimized_POSITION_SIZE = 0
        self.optimized_RSI_HIGH = 0
        self.optimized_RSI_LOW = 0
        self.optimized_STOP_LOSS = 0
        self.optimized_TAKE_PROFIT = 0

        self.optimized_RSI_WEIGHT = 0
        self.optimized_MACD_WEIGHT = 0
        self.optimized_BB_WEIGHT = 0


    def objective(self, POSITION_SIZE, RSI_HIGH, RSI_LOW, TAKE_PROFIT, STOP_LOSS, RSI_WEIGHT=1, MACD_WEIGHT=1, BB_WEIGHT=1):
        RSI_HIGH = int(RSI_HIGH)
        RSI_LOW = int(RSI_LOW)
        POSITION_SIZE = int(POSITION_SIZE)
        TAKE_PROFIT = float(TAKE_PROFIT)
        STOP_LOSS = float(STOP_LOSS)
        RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT = RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT
        
        if RSI_HIGH <= RSI_LOW:
            return -9999

        strategy = Momentum(self.df, RSI_HIGH=RSI_HIGH, RSI_LOW=RSI_LOW, RSI_WEIGHT=1, MACD_WEIGHT=1, BB_WEIGHT=1)
        self.df = strategy.evaluate_indicators()
        self.df = tools.simulate_trades(self.df)    # implement strategy, determine BUY/SELL signal    
        
        profit, roi = tools.calculate_pnl(self.df, POSITION_SIZE, TAKE_PROFIT, STOP_LOSS)
        
        return roi  # Directly maximize profit
    
    def optimize(self):
        pbounds = {
            'RSI_HIGH': (50, 100),
            'RSI_LOW': (0, 50),
            'POSITION_SIZE': (500, 2000),
            'TAKE_PROFIT': (1, 10),
            'STOP_LOSS': (1, 5),
            # 'TAKE_PROFIT': (1, 20),
            # 'STOP_LOSS': (1, 10),
            # 'TAKE_PROFIT': (1, 100),
            # 'STOP_LOSS': (1, 100),
            'RSI_WEIGHT': (0, 3),
            'MACD_WEIGHT': (0, 3),
            'BB_WEIGHT': (0, 3),
        }
        optimizer = BayesianOptimization(f=self.objective, pbounds=pbounds, verbose=0, random_state=1)
        optimizer.maximize(init_points=10, n_iter=100)

        self.optimized_POSITION_SIZE = optimizer.max['params'].get('POSITION_SIZE')
        self.optimized_RSI_HIGH = optimizer.max['params'].get('RSI_HIGH')
        self.optimized_RSI_LOW = optimizer.max['params'].get('RSI_LOW')
        self.optimized_STOP_LOSS = optimizer.max['params'].get('STOP_LOSS')
        self.optimized_TAKE_PROFIT = optimizer.max['params'].get('TAKE_PROFIT')

        self.optimized_RSI_WEIGHT = optimizer.max['params'].get('RSI_WEIGHT')
        self.optimized_MACD_WEIGHT = optimizer.max['params'].get('MACD_WEIGHT')
        self.optimized_BB_WEIGHT = optimizer.max['params'].get('BB_WEIGHT')
        
        return optimizer.max['params']

    def get_optimized_parameters(self):
        return self.optimized_POSITION_SIZE, self.optimized_RSI_HIGH, self.optimized_RSI_LOW, self.optimized_TAKE_PROFIT, self.optimized_STOP_LOSS, self.optimized_RSI_WEIGHT, self.optimized_MACD_WEIGHT, self.optimized_BB_WEIGHT


# ———————————————————— Test ——————————————————————


'''
Rather than test everything.

Use machine learning by reflecting on the trades.

Learn which signals are positive (profitable) and which signals are negative (unprofitable). 

'''