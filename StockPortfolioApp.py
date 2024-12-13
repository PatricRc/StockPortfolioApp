import streamlit as st
import pandas as pd
import yfinance as yf

st.title("Stock Portfolio Tracker")

# Initialize an empty dataframe to store transactions if it does not exist in session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=["Symbol", "Date", "Shares", "Current Price", "Transaction Type"])


# Function to fetch current stock price using yfinance
def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period="1d")
    if not todays_data.empty:
        return todays_data['Close'].iloc[-1]
    return None

# Input for adding stock transactions
with st.form(key="add_transaction"):
    symbol = st.text_input("Stock Symbol")
    date = st.date_input("Purchase Date")
    shares = st.number_input("Number of Shares", min_value=1)
    transaction_type = st.selectbox("Transaction Type", ["Buy", "Sell"])
    submitted = st.form_submit_button("Add Transaction")

    if submitted:
        # Fetch current price only when a new transaction is submitted
        current_price = get_current_price(symbol)
        if current_price is not None:
          new_transaction = pd.DataFrame({"Symbol": [symbol], "Date": [date], "Shares": [shares], "Current Price": [current_price], "Transaction Type": [transaction_type]})
          st.session_state.transactions = pd.concat([st.session_state.transactions, new_transaction], ignore_index=True)
        else:
            st.error("Could not fetch current price for this ticker. Please check if the stock symbol is correct.")


# Function to calculate portfolio value
def calculate_portfolio_value(transactions_df):
  portfolio_value = 0
  if transactions_df.empty:
      return portfolio_value, pd.DataFrame()

  transactions_df["Current Price"] = transactions_df["Symbol"].apply(get_current_price)
  transactions_df["Value"] = transactions_df["Current Price"] * transactions_df["Shares"]
  portfolio_value = transactions_df["Value"].sum()
  return portfolio_value, transactions_df

# Update prices on existing holdings
if st.button("Update Prices"):
  portfolio_value, updated_transactions = calculate_portfolio_value(st.session_state.transactions.copy())
  st.session_state.transactions = updated_transactions
  st.session_state.portfolio_value = portfolio_value


# Display the transactions table
st.dataframe(st.session_state.transactions)

# Display the total portfolio value
if 'portfolio_value' in st.session_state:
    st.write(f"Total Portfolio Value: ${st.session_state.portfolio_value:.2f}")
