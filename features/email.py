from simplegmail import Gmail

def send_email(to,sender,subject,main_body):

    gmail = Gmail()

    params = {"to":to,"sender":sender,"subject":subject,"msg_html":main_body,"signature":True}
    
    messages = gmail.send_message(**params)

    return "Email sent successfully."

def check_unread_emails():
    return

def check_starred_emails():
    return