import base64
import binascii
import hashlib
import hmac
import io
import json
import string
import struct
import time
import random
import urllib.parse
from random import choice

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from .log import logger

from dingraia.tools.debug import delog


def decrypt(encrypt_data, aes_key):
    key = base64.b64decode(aes_key + '=')
    encrypt_data = base64.b64decode(encrypt_data)
    iv = encrypt_data[:16]
    encrypted_msg = encrypt_data[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(encrypted_msg)
    msg_len = int.from_bytes(decrypted_data[:4], byteorder="big")
    msg = decrypted_data[4:4 + msg_len]
    return json.loads(msg.decode())


def encrypt(data, token, aesKey, appKey):
    aesKey = base64.b64decode(aesKey + '=')
    timestamp = str(int(time.time()*1000))
    nonce = ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 16))
    msg_len = struct.pack('>I', len(data))
    data_to_encrypt = nonce.encode('utf-8') + msg_len + (data + appKey).encode('utf-8')
    iv = aesKey[:16]
    cipher = AES.new(aesKey, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(data_to_encrypt, AES.block_size))
    encrypted_msg = base64.b64encode(encrypted_data).decode('utf-8')
    signature = hashlib.sha1(''.join(sorted([nonce, timestamp, token, encrypted_msg])).encode()).hexdigest()
    return {'msg_signature': signature, 'encrypt': encrypted_msg, 'timeStamp': timestamp, 'nonce': nonce}


def sign_js(Token, AES_KEY, AppKey):
    return encrypt("success", Token, AES_KEY, AppKey)


@logger.catch
def get_sign(secure_key: str):
    timestamp = str(round(time.time() * 1000))
    sign_str = timestamp + '\n' + secure_key
    sign = hmac.new(secure_key.encode("utf-8"), sign_str.encode("utf-8"), hashlib.sha256).digest()
    sign = base64.b64encode(sign)
    sign = urllib.parse.quote_plus(sign)
    delog.success(f"成功加签", no=40)
    return sign, timestamp


class DingCallbackCrypto3:
    def __init__(self, token, encodingAesKey, key):
        self.encodingAesKey = encodingAesKey
        self.key = key
        self.token = token
        self.aesKey = base64.b64decode(self.encodingAesKey + '=')
    
    # 生成回调处理完成后的success加密数据
    def getEncryptedMap(self, content):
        encryptContent = self.encrypt(content)
        timeStamp = str(int(time.time()))
        nonce = self.generateRandomKey(16)
        sign = self.generateSignature(nonce, timeStamp, self.token, encryptContent)
        return {'msg_signature': sign, 'encrypt': encryptContent, 'timeStamp': timeStamp, 'nonce': nonce}
    
    # 解密钉钉发送的数据
    def getDecryptMsg(self, msg_signature, timeStamp, nonce, content):
        """
        解密
        :param msg_signature: 消息体签名
        :param timeStamp: 时间戳
        :param nonce: 随机字符串
        :param content: 钉钉返回的encrypt字段
        :return:
        """
        sign = self.generateSignature(nonce, timeStamp, self.token, content)
        # print(sign, msg_signature)
        if msg_signature != sign:
            raise ValueError('signature check error')
        content = base64.decodebytes(content.encode('UTF-8'))  # 钉钉返回的消息体
        iv = self.aesKey[:16]  # 初始向量
        aesDecode = AES.new(self.aesKey, AES.MODE_CBC, iv)
        decodeRes = aesDecode.decrypt(content)
        pad = int(decodeRes[-1])
        if pad > 32:
            raise ValueError('Input is not padded or padding is corrupt')
        decodeRes = decodeRes[:-pad]
        l = struct.unpack('!i', decodeRes[16:20])[0]
        nl = len(decodeRes)
        if decodeRes[(20 + l):].decode() != self.key:
            raise ValueError(f'corpId 校验错误:{decodeRes[(20 + l):].decode(), self.key}')
        return decodeRes[20:(20 + l)].decode()
    
    def encrypt(self, content):
        """
        加密
        :param content: 要加密的消息体
        :return: 加密完成的字符串
        """
        msg_len = self.length(content)
        content = ''.join([self.generateRandomKey(16), msg_len.decode(), content, self.key])
        contentEncode = self.pks7encode(content).encode()
        iv = self.aesKey[:16]
        aesEncode = AES.new(self.aesKey, AES.MODE_CBC, iv)
        aesEncrypt = aesEncode.encrypt(contentEncode)
        return base64.encodebytes(aesEncrypt).decode('UTF-8')
    
    # 生成回调返回使用的签名值
    @staticmethod
    def generateSignature(nonce, timestamp, token, msg_encrypt):
        # print(type(nonce), type(timestamp), type(token), type(msg_encrypt))
        v = msg_encrypt
        signList = ''.join(sorted([nonce, timestamp, token, v]))
        return hashlib.sha1(signList.encode()).hexdigest()
    
    @staticmethod
    def length(content):
        """
        将msg_len转为符合要求的四位字节长度
        :param content:
        :return:
        """
        l = len(content)
        return struct.pack('>l', l)
    
    @staticmethod
    def pks7encode(content):
        """
        安装 PKCS#7 标准填充字符串
        :param content: str
        :return: str
        """
        l = len(content)
        output = io.StringIO()
        val = 32 - (l % 32)
        for _ in range(val):
            output.write('%02x' % val)
        # print "pks7encode",content,"pks7encode", val, "pks7encode", output.getvalue()
        return content + binascii.unhexlify(output.getvalue()).decode()
    
    @staticmethod
    def pks7decode(content):
        nl = len(content)
        val = int(binascii.hexlify(content[-1]), 16)
        if val > 32:
            raise ValueError('Input is not padded or padding is corrupt')
        
        l = nl - val
        return content[:l]
    
    @staticmethod
    def generateRandomKey(size,
                          chars=string.ascii_letters + string.ascii_lowercase + string.ascii_uppercase + string.digits):
        """
        生成加密所需要的随机字符串
        :param size:
        :param chars:
        :return:
        """
        return ''.join(choice(chars) for i in range(size))
