




## 查询用户信息


请求方式: GET

请求网址: /gettoken/用户地址
比如： /gettoken/ckt1qyqd5eyygtdmwdr7ge736zw6z0ju6wsw7rssu8fcve

返回值有3种
1. `{"status": 0, "msg": "address not found"}`  用户还没有获取代币.
2. `{
            "status": 1,
            "name": "gaojin"
            "amount": 100,
            "txhash": "",
    }`  txhash为空表示请求了，等待打币中 

3. `{
            "status": 1,
            "name": "gaojin"
            "amount": 100,
            "txhash": "0x8d706a80d988475f9a46daf9a26429f6e5159091adb1e35790570de998f0db2b",
    }`  txhash有了，表示已经打币了



## 获取代币


请求方式：POST

请求网址: /gettoken/用户地址
比如： /gettoken/ckt1qyqd5eyygtdmwdr7ge736zw6z0ju6wsw7rssu8fcve

参数 name,checktoken 

name是用户输入的名字. 

checktoken是一个校验参数. 目前还没有卡.
就是先按照下面的规则拼接，然后 sha256,拿到返回的hash.
```
def verifyToken(checktoken, address, name):
    data = f"address:{address},name:{name}"

    # address = 'ckb1qyqz8j38uju4l93wfhtxrra4l4uu7uqqvktsj9wh0j'
    # name = '测试1'
    # 等待hash的参数.
    # 'address:ckb1qyqz8j38uju4l93wfhtxrra4l4uu7uqqvktsj9wh0j,name:测试1'

    # hash: 'eaa49aa14b58f3f842f9941df638bbd8f4079e68c2bbf73f913a0365701c4107'
    return checktoken == hashlib.sha256(data.encode()).hexdigest()
```

返回值有3种
1. ` {"status": 0, "msg": "参数校验失败."}` checktoken校验失败
2.  `{"status": 0, "msg": "代币已经发过了."}` 代币已经领取过了
3. `{"status": 1, "name": name, "amount": amount}` 返回用户领取数量以及名字.
 
