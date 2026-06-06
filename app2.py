import streamlit as st
import pandas as pd
import hashlib
import io
from currency_converter import CurrencyConverter
from database import get_db_connection
from auth import authenticate_user
from ai_engine import extract_invoice_data
from email_service import send_dispute_email

# Initialize Dynamic Converter
c = CurrencyConverter()``

# --- PAGE CONFIG ---
st.set_page_config(page_title="FinOps AI", page_icon="🛡️", layout="wide")


# --- DYNAMIC MULTI-CURRENCY CONVERSION LOGIC ---
def get_dynamic_inr(amount, currency_code):
    try:
        if not currency_code:
            return amount * 83.0

        # Standardize common codes and symbols
        currency_code = currency_code.strip().lower()

        # Explicit Recognition for Indian Rupee to ensure 1:1 ratio
        if currency_code in ["₹", "rs", "rs.", "inr"]:
            return float(amount)

        symbol_map = {"$": "USD", "£": "GBP", "€": "EUR"}
        code = symbol_map.get(currency_code, currency_code).upper()

        return c.convert(amount, code, 'INR')
    except Exception:
        fallback_rates = {"USD": 83.0, "GBP": 125.0,
                          "EUR": 90.0, "CNY": 11.5, "INR": 1.0, "JPY": 0.58}
        return amount * fallback_rates.get(currency_code.upper() if currency_code else "", 83.0)


# --- EXCEL FORMATTER ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Monthly_Report')
        worksheet = writer.sheets['Monthly_Report']
        for col in worksheet.columns:
            max_length = max([len(str(cell.value)) for cell in col])
            worksheet.column_dimensions[col[0]
                                        .column_letter].width = max_length + 2
    return output.getvalue()


# --- 1. LOGIN SCREEN ---
def login_screen():
    st.title("🔐 FinOps Login")
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            user, msg = authenticate_user(u, p)
            if user:
                st.session_state.update(
                    {"logged_in": True, "user_id": user['id'], "user": user['username'], "role": user['role']})
                st.query_params.update(
                    {"authenticated": "true", "uid": user['id'], "uname": user['username'], "urole": user['role']})
                st.rerun()
            else:
                st.error(msg)


# --- 2. ADMIN PAGES ---
def admin_manage_invoices():
    st.header("📋 Master Invoice Ledger")
    conn = get_db_connection()
    # Fetches 'amount_inr' directly from database for 100% accuracy
    df = pd.read_sql("""
        SELECT i.filename, i.vendor_name, i.grand_total as 'Original Amount', 
        i.currency, i.amount_inr as 'Amount pay(INR)', i.status, 
        u.username as processed_by, i.upload_time 
        FROM invoices i 
        JOIN users u ON i.uploaded_by = u.id 
        ORDER BY i.upload_time DESC""", conn)
    conn.close()
    if not df.empty:
        approved_only_df = df[df['status'] == '🟢 Approved'].copy()
        if not approved_only_df.empty:
            st.dataframe(approved_only_df, use_container_width=True)

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                csv_buffer = io.StringIO()
                approved_only_df.to_csv(csv_buffer, index=False)
                st.download_button("Download Formatted CSV", csv_buffer.getvalue(
                ), "formatted_payments.csv", "text/csv")
            with col2:
                st.download_button("Download Formatted Excel", to_excel(
                    approved_only_df), "Monthly_Report.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No invoices processed yet.")


def admin_audit():
    st.header("🕵️ Security Audit Log")
    conn = get_db_connection()
    df = pd.read_sql("""
        SELECT u.username, a.action, a.timestamp 
        FROM audit_logs a 
        JOIN users u ON a.user_id = u.id 
        ORDER BY a.timestamp DESC""", conn)
    conn.close()
    st.dataframe(df, use_container_width=True)


def admin_analytics():
    st.header("📊 Financial Analytics Dashboard")
    conn = get_db_connection()
    # Use amount_inr for summing total spending
    df = pd.read_sql(
        "SELECT amount_inr, status, vendor_name, upload_time FROM invoices", conn)
    conn.close()

    if not df.empty:
        df['upload_time'] = pd.to_datetime(df['upload_time'])
        df['month_year'] = df['upload_time'].dt.to_period('M').astype(str)
        available_months = sorted(df['month_year'].unique(), reverse=True)
        selected_month = st.selectbox(
            "📅 Filter by Month", ["All Time"] + available_months)

        filtered_df = df.copy()
        if selected_month != "All Time":
            filtered_df = df[df['month_year'] == selected_month]

        c1, c2, c3 = st.columns(3)
        # Summing the stored INR values
        total_spent_inr = filtered_df['amount_inr'].sum()
        c1.metric(f"Spending ({selected_month})", f"₹{total_spent_inr:,.2f}")
        c2.metric("Invoices Processed", len(filtered_df))
        approved_count = len(
            filtered_df[filtered_df['status'] == '🟢 Approved'])
        acc = (approved_count / len(filtered_df)) * \
            100 if len(filtered_df) > 0 else 0
        c3.metric("Approval Rate", f"{acc:.1f}%")

        st.divider()
        st.subheader("Vendor Distribution")
        st.bar_chart(filtered_df['vendor_name'].value_counts())
    else:
        st.info("No data available.")


# --- 3. OPERATOR PAGES ---
def operator_upload():
    st.header("📤 Multi-Invoice Processing")
    uploaded_files = st.file_uploader(
        "Upload Invoices", type=['png', 'jpg', 'pdf'], accept_multiple_files=True)

    if uploaded_files:
        for f in uploaded_files:
            file_bytes = f.getvalue()
            file_hash = hashlib.md5(file_bytes).hexdigest()

            with st.spinner(f"Processing {f.name}..."):
                data = extract_invoice_data(file_bytes, f.type)

                if data:
                    st.write(f"### {f.name}")
                    st.json(data)

                if not data or data.get("Is_Receipt") is False:
                    st.error(
                        f"❌ Rejected: '{f.name}' is not a valid receipt/invoice.")
                    continue

                curr = data.get("Currency_Code") or data.get(
                    "Currency") or "USD"
                total = float(data.get("Grand_Total", 0))

                # Dynamic check for Indian Rupee
                total_inr = get_dynamic_inr(total, curr)

                sub, tax = float(data.get('Subtotal', 0)
                                 ), float(data.get('Tax', 0))
                status = "🟢 Approved" if abs(
                    (sub + tax) - total) < 0.05 else "🔴 Flagged"

                try:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    # Saving total_inr into amount_inr column
                    cur.execute("""
                        INSERT INTO invoices (filename, file_hash, vendor_name, vendor_email, grand_total, status, uploaded_by, currency, amount_inr) 
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                                (f.name, file_hash, data['Vendor_Name'], data['Vendor_Email'], total, status, st.session_state['user_id'], curr, total_inr))
                    conn.commit()
                    cur.close()
                    conn.close()

                    if "Flagged" in status and data['Vendor_Email']:
                        send_dispute_email(
                            data['Vendor_Email'], data['Vendor_Name'], sub, tax, total)

                    st.info(
                        f"🌍 Currency Detected: **{curr}** | Conversion: **₹{total_inr:,.2f} INR**")
                    st.success(f"✅ Processed {f.name}: {status}")

                except Exception as e:
                    if "1062" in str(e):
                        st.warning(
                            f"⚠️ Skipping '{f.name}': Already processed.")
                    else:
                        st.error(f"Error saving {f.name}: {e}")


def operator_comms():
    st.header("📞 Communication Hub")
    conn = get_db_connection()
    df = pd.read_sql(
        "SELECT vendor_name, vendor_email FROM invoices WHERE status LIKE '%Flagged%'", conn)
    conn.close()

    if df.empty:
        st.info("No follow-ups needed.")
    else:
        st.subheader("📧 Automated Email Sent")
        email_df = df[df['vendor_email'].str.strip() != ""]
        if email_df.empty:
            st.write("No vendors require email follow-up.")
        else:
            for i, row in email_df.iterrows():
                with st.expander(f"Contact: {row['vendor_name']}"):
                    st.success(f"**Email Sent To:** {row['vendor_email']}")
                    st.write(
                        "Dispute details have been automatically mailed to the vendor.")

        st.divider()

        st.subheader("📱 Manual Phone Call Needed")
        phone_df = df[df['vendor_email'].str.strip() == ""]
        if phone_df.empty:
            st.write("No manual calls required.")
        else:
            for i, row in phone_df.iterrows():
                with st.expander(f"Contact: {row['vendor_name']}"):
                    st.error("❌ No email found on receipt.")
                    st.write(
                        "**Action:** Please contact this vendor manually to clarify the flagged discrepancy.")


# --- MAIN NAVIGATION ---
params = st.query_params
if 'logged_in' not in st.session_state:
    if params.get("authenticated") == "true":
        st.session_state.update({"logged_in": True, "user_id": int(params.get(
            "uid")), "user": params.get("uname"), "role": params.get("urole")})
    else:
        st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login_screen()
else:
    with st.sidebar:
        st.title(f"👤 {st.session_state['user']}")
        # NAVIGATION LOGIC: Restored visibility for Admin Navigate panel
        if st.session_state['role'] == 'Admin':
            page = st.radio(
                "Navigate", ["Manage Invoices", "Security Audit", "Analytics Dashboard"])
        else:
            page = st.radio(
                "Navigate", ["Upload Invoice", "Communication Hub"])
        
        st.divider()
        if st.button("Logout"):
            st.session_state['logged_in'] = False
            st.query_params.clear()
            st.rerun()

    # Page Routing
    if page == "Manage Invoices":
        admin_manage_invoices()
    elif page == "Security Audit":
        admin_audit()
    elif page == "Analytics Dashboard":
        admin_analytics()
    elif page == "Upload Invoice":
        operator_upload()
    elif page == "Communication Hub":
        operator_comms()