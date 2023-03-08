from constants.backend_util import BackendUtil
# import requests


def get_raw_qr(for_content: str):
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Host": "qrcode3.p.rapidapi.com",
        "X-RapidAPI-Key": "{}".format(BackendUtil.rapid_api_key)
    }

    payload = {
        "data": for_content,
        "style": {
            "module": {
                "color": "black",
                "shape": "default"
            },
            "inner_eye": {"shape": "default"},
            "outer_eye": {"shape": "default"},
            "background": {
                "color": "white"
            }
        },
        "size": {
            "width": 100,
            "quiet_zone": 0,
            "error_correction": "M"
        },
        "output": {
            "filename": "Random recipe",
            "format": "jpeg"
        }
    }

    try:

        respone = requests.request("POST", BackendUtil.qr_text_endpoint, json=payload, headers=headers)
        return respone

    except Exception as e:
        print("Could not fetch QR Code \n")
        print("Error code: {}".format(e))
