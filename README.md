# Buffet V2

Buffet is part of a sophisticated Trading AI trained to perform and outperform human traders. Buffet V2 is an advanced trading algorithm that derives, tests, and optimizes trading strategies. It can perform paper trading or live trading on actual accounts, utilizing different optimizations to find the best parameters for trading.

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

To use Buffet, follow these steps:

1. **Strategy Selection**: Pick the strategy model you want to use for testing and trading. The strategies should be in **strategies.py**.

2. **Strategy Testing**: Test the selected strategy with set timeframe.
    Use the tester in **tester.py** to create testing objects for testing basic (given) parameters 
    and opimized paratemers derived from **optimizers.py**
    ```bash
    python 
    python train_model.py
    ```

3. **Simulated Trading**: Test the model in a simulated trading environment.
    ```bash
    python paper_trading.py
    ```

4. **Live Trading**: Deploy the model for live trading (ensure all safety checks and risk management protocols are in place).
    ```bash
    To be rolled out.
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
