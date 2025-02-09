
# Buffet V2

Buffet is part of a sophisticated Trading AI trained to perform and outperform human traders. Buffet V2 is an advanced trading algorithm that derives, tests, and optimizes trading strategies. It can perform paper trading or live trading on actual accounts, utilizing different optimizations to find the best parameters for trading. In this version we are focused are rebuilding the software architecture and letting Buffet run on a paper trading brokerage. 

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/KenSu2003/Buffet.git
    cd Buffet
    git checkout branchForV2
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. If the installation does not work follow these steps:
    ```bash
    < Install TA-Lib >
    pip install numpy==1.26.4
    brew install ta-lib
    pip install TA-Lib

    < Install Bayesian Optimization >
    pip install bayesian-optimization

    < Install Alapaca API >
    pip install alpaca-py

    < Install Other Tools >
    pip install pandas
    pip install matplotlib
    pip install apscheduler
    ```

## Usage

1. **Set the Correct Parameters**:  
   Ensure you’ve correctly configured key parameters like timeframes, thresholds, and risk limits in `paper_trading.py`.

2. **Switch or Write a New Strategy (If Needed)**:  
   - Pick or write a strategy in `strategies.py`.  
   - Modify the `strategy` variable in `paper_trading.py` to select the appropriate strategy.  

3. **Modify Optimizers (If Needed)**:  
   - Edit or switch optimizers in the `optimizers.py` file.  
   - Update the corresponding optimizer reference in `paper_trading.py`.  

4. **Run `paper_trading.py`**:  
   Execute the `paper_trading.py` script to start paper trading with the selected strategy and parameters.

   ```bash
   python Buffet/Code/paper_trading.py
   ```

5. **Run the Shell File (Optional)**:  
   Use the provided `automated_testing.sh` to automate the execution of `paper_trading.py` with background logging.

   ```bash
   ./Buffet/automated_testing.sh
   ```

## Features

- **Technical Indicators**: Utilizes various technical indicators to predict market movements.
- **Simulated Trading**: Allows for backtesting and strategy optimization in a simulated environment.
- **Risk Management**: Includes modules for setting take-profit and stop-loss levels to manage risk.
- **Live Trading**: Capable of executing trades in a live market environment.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
