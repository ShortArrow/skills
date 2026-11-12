CONVERTIBLE = {"pdf", "docx", "pptx"}


class Document:
    def __init__(self, name, file_type):
        self.name = name
        self.file_type = file_type
        self.is_uploaded = False
        self.is_converted = False
        self.is_locked = False


def can_convert(file_type, is_uploaded):
    return file_type in CONVERTIBLE and is_uploaded


def convert(doc):
    if not can_convert(doc.file_type, doc.is_uploaded):
        return None
    if doc.is_locked:
        return None
    doc.is_converted = True
    return doc.name + ".pdf"
