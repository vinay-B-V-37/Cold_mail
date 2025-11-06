import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Bulk Email Sender", layout="centered")

st.title("📧 Bulk Email Sender with PDF Attachment")

st.markdown("Send the same email with a PDF attachment to multiple recipients using Gmail SMTP.")

# --- User Inputs ---
sender_email = st.text_input("Sender Gmail ID")
app_password = st.text_input("Gmail App Password", type="password")
subject = st.text_input("Email Subject")
body = st.text_area("Email Body (supports multiline text)", height=150)

uploaded_csv = st.file_uploader("Upload CSV File (must have 'email' column)", type=["csv"])
uploaded_pdf = st.file_uploader("Upload PDF Attachment", type=["pdf"])

# --- Send Email Function ---
def send_email(sender, password, recipient, subject, body, pdf_bytes, pdf_filename):
    try:
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        # Attach PDF
        part = MIMEApplication(pdf_bytes, Name=pdf_filename)
        part["Content-Disposition"] = f'attachment; filename="{pdf_filename}"'
        msg.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)

        return "✅ Sent"
    except Exception as e:
        return f"❌ Failed: {str(e)}"

# --- Send Button ---
if st.button("Send Emails"):
    if not sender_email or not app_password or not uploaded_csv or not uploaded_pdf:
        st.warning("Please fill all fields and upload both files.")
    else:
        df = pd.read_csv(uploaded_csv)
        if "email" not in df.columns:
            st.error("CSV file must have an 'email' column.")
        else:
            pdf_bytes = uploaded_pdf.read()
            pdf_filename = uploaded_pdf.name
            results = []

            st.info("Sending emails... Please wait ⏳")
            progress_bar = st.progress(0)

            for i, row in df.iterrows():
                recipient = row["email"]
                status = send_email(sender_email, app_password, recipient, subject, body, pdf_bytes, pdf_filename)
                results.append({"email": recipient, "status": status})
                progress_bar.progress((i + 1) / len(df))

            result_df = pd.DataFrame(results)
            st.success("Email sending completed! ✅")
            st.dataframe(result_df)

            # Download report
            csv_buffer = BytesIO()
            result_df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            st.download_button(
                label="⬇️ Download Result CSV",
                data=csv_buffer,
                file_name="email_send_report.csv",
                mime="text/csv",
            )
