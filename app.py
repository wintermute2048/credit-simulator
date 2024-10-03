from datetime import datetime
from pandas.tseries.offsets import DateOffset

import streamlit as st
from textwrap import dedent

import pandas as pd

from credit import Credit
from side_fees import NOTARY_FEE_RATE, LAND_REGISTRY_FEE_RATE, STATES,\
    PROPERTY_TRANSFER_TAX


STATE_DEFAULT = STATES.index("Rhineland-Palatinate")

st.title("Credit Simulation App [WIP]")
st.write(dedent("""\
    This is a hobby project, accurate info is not guaranteed.
    In fact, some parts are approximate or not yet fully worked out.
    Use at own risk."""
))
col_project, col_credit = st.columns(2)

with col_project:
    st.header("Project")
    sale_price = 1e3*st.number_input(
        "Sale Price (k€)", min_value=0.0, step=10.0, value=280.)
    selected_state = st.selectbox("State", STATES, index=STATE_DEFAULT)
    bool_agent_fee = st.checkbox("Agent fee?", True)
    agent_fee = .01*st.number_input(
        "Agent fee (%, brutto)", min_value=0.0, step=0.1, value=3.57,
        disabled=not bool_agent_fee)
    
    # calculate side fees
    fees = {}
    fees["Property transfer tax"] = PROPERTY_TRANSFER_TAX[selected_state]
    fees["Notary fee rate"] = NOTARY_FEE_RATE
    fees["Land registry fee rate"] = LAND_REGISTRY_FEE_RATE
    if bool_agent_fee:
        fees["Agent fee rate"] = agent_fee
    
    # sum up
    side_fee_rate = sum(fees.values())
    fees["Total"] = side_fee_rate

    # Make a table
    df = pd.DataFrame().from_dict(fees, orient="index", columns=["Rate / %"])
    df.index.name = "Item"
    df["Rate / %"] *= 100 # Convert to %

    st.write(df)

    # derive values
    side_fees = side_fee_rate * sale_price
    total_price = sale_price + side_fees
    st.write(f"**Side Fees:** {side_fees:.2f} €")
    st.write(f"**Total price:** {total_price:.2f} €")

with col_credit:
    st.header("Credit")

    copayment = 1e3*st.number_input(
        "Copayment (k€)", min_value=0.0, max_value=total_price/1e3,
        step=10.0, value=200.)
    interest_rate = 1e-2*st.number_input(
        "Interest Rate (%)", min_value=0.0, step=0.1, value=3.2)
    monthly_payment = st.number_input(
        "Monthly Payment", min_value=0.0, step=100.0, value=1100.)
    extra_payment_fraction = 0.01*st.number_input(
        "Extra payment fraction", min_value=0.0,
        step=1., value=1.)
    
    credit_amount = total_price - copayment
    st.write(f"**Credit amount:** {credit_amount/1e3:.3f} k€")

    c = Credit(
        credit_amount, interest_rate, monthly_payment, extra_payment_fraction)
    
    if c.residual_debt > 0:
        st.write(f"**Residual Debt:** {c.residual_debt/1e3:.3f} k€")
    
    st.write(f"Extra payment (year): {c.extra_payment:.2f} €")
    st.write(f"Extra payment (month): {c.extra_payment/12:.2f} €")
    st.write(
        "**Effective monthly payment:** "
        f"{monthly_payment + c.extra_payment/12:.2f} €")
    duration_years = int(c.duration)
    duration_months = round((c.duration - duration_years) * 12)
    st.write(f"**Duration:** {int(c.duration)} years {duration_months} months")
    st.write(f"**Total paid interest:** {c.interest_total/1e3:.3f} / k€")

df = c.payment_plan
df["Date"] = datetime.today() + df["time"].apply(
    lambda t: DateOffset(months=t))

st.header("Payments")
rename_dict = {
    "extra_payment":    "(1) Extra payment",
    "repayment":        "(2) Repayment",
    "interest_payment": "(3) Interest payment",
}
st.bar_chart(
    df.rename(columns=rename_dict),
    x="Date", y=rename_dict.values())

st.header("Debt and Cumulative Payments")
rename_dict = {
    "paid interest":    "(1) Paid interest",
    "debt":             "(2) Debt",
    "paid debt":        "(3) Paid debt",
}
st.bar_chart(
    df.rename(columns=rename_dict),
    x="Date", y=rename_dict.values())

st.header("Payment Plan")
rename_dict = {
    "time": "Month",
    "debt": "Debt",
    "monthly_payment": "Monthly payment",
    "interest_payment": "Interest payment",
    "repayment": "Repayment",
    "extra_payment": "Extra payment",
}
df = df.rename(columns=rename_dict)
df = df[rename_dict.values()]
st.dataframe(df, hide_index=True)
