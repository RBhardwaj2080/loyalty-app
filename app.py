import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

DB_FILE = "loyalty.db"
POINTS_PER_DOLLAR = 10 # Business Rule: 10 points per $1 spent
GOLD_TIER_THRESHOLD = 500 # Business Rule: Spend $500 in a year for Gold

# --- Database Connection Function ---
def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False) # check_same_thread=False is needed for Streamlit
    # Return rows as dictionaries (easier to work with)
    conn.row_factory = sqlite3.Row
    return conn

# --- Database Helper Functions ---
def get_customer_by_email(email):
    """Finds a customer by their email address."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers WHERE email = ?", (email,))
    customer = cursor.fetchone()
    conn.close()
    return customer

def get_customer_point_balance(customer_id):
    """Calculates the current point balance for a customer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(points_change) FROM PointsLedger WHERE customer_id = ?", (customer_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] is not None else 0

def get_customer_point_history(customer_id):
    """Retrieves the point transaction history for a customer."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, transaction_type, points_change, note
        FROM PointsLedger
        WHERE customer_id = ?
        ORDER BY timestamp DESC
    """, (customer_id,))
    history = cursor.fetchall()
    conn.close()
    return history

def get_available_rewards():
    """Retrieves all available rewards from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT reward_id, name, points_cost FROM Rewards ORDER BY points_cost ASC")
    rewards = cursor.fetchall()
    conn.close()
    return rewards

def add_points_transaction(customer_id, points, transaction_type, note):
    """Adds a new transaction to the PointsLedger."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO PointsLedger (customer_id, points_change, transaction_type, note)
        VALUES (?, ?, ?, ?)
    """, (customer_id, points, transaction_type, note))
    conn.commit()
    conn.close()

def get_customer_spending_this_year(customer_id):
    """Calculates customer's total spending based on 'earn' transactions this year."""
    # Note: This is a simplified calculation based on points earned.
    # A real system would link points to specific order amounts.
    conn = get_db_connection()
    cursor = conn.cursor()
    current_year = datetime.now().year
    start_of_year = f"{current_year}-01-01 00:00:00"
    end_of_year = f"{current_year}-12-31 23:59:59"

    cursor.execute("""
        SELECT SUM(points_change)
        FROM PointsLedger
        WHERE customer_id = ?
        AND transaction_type = 'earn'
        AND timestamp BETWEEN ? AND ?
    """, (customer_id, start_of_year, end_of_year))
    result = cursor.fetchone()
    conn.close()
    points_earned_this_year = result[0] if result and result[0] is not None else 0
    # Assuming points_per_dollar, calculate approximate spending
    spending_this_year = points_earned_this_year / POINTS_PER_DOLLAR
    return spending_this_year


def update_customer_tier(customer_id):
    """Checks customer spending and updates tier if necessary."""
    spending = get_customer_spending_this_year(customer_id)
    new_tier = "Gold" if spending >= GOLD_TIER_THRESHOLD else "Standard"

    conn = get_db_connection()
    cursor = conn.cursor()
    # Get current tier first to avoid unnecessary updates
    cursor.execute("SELECT tier FROM Customers WHERE customer_id = ?", (customer_id,))
    current_tier = cursor.fetchone()['tier']

    if new_tier != current_tier:
        cursor.execute("UPDATE Customers SET tier = ? WHERE customer_id = ?", (new_tier, customer_id))
        conn.commit()
        st.success(f"Customer tier updated to {new_tier}!") # Give feedback in the app
    conn.close()


# --- Page Setup ---
st.set_page_config(
    page_title="UrbanThread Loyalty",
    page_icon="✨",
    layout="wide"
)

st.title("✨ UrbanThread Loyalty Program Dashboard ✨")
st.markdown("---") # Add a horizontal line

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Customer View", "Add Points (Purchase)", "Redeem Reward", "Customer Service"])
st.sidebar.markdown("---")
# Add a little status indicator for DB connection
try:
    conn_check = get_db_connection()
    st.sidebar.success("DB Connected")
    conn_check.close()
except Exception as e:
    st.sidebar.error(f"DB Error: {e}")


# --- Page Content ---
if page == "Customer View":
    st.header("👤 Customer View")

    # --- Input: Customer Email ---
    customer_email = st.text_input("Enter Customer Email:", key="customer_email_input_view")

    if customer_email:
        customer = get_customer_by_email(customer_email)

        if customer:
            st.subheader(f"Welcome, {customer['first_name']} {customer['last_name']}!")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Customer ID:** {customer['customer_id']}")
            with col2:
                st.write(f"**Current Tier:** {customer['tier']}")

            current_balance = get_customer_point_balance(customer['customer_id'])
            st.metric(label="Current Point Balance", value=f"{current_balance:,} Points ✨") # Added comma formatting
            st.markdown("---")

            # --- Show Point History ---
            st.subheader("Point Transaction History")
            history = get_customer_point_history(customer['customer_id'])

            if history:
                # Convert list of Row objects to DataFrame
                history_df = pd.DataFrame([dict(row) for row in history])
                # Reorder columns for better readability
                history_df = history_df[['timestamp', 'transaction_type', 'points_change', 'note']]
                # Optional: Format timestamp
                history_df['timestamp'] = pd.to_datetime(history_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
                st.dataframe(history_df.rename(columns={
                    'timestamp': 'Timestamp',
                    'transaction_type': 'Type',
                    'points_change': 'Points Change',
                    'note': 'Note'
                }), use_container_width=True)
            else:
                st.write("No point history found.")

        else:
            st.warning("Customer email not found. Please check the email address.")

elif page == "Add Points (Purchase)":
    st.header("🛒 Add Points (Simulate Purchase)")

    customer_email = st.text_input("Enter Customer Email:", key="customer_email_input_add")
    purchase_amount = st.number_input("Enter Purchase Amount ($):", min_value=0.01, step=0.01, format="%.2f", key="purchase_amount")
    order_id = st.text_input("Enter Order ID/Number:", key="order_id")

    if st.button("Add Points for Purchase", key="add_points_button"):
        if not customer_email or not purchase_amount or not order_id:
            st.warning("Please fill in all fields.")
        else:
            customer = get_customer_by_email(customer_email)
            if customer:
                points_to_add = int(purchase_amount * POINTS_PER_DOLLAR)
                transaction_note = f"Order #{order_id}"
                try:
                    add_points_transaction(customer['customer_id'], points_to_add, 'earn', transaction_note)
                    st.success(f"Successfully added {points_to_add} points for customer {customer_email} (Order: {order_id}).")
                    # Check and update tier after adding points
                    update_customer_tier(customer['customer_id'])
                except Exception as e:
                    st.error(f"Failed to add points: {e}")
            else:
                st.error("Customer email not found.")

elif page == "Redeem Reward":
    st.header("🎁 Redeem Reward")

    customer_email = st.text_input("Enter Customer Email:", key="customer_email_input_redeem")

    if customer_email:
        customer = get_customer_by_email(customer_email)
        if customer:
            st.write(f"Redeeming for: **{customer['first_name']} {customer['last_name']}**")
            current_balance = get_customer_point_balance(customer['customer_id'])
            st.write(f"Current Balance: **{current_balance:,} Points**")

            rewards = get_available_rewards()
            if not rewards:
                st.warning("No rewards currently available.")
            else:
                # Create a list of reward options for the selectbox
                reward_options = {f"{r['name']} ({r['points_cost']} Points)": r['reward_id'] for r in rewards}
                selected_reward_display = st.selectbox("Select Reward to Redeem:", options=reward_options.keys(), key="reward_select")

                if st.button("Redeem Selected Reward", key="redeem_button"):
                    selected_reward_id = reward_options[selected_reward_display]
                    
                    # Find the cost of the selected reward
                    selected_reward_cost = next((r['points_cost'] for r in rewards if r['reward_id'] == selected_reward_id), None)

                    if selected_reward_cost is None:
                        st.error("Selected reward not found.")
                    elif current_balance >= selected_reward_cost:
                        try:
                            # Add a negative transaction to the ledger
                            add_points_transaction(
                                customer['customer_id'],
                                -selected_reward_cost, # Note the negative sign
                                'redeem',
                                f"Redeemed: {selected_reward_display.split(' (')[0]}" # Get only the name
                            )
                            st.success(f"Successfully redeemed {selected_reward_display}! {selected_reward_cost} points deducted.")
                            st.balloons()
                            # Refresh balance display (optional, Streamlit often handles this)
                            # current_balance = get_customer_point_balance(customer['customer_id'])
                            # st.write(f"New Balance: **{current_balance:,} Points**")
                        except Exception as e:
                            st.error(f"Failed to redeem reward: {e}")
                    else:
                        st.error("Insufficient points to redeem this reward.")
        else:
            st.error("Customer email not found.")


elif page == "Customer Service":
    st.header("🛠️ Customer Service - Manual Point Adjustment")

    customer_email = st.text_input("Enter Customer Email:", key="customer_email_input_cs")
    points_to_adjust = st.number_input("Points to Add/Subtract (+/-):", step=1, key="points_adjust")
    reason = st.text_area("Reason for Adjustment:", key="reason_adjust")

    if st.button("Adjust Points", key="adjust_points_button"):
        if not customer_email or points_to_adjust == 0 or not reason:
            st.warning("Please fill in all fields (Points cannot be zero).")
        else:
            customer = get_customer_by_email(customer_email)
            if customer:
                try:
                    add_points_transaction(customer['customer_id'], points_to_adjust, 'manual_adjust', reason)
                    st.success(f"Successfully adjusted points by {points_to_adjust} for {customer_email}. Reason: {reason}")
                    # Check and update tier after adjustment
                    update_customer_tier(customer['customer_id'])
                except Exception as e:
                    st.error(f"Failed to adjust points: {e}")
            else:
                st.error("Customer email not found.")
                