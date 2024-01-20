import requests, os, time, json
from datetime import datetime
from uuid import uuid4
import random
import binascii
import numpy as np
import pandas as pd
from captcha.image import ImageCaptcha
def generate_key():
    return str(random.randint(10, 1000))
    return binascii.hexlify(os.urandom(20)).decode()
cwd = os.getcwd()
def currentTime(wdm="both"):
    now = datetime.now()
    if wdm == "date":
        return now.strftime("%d/%m/%y")
    elif wdm == "time":
        return now.strftime("%H:%M:%S")
    else:
        return now.strftime("%d/%m/%y %H:%M:%S")
    
def clog(comment, error=None):
    if error == None:
        error = ""
    else:
        error = f"[{error}]"
    clog_Str = f"[{currentTime()}] [{comment}] {error}"
    print(f"[+] {clog_Str}")
    try:
        with open(f"{cwd}/logs/central_logs", "a") as logger:
            logger.write(clog_Str+"\n")
            logger.close()
    except Exception as error:
        print("Error faced while logging log")
def cl(config_name: str):
    config_dir = cwd+"/configs"
    if config_name.endswith(".json"):
        pass
    else:
        config_name+= ".json"
    return json.load(open(f"{config_dir}/{config_name}", "r"))
        
def transaction_validator(details):
    tC = cl("transaction")  
    
    tVSchema = tC['valid_transaction_schema']
    if details['transaction_type'] in tVSchema['transaction_type']:
        if "sendparent" not in details:
            details['sendparent'] = "off"
        else:
            pass
        if details['sendparent'] in tVSchema['sendparent']:
            dump_dir = tC['dump_dir']
            response_name = generate_key()
            open(f"{cwd}{dump_dir}/{response_name}.json", "w").write(json.dumps(details, indent=4))
            return True
        else:
            return False
    else: 
            return False
class DashCalc:
    def __init__(self, today_user_data):
        self.user_data = today_user_data
        # print(self.user_data)
        # print(type(today_user_data))
    def calculate_total_spent(self):
        spents_values = []

        for i in self.user_data:
            if int(i.gone) != 0:
                # print(f"Found {i.gone}")
                spents_values.append(int(i.gone))
            else:
                continue
                # print(f"Not Found {i.gone}")
        # print("s",result)
        spents_values = np.array(spents_values)
        sum = 0
        for i in spents_values:
            sum = sum + int(i)
        # print("t",sum)
        return sum
    def calculate_total_income(self):

        spents_values = []

        for i in self.user_data:
            if int(i.come) != 0:
                # print(f"Found {i.gone}")
                spents_values.append(int(i.come))
            else:
                pass
                # print(f"Not Found {i.come}")
        # print("s",result)
        spents_values = np.array(spents_values)
        sum = 0
        for i in spents_values:
            sum = sum + int(i)
        # print("t",sum)
        return sum



if __name__ == "__main__":
    pass
    #changes for pushing project
