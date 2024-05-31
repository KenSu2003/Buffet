from bayes_opt import BayesianOptimization, Events
import strategy1
import strategy_tools
import yfinance as yf
import csv

def objective(RSI_HIGH, RSI_LOW, POSITION_SIZE, TAKE_PROFIT, STOP_LOSS):
    # Adjust types as Bayesian Optimization works with float
    RSI_HIGH = int(RSI_HIGH)
    RSI_LOW = int(RSI_LOW)
    POSITION_SIZE = int(POSITION_SIZE)
    TAKE_PROFIT = float(TAKE_PROFIT)
    STOP_LOSS = float(STOP_LOSS)
    RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT = 1, 1, 1

    # Load data
    symbol = 'AMD'
    start_date = '2020-01-01'
    end_date = '2020-12-31'
    interval = '1d'
    df = strategy_tools.setup(symbol,start_date,end_date,interval)
    df = strategy1.trade(df, RSI_HIGH, RSI_LOW, RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT)
    
    # Calculate profitability
    profit = strategy_tools.calculate_profitability(df, TAKE_PROFIT, STOP_LOSS, POSITION_SIZE)
    return profit  # Directly maximize profit

# Define parameter bounds
pbounds = {
    'RSI_HIGH': (20, 80),
    'RSI_LOW': (20, 80),
    'POSITION_SIZE': (500, 2000),
    'TAKE_PROFIT': (1, 10),
    'STOP_LOSS': (1, 5)
}

optimizer = BayesianOptimization(
    f=objective,
    pbounds=pbounds,
    random_state=1,
)

optimizer.maximize(
    init_points=10,
    n_iter=40,
)

print("Best parameters:", optimizer.max['params'])
print("Best profitability:", optimizer.max['target'])


# class Logger:
#     def __init__(self, file_path):
#         self.file_path = file_path
#         with open(self.file_path, mode='w', newline='') as file:
#             self.writer = csv.writer(file)
#             self.writer.writerow(['iter', 'target', 'POSITION_SIZE', 'RSI_HIGH', 'RSI_LOW', 'STOP_LOSS', 'TAKE_PROFIT'])

#     def update(self, event, optimizer, result):
#         with open(self.file_path, mode='a', newline='') as file:
#             self.writer = csv.writer(file)
#             self.writer.writerow([
#                 len(optimizer.res),  # Use the length of the results list to get the iteration number
#                 result['target'],
#                 result['params']['POSITION_SIZE'],
#                 result['params']['RSI_HIGH'],
#                 result['params']['RSI_LOW'],
#                 result['params']['STOP_LOSS'],
#                 result['params']['TAKE_PROFIT']
#             ])

# # Create a CSV file to store the results
# output_file = '/mnt/data/optimized_strategy_iterations.csv'
# logger = Logger(output_file)

# optimizer.subscribe(Events.OPTIMIZATION_STEP, logger.update)
# optimizer.maximize(
#     init_points=10,
#     n_iter=40,
# )