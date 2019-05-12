import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



def error_email(content):

    # Server Credentials
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"

    # Email Contents
    subject = "Backup Failed Confirmation Email!"
    body = content
    sender_email = "shah.developer87@gmail.com"
    password = input("Type your password and press enter: ")
    receiver_email = "sfiroz@razoyo.com" 

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    text = message.as_string()

    # Create a secure SSL context
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        
        # TODO: Send email here
        # Single Recipients
        server.sendmail(sender_email, receiver_email, text)
        print("Email sent!")



