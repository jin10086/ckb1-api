from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import random, hashlib, json
from flask_pymongo import PyMongo

from redis import StrictRedis

client = StrictRedis(decode_responses=True)

parser = reqparse.RequestParser()
parser.add_argument("token", type=str)
parser.add_argument("name", type=str)

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
api = Api(app)
mongo = PyMongo(app)


todos = {}


def verifyToken(token, address, name):
    data = f"address:{address},name:{name}"

    # address = 'ckb1qyqz8j38uju4l93wfhtxrra4l4uu7uqqvktsj9wh0j'
    # name = '测试1'
    # 等待hash的参数.
    # 'address:ckb1qyqz8j38uju4l93wfhtxrra4l4uu7uqqvktsj9wh0j,name:测试1'

    # hash: 'eaa49aa14b58f3f842f9941df638bbd8f4079e68c2bbf73f913a0365701c4107'
    return token == hashlib.sha256(data.encode()).hexdigest()


def getTokenAmount():
    return random.randint(100, 100000)


class CKBApi(Resource):
    def get(self, address):
        user = mongo.db.users.find_one({"address": address})
        if not user:
            return {"status": 0, "msg": "address not found"}
        if user.get("tx"):
            tx = user["tx"]
        else:
            tx = ""
        return {
            "status": 1,
            "name": user["name"],
            "amount": user["amount"],
            "txhash": tx,
        }

    def post(self, address):
        args = parser.parse_args()
        name = args["name"]
        checktoken = args["checktoken"]

        # if not verifyToken(checktoken, address, name):
        #     return {{"status": 0, "msg": "参数校验失败."}}
        user = mongo.db.users.find_one({"address": address})
        if user:
            return {"status": 0, "msg": "代币已经发过了."}
        amount = getTokenAmount()
        # TODO: 添加到redis队列.队列按照顺序处理.
        client.lpush("sendtoken", json.dumps({"address": address, "amount": amount}))
        user = {"address": address, "name": name, "amount": amount}
        mongo.db.users.insert_one(user)
        return {"status": 1, "name": name, "amount": amount}


api.add_resource(CKBApi, "/address/<string:address>")

if __name__ == "__main__":
    app.run(debug=True,port=8000)
