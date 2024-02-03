import ghasedakpack as ghasedak


def send_register_sms(receptor, code):
    sms = ghasedak.Ghasedak("ec460cd13f734e63c9cc3dbd58d0fef09fbdbac8f639a1bf26824b87bd88b49e")

    sms_verification = sms.verification(
        {'receptor': receptor, 'type': '1', 'template': 'RedShotPyContentSimplifierRegister', 'param1': code})

    return sms_verification


def send_forget_password_code_sms(receptor, code):
    sms = ghasedak.Ghasedak("ec460cd13f734e63c9cc3dbd58d0fef09fbdbac8f639a1bf26824b87bd88b49e")

    sms_verification = sms.verification(
        {'receptor': receptor, 'type': '1', 'template': 'RedShotPyContentSimplifierForgetPassword', 'param1': code})

    return sms_verification
