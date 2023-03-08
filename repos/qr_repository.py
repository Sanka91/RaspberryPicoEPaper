from data.models.qr_code import QRCode
from data.data_providers.raw_data_provider_functions import get_raw_qr


class QRRepository:

    @classmethod
    def generate_qr_code(cls, for_content: str) -> QRCode:
        response = get_raw_qr(for_content=for_content)

        return QRCode.from_bytestring(qr_bytestring=response.content)

