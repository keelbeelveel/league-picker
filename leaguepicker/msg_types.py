# Script modified: Sun May 02, 2021 @ 02:30:07 EDT

def code_msg(msg, form=""):
    """Return message content in discord marked format (red)."""
    if form == "diff":
        msg = "- " + msg
    elif form == "json":
        msg = "{\n" + msg + "\n}"
    return f'''```{form}\n{msg}\n```'''

