from django.core.exceptions import ValidationError

import datetime
import re

def validate_appointment_date(value):
    today = datetime.date.today()
    if value < today:
        raise ValidationError('choose a future date ')
    return value 

def rate_validation(value):
    if value > 10 or value < 0:
        raise ValidationError("Value must be between 1 to 10")
    return value
def validate_amount(value):
    if value <= 0:
        raise ValidationError("Amount must be more than 0!")
    return value 

def validatePhoneNumber(value):
    if len(value) == 10 or len(value) == 13:
        if len(value) == 10:
            valid_phone_number_format = re.findall('(^0[0-9]+$)', value)
            # SHOULD RETURN ONLY ONE STRING VALUE IE A VALID PHONE NUMBER
            if len(valid_phone_number_format) == 1:
                if valid_phone_number_format[0] != value:
                    raise ValidationError('Please Enter a Valid Phone Number; follow the correct format of a phone number')
            else:
                raise ValidationError('Please Enter a Valid Phone Number; follow the correct format of a phone number')
        else:
            valid_phone_number_format = re.findall('(^\+254[0-9]+$)', value)
            print(re.findall('(^\+254[0-9]+$)', value))

            # SHOULD RETURN ONLY ONE STRING VALUE IE A VALID PHONE NUMBER
            if len(valid_phone_number_format) == 1:
                if valid_phone_number_format[0] != value:
                    raise ValidationError('Please Enter a Valid Phone Number; follow the correct format of a phone number')
            else:
                raise ValidationError('Please Enter a Valid Phone Number; follow the correct format of a phone number')
    else:
        raise ValidationError('Please Enter a valid phone number; the phone number is either too short or too long ')
    return value 




