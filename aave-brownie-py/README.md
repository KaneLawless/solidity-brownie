1. Swap ETH for WETH
2. Deposit some ETH in AAVE
3. Borrow some asset with the ETH collateral
    - Sell that borrowed asset (short selling)
4. Repay everything back

Testing:
Integration test: Kovan
Unit tests: Mainnet Fork
 -> Because we dont have any oracles we don't need to deploy mocks (don't need to mock responses)