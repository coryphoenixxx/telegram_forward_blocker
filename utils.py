def keytoint(d: dict):
    return {int(k) if k.lstrip('-').isdigit() else k: v for k, v in d.items()}
