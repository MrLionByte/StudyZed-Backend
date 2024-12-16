# First let's get jinja2
from jinja2 import Template

# We will need smtplib to connect to our smtp email server
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Read the Jinja2 email template
with open("template.html", "r") as file:
    template_str = file.read()

jinja_template = Template(template_str)

# Define email server and credentials
smtp_server = "smtp.server.com"
smtp_port = 587
sender_email = "fanunaf25@gmail.com"
sender_password = "nses jwwu fnya tbnl"

# Set up email server
server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls()
server.login(sender_email, sender_password)

# Define recipients and their details
# This can be read from some CSV file or passed from some other program or API
people_data = [
    {"name": "John Doe", "email": "konen50746@pokeline.com"},
    {"name": "Jane Smith", "email": "jane@example.com"},
    {"name": "Bob Johnson", "email": "bob@example.com"},
]

# Now we iterate over our data to generate and send custom emails to each
for person in people_data:
    # Create email content using Jinja2 template
    email_data = {
        "subject": "Greetings from Jinja Email",
        "greeting": f"Hello {person['name']}!",
        "message": "This is a sample email generated using Jinja2.",
        "sender_name": "GFG",
    }
    email_content = jinja_template.render(email_data)

    # Create the email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = person["email"]
    msg["Subject"] = email_data["subject"]

    # Attach the HTML content to the email
    msg.attach(MIMEText(email_content, "html"))

    # Print and send the email
    print(f"Sending email to {person['email']}:\n{email_content}\n\n")
    
    server.sendmail(sender_email, person["email"], msg.as_string())

# Close the server connection
server.quit()