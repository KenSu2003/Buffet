from bayes_opt import BayesianOptimization
import strategy1
import strategy_tools
import yfinance as yf

def objective(RSI_HIGH, RSI_LOW, POSITION_SIZE, TAKE_PROFIT, STOP_LOSS):
    # Adjust types as Bayesian Optimization works with float
    RSI_HIGH = int(RSI_HIGH)
    RSI_LOW = int(RSI_LOW)
    POSITION_SIZE = int(POSITION_SIZE)
    TAKE_PROFIT = float(TAKE_PROFIT)
    STOP_LOSS = float(STOP_LOSS)

    # Load data
    symbol = 'AMD'
    start_date = '2020-01-01'
    end_date = '2020-12-31'
    interval = '1d'
    df = strategy_tools.setup(symbol,start_date,end_date,interval)
    df = strategy1.trade(df, RSI_HIGH, RSI_LOW)
    
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