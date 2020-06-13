import base64

TEXT_VERIFY = """
Czesc!

Twoja weryfikacja to: {}

Papa ;-)
"""

TEXT_FORGET = """
Czesc!

Zapomnialo sie?
Nie szkodzi, wejdz tu: {}

Papa ;-)
"""

def send_message_verify(email, recovery):
    args = f"{email}/{recovery}"
    args = base64.b64encode(args.encode('utf-8')).decode('utf-8')
    url = f"http://127.0.0.1:5000/verify/{args}"

    #print("-"*10)
    print(f"[SEND MESSAGE / VERIFY] to {email}")
    #print(TEXT_VERIFY.format(url))
    #print("-"*10)

    return url

def send_message_forget(email, recovery):
    args = f"{email}/{recovery}"
    args = base64.b64encode(args.encode('utf-8')).decode('utf-8')
    url = f"http://127.0.0.1:5000/forget/{args}"

    #print("-"*10)
    print(f"[SEND MESSAGE / FORGET] to {email}")
    #print(TEXT_FORGET.format(url))
    #print("-"*10)

    return url
