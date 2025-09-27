import imaplib
import email
from email.header import decode_header
import base64
import re
from datetime import datetime
import mysql.connector as mysql
import settings as s

# --- IMAP (Gmail) Connection ---
imap_host = "imap.gmail.com"
imap_user = s.IMAP_USER
imap_pass = s.IMAP_PASS

email_body = ""

try:
    mail = imaplib.IMAP4_SSL(imap_host)
    mail.login(imap_user, imap_pass)
    mail.select("inbox")

    status, search_data = mail.search(None, 'FROM "no-reply@discovery.bank"')

    if status != "OK" or not search_data[0]:
        print("No Transaction Emails")
        emailID, subject, from_email, Emaildate, fullbody = None, None, None, None, None
    else:
        email_ids = search_data[0].split()
        latest_email_id = email_ids[-1]  # last one

        status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        raw_msg = msg_data[0][1]

        msg = email.message_from_bytes(raw_msg)

        # Extract headers
        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")

        from_email = msg.get("From")
        date_tuple = email.utils.parsedate_tz(msg.get("Date"))
        if date_tuple:
            Emaildate = datetime.fromtimestamp(
                email.utils.mktime_tz(date_tuple)
            ).strftime("%Y-%m-%d %H:%M:%S")

        emailID = latest_email_id.decode()

        # Extract body
        fullbody = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/html":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    paragraphs = re.findall(
                        r"<p>(.*?)</p>", body, re.IGNORECASE | re.DOTALL
                    )
                    for match in paragraphs:
                        cleaned = re.sub(r"<.*?>", "", match)
                        fullbody += cleaned + "\n"
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")
            paragraphs = re.findall(r"<p>(.*?)</p>", body, re.IGNORECASE | re.DOTALL)
            for match in paragraphs:
                cleaned = re.sub(r"<.*?>", "", match)
                fullbody += cleaned + "\n"

        email_body = fullbody

    mail.logout()

except Exception as e:
    print(f"IMAP error: {e}")
    exit()

print(email_body)


# --- SQL Server Connection ---

# try:
#     conn = mysql.connect(
#         host=s.DATABASE_HOSTNAME,
#         user=s.ACTIVE_USERNAME,
#         password=s.ACTIVE_USER_PWD,
#         database=s.ACTIVE_DATABASE,
#     )
#     cursor = conn.cursor()
#
#     if emailID and subject:
#         sql = """INSERT INTO MailImport
#                  (EmailID, VendorID, DateRecordCreated, EmailFrom, EmailSubject, EmailBody)
#                  VALUES (?, ?, ?, ?, ?, ?)"""
#         params = (emailID, 1, Emaildate, from_email, subject, fullbody)
#         cursor.execute(sql, params)
#         conn.commit()
#
#     cursor.close()
#     conn.close()
#
# except Exception as e:
#     print(f"SQL Server Error: {e}")
