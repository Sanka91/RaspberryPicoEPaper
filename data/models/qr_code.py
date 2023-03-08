
class QRCode:

    def __init__(self, bytestring: bytes):
        self.bytestring = bytestring

    @classmethod
    def from_bytestring(cls, qr_bytestring: bytes):
        return QRCode(bytestring=qr_bytestring)

