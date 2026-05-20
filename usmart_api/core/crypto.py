# -*- coding: utf-8 -*-
"""
加密工具模块

提供RSA加密、MD5withRSA签名、序列号生成等功能。
兼容原版 openapi-demo-py 的 EncryptUtil
"""

import base64
import time
import random
from typing import Optional

# 尝试导入 rsa 库，如果不存在则使用 pycryptodome
try:
    import rsa
    HAS_RSA = True
except ImportError:
    HAS_RSA = False
    from Crypto.Hash import MD5
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5
    from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme


class EncryptUtil:
    """
    加密工具类
    
    提供RSA加密解密、MD5withRSA签名等功能。
    兼容原版 openapi-demo-py 的密钥格式。
    
    Attributes:
        public_key: RSA公钥
        private_key: RSA私钥
    """
    
    def __init__(self, public_key_str: str, private_key_str: str):
        """
        初始化加密工具
        
        Args:
            public_key_str: RSA公钥字符串（PEM格式或裸钥）
            private_key_str: RSA私钥字符串（PEM格式或裸钥）
        """
        self._has_rsa = HAS_RSA
        
        if self._has_rsa:
            # 使用 rsa 库（重写版方式）
            self._init_with_rsa_lib(public_key_str, private_key_str)
        else:
            # 使用 pycryptodome 库（原版方式）
            self._init_with_pycryptodome(public_key_str, private_key_str)
    
    def _init_with_rsa_lib(self, public_key_str: str, private_key_str: str):
        """使用 rsa 库初始化"""
        # 加载公钥
        if '-----BEGIN PUBLIC KEY-----' in public_key_str:
            self.public_key = rsa.PublicKey.load_pkcs1_openssl_pem(public_key_str.encode())
        else:
            self.public_key = rsa.PublicKey.load_pkcs1(public_key_str.encode())
        
        # 加载私钥
        if '-----BEGIN RSA PRIVATE KEY-----' in private_key_str:
            self.private_key = rsa.PrivateKey.load_pkcs1(private_key_str.encode())
        else:
            self.private_key = rsa.PrivateKey.load_pkcs1(private_key_str.encode())
    
    def _init_with_pycryptodome(self, public_key_str: str, private_key_str: str):
        """使用 pycryptodome 库初始化（原版方式）"""
        charset = "utf-8"
        # 原版密钥格式是反的：public_key 用 PRIVATE KEY 标记，private_key 用 PUBLIC KEY 标记
        pub_key_pem = ("-----BEGIN PRIVATE KEY-----\n%s\n-----END PRIVATE KEY-----" % public_key_str).encode(charset)
        pri_key_pem = ("-----BEGIN PUBLIC KEY-----\n%s\n-----END PUBLIC KEY-----" % private_key_str).encode(charset)
        
        self._public_key = RSA.import_key(pub_key_pem)
        self._private_key = RSA.import_key(pri_key_pem)
        self._charset = charset
    
    def rsa_encrypt(self, plaintext: str) -> str:
        """
        RSA加密
        
        Args:
            plaintext: 明文
        
        Returns:
            base64编码的密文（URL-safe）
        """
        if self._has_rsa:
            encrypted = rsa.encrypt(plaintext.encode(), self.public_key)
            return base64.urlsafe_b64encode(encrypted).decode()
        else:
            cipher_rsa = PKCS1_v1_5.new(self._public_key)
            encrypted = cipher_rsa.encrypt(plaintext.encode(self._charset))
            return base64.urlsafe_b64encode(encrypted).decode(self._charset)
    
    def rsa_decrypt(self, ciphertext: str) -> str:
        """
        RSA解密
        
        Args:
            ciphertext: base64编码的密文
        
        Returns:
            明文
        """
        if self._has_rsa:
            encrypted = base64.b64decode(ciphertext)
            decrypted = rsa.decrypt(encrypted, self.private_key)
            return decrypted.decode()
        else:
            raise NotImplementedError("pycryptodome 模式下不支持解密")
    
    def sign_to_b64str(self, content: str, hash_method: str = 'MD5') -> str:
        """
        MD5withRSA签名（标准base64）
        
        Args:
            content: 待签名内容
            hash_method: 哈希方法，默认MD5
        
        Returns:
            base64编码的签名
        """
        if self._has_rsa:
            hash_func = getattr(rsa, hash_method.lower(), rsa.md5)
            signature = rsa.sign(content.encode(), self.private_key, hash_func)
            return base64.b64encode(signature).decode()
        else:
            signer = PKCS115_SigScheme(self._private_key)
            m = MD5.new(content.encode(self._charset))
            signature = signer.sign(m)
            return base64.b64encode(signature).decode(self._charset)
    
    def sign_with_urlsafe_b64str(self, content: str, hash_method: str = 'MD5') -> str:
        """
        MD5withRSA签名（URL-safe base64）
        
        Args:
            content: 待签名内容
            hash_method: 哈希方法，默认MD5
        
        Returns:
            URL-safe base64编码的签名
        """
        if self._has_rsa:
            hash_func = getattr(rsa, hash_method.lower(), rsa.md5)
            signature = rsa.sign(content.encode(), self.private_key, hash_func)
            return base64.urlsafe_b64encode(signature).decode()
        else:
            signer = PKCS115_SigScheme(self._private_key)
            m = MD5.new(content.encode(self._charset))
            signature = signer.sign(m)
            return base64.urlsafe_b64encode(signature).decode(self._charset)
    
    def verify_sign(self, content: str, signature: str, hash_method: str = 'MD5') -> bool:
        """
        验证签名
        
        Args:
            content: 原始内容
            signature: base64编码的签名
            hash_method: 哈希方法
        
        Returns:
            签名是否有效
        """
        if self._has_rsa:
            try:
                sign_bytes = base64.b64decode(signature)
                hash_func = getattr(rsa, hash_method.lower(), rsa.md5)
                rsa.verify(content.encode(), sign_bytes, self.public_key)
                return True
            except rsa.VerificationError:
                return False
        else:
            raise NotImplementedError("pycryptodome 模式下不支持验签")
    
    def gen_serialno_str(self, length: int = 19) -> str:
        """
        生成序列号（雪花算法简化版）
        
        Args:
            length: 序列号长度，默认19位
        
        Returns:
            序列号字符串
        """
        # 使用当前时间戳+随机数生成唯一ID
        time_part = str(int(time.time() * 10**6))
        random_part = str(random.randint(0, 999)).zfill(3)
        return (time_part + random_part)[:length].ljust(length, '0')
    
    def gen_unix_time_str(self, length: int = 10) -> str:
        """
        生成Unix时间戳字符串
        
        Args:
            length: 长度，默认10位（秒级）
        
        Returns:
            时间戳字符串
        """
        if length <= 10:
            return str(int(time.time()))[:length]
        else:
            return str(int(time.time() * 1000))[:length]
