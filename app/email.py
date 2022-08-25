import smtplib,ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

class Email:
    def __init__(self):
        self.port = Config.MAIL_PORT
        self.smtp_server_domain_name = Config.MAIL_SERVER
        self.sender_mail = Config.MAIL_USERNAME
        self.sender_pass = Config.MAIL_PASSWORD

    def send(self,text_template,html_template,subject_postfix,email_to):
        ssl_context = ssl.create_default_context()
        service = smtplib.SMTP_SSL(self.smtp_server_domain_name, self.port, context=ssl_context)
        service.login(self.sender_mail, self.sender_pass)

        mail = MIMEMultipart('alternative')
        mail['Subject'] = Config.MOBILE_MAIL_SUBJECT_PREFIX + subject_postfix
        mail['From'] = self.sender_mail
        mail['To'] = email_to


        html_content = MIMEText(html_template, 'html')
        text_content = MIMEText(text_template, 'plain')

        mail.attach(text_content)
        mail.attach(html_content)

        service.sendmail(self.sender_mail, email_to, mail.as_string())
        service.quit()