from redis import StrictRedis
import requests
import json
import time
from loguru import logger

s = requests.Session()
client = StrictRedis(decode_responses=True)

logger.add(
    "process.log",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss:SSS} - {level} - {file} - {line} - {message}",
    rotation="10 MB",
)


def sendtx(toAddress, sendAmount):
    url = "http://127.0.0.1:5000/ckbsend"
    params = {"toAddress": toAddress, "sendAmount": sendAmount}
    z1 = s.get(url, params=params)
    rsp = z1.json()
    txhash = rsp["txhash"]
    if txhash == "error":
        return False
    return txhash


def do():
    while 1:
        time.sleep(0.5)
        waitsend = client.brpop("sendtoken")[1]
        waitsend = json.loads(waitsend)
        logger.info(f"准备处理 {waitsend}")
        txhash = sendtx(waitsend["address"], waitsend["amount"])
        if txhash:
            logger.info(f"代币发送成功,txhash:{txhash}")
        else:
            logger.error(f"代币发送失败,重新给他丢回队列")
            client.lpush("sendtoken", json.dumps(waitsend))


if __name__ == "__main__":
    do()
