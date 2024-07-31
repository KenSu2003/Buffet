import numpy as np

def calculate_optimal_f(returns):
    """
    Calculate the optimal fraction of capital to risk per trade using the Kelly criterion.
    
    Parameters:
    returns (list or np.array): Array of historical returns.
    
    Returns:
    float: The optimal fraction of capital to risk per trade.
    """
    if len(returns) == 0:
        return 0  # Avoid division by zero for empty returns
    
    # Calculate win probability (p) and loss probability (q)
    win_rate = np.mean(returns > 0)
    loss_rate = 1 - win_rate
    
    # Calculate average win (b) and average loss
    average_win = np.mean(returns[returns > 0])
    average_loss = -np.mean(returns[returns < 0])
    
    if average_loss == 0 or np.isnan(average_loss):  # Avoid division by zero and handle NaN
        return 0
    
    # Calculate optimal f using Kelly criterion
    optimal_f = (average_win * win_rate - average_loss * loss_rate) / (average_win * average_loss)
    
    return max(0, min(optimal_f, 1))  # Ensure optimal f is within the range [0, 1]

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    """
    Calculate the Sharpe ratio of a portfolio.
    
    Parameters:
    returns (list or np.array): Array of historical returns.
    risk_free_rate (float): The risk-free rate, default is 0.0.
    
    Returns:
    float: The Sharpe ratio.
    """
    if len(returns) == 0:
        return 0  # Avoid division by zero for empty returns
    
    excess_returns = returns - risk_free_rate
    mean_excess_return = np.mean(excess_returns)
    std_excess_return = np.std(excess_returns)
    
    if std_excess_return == 0 or np.isnan(std_excess_return):  # Avoid division by zero and handle NaN
        return 0
    
    sharpe_ratio = mean_excess_return / std_excess_return
    
    return sharpe_ratio

def calculate_order_size_dynamic(current_balance, historical_returns, signal, risk_free_rate=0.0, risk_ratio=1.0, shape_adjustment=1.0):
    """
    Calculate the order size using the Dynamic Position Sizing Model.
    
    Parameters:
    current_balance (float): The current account balance.
    historical_returns (list or np.array): Array of historical returns.
    signal (float): The trading signal strength.
    risk_free_rate (float): The risk-free rate, default is 0.0.
    risk_ratio (float): The risk/reward ratio, default is 1.0.
    shape_adjustment (float): The adjustment factor based on the shape of the return distribution, default is 1.0.
    
    Returns:
    float: The calculated order size.
    """
    if -1 <= signal <= 1:
        return 0  # No trade
    
    optimal_f = calculate_optimal_f(historical_returns)
    sharpe_ratio = calculate_sharpe_ratio(historical_returns, risk_free_rate)
    
    if optimal_f == 0 or sharpe_ratio == 0:  # Avoid zero order size due to zero optimal_f or sharpe_ratio
        return 0
    
    risk_adjustment = sharpe_ratio * risk_ratio * shape_adjustment * abs(signal)
    
    order_size = current_balance * optimal_f * risk_adjustment
    
    return max(0, order_size)  # Ensure order size is non-negative

# Example usage
historical_returns = np.array([0.01, 0.02, -0.015, 0.03, -0.005, 0.01, -0.02, 0.015])  # Example returns
current_balance = 100000  # Example current balance
signal = 1.5  # Example signal strength
risk_free_rate = 0.01  # Example risk-free rate
risk_ratio = 1.5  # Example risk/reward ratio
shape_adjustment = 0.9  # Example shape adjustment factor

order_size = calculate_order_size_dynamic(current_balance, historical_returns, signal, risk_free_rate, risk_ratio, shape_adjustment)
print(f"Calculated Order Size: ${order_size:.2f}")
