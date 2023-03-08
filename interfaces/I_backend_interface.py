from abc import ABC, abstractmethod
from data.models.qr_code import QRCode

class IQRInterface(ABC):

    @abstractmethod
    def get_qr_code(self, for_content: str) -> QRCode:
        pass
