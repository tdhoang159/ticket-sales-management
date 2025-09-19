import hashlib
import hmac
import urllib.parse
from datetime import datetime

class VNPAY:
    def __init__(self, vnp_TmnCode, vnp_HashSecret, vnp_Url, vnp_ReturnUrl):
        self.vnp_TmnCode = vnp_TmnCode
        self.vnp_HashSecret = vnp_HashSecret
        self.vnp_Url = vnp_Url
        self.vnp_ReturnUrl = vnp_ReturnUrl
        self.requestData = {}

    def add_param(self, key, value):
        if value is not None and value != "":
            self.requestData[key] = value

    def get_payment_url(self):
        sortedData = sorted(self.requestData.items())
        queryString = urllib.parse.urlencode(sortedData)

        hashValue = hmac.new(
            bytes(self.vnp_HashSecret, 'utf-8'),
            queryString.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        return f"{self.vnp_Url}?{queryString}&vnp_SecureHash={hashValue}"
