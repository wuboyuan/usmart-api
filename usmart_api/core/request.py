# -*- coding: utf-8 -*-
"""
核心请求工具模块

提供HTTP请求封装、签名生成、加密等功能。
兼容原版 openapi-demo-py 的 RequestUtil
"""

import json
import os
import requests
from typing import Dict, Any, Optional

from usmart_api.core.crypto import EncryptUtil


class RequestUtil:
    """
    HTTP请求工具类
    
    封装uSMART OpenAPI的HTTP请求，自动处理签名和认证。
    
    Attributes:
        token (str): 登录后获取的认证token
        trade_host (str): 交易接口服务器地址
        quote_host (str): 行情接口服务器地址
        ws_host (str): WebSocket服务器地址
        ws_origin (str): WebSocket来源地址
        X_Lang (str): 语言设置
        X_Channel (str): 渠道标识
        areaCode (str): 区号
        phoneNumber (str): 手机号
        login_password (str): 登录密码
        trade_passwrod (str): 交易密码
        encryptUtil (EncryptUtil): 加密工具实例
    """
    
    def __init__(self, trade_host: str, quote_host: str, 
                 X_Lang: str, X_Channel: str, areaCode: str,
                 phoneNumber: str, login_password: str, trade_passwrod: str,
                 public_key: str, private_key: str,
                 ws_host: Optional[str] = None, ws_origin: Optional[str] = None):
        """
        初始化RequestUtil实例
        
        Args:
            trade_host: 交易接口服务器地址
            quote_host: 行情接口服务器地址
            X_Lang: 语言设置 '1'-简体 '2'-繁体 '3'-英文
            X_Channel: 渠道标识
            areaCode: 区号
            phoneNumber: 手机号
            login_password: 登录密码
            trade_passwrod: 交易密码
            public_key: RSA公钥
            private_key: RSA私钥
            ws_host: WebSocket服务器地址
            ws_origin: WebSocket来源地址
        """
        self.token: Optional[str] = None
        self.trade_host = trade_host
        self.quote_host = quote_host
        self.ws_host = ws_host
        self.ws_origin = ws_origin
        self.X_Lang = X_Lang
        self.X_Channel = X_Channel
        self.areaCode = areaCode
        self.phoneNumber = phoneNumber
        self.login_password = login_password
        self.trade_passwrod = trade_passwrod
        self.encryptUtil = EncryptUtil(public_key, private_key)
    
    @classmethod
    def from_config(cls, config_path: Optional[str] = None, user_key: str = "default_user"):
        """
        从配置文件创建RequestUtil实例（兼容原版）
        
        Args:
            config_path: 配置文件路径，默认从 API_DEMO_HOMEPATH 环境变量读取
            user_key: 配置文件中的用户key
        
        Returns:
            RequestUtil实例
        """
        if config_path is None:
            config_path = os.path.join(
                os.environ.get('API_DEMO_HOMEPATH', ''), 
                'conf', 'config.json'
            )
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        user_config = config.get(user_key, config.get("default_user"))
        
        return cls(
            trade_host=config["trade_host"],
            quote_host=config["quote_host"],
            X_Lang=user_config["X-Lang"],
            X_Channel=user_config["X-Channel"],
            areaCode=user_config["areaCode"],
            phoneNumber=user_config["phoneNumber"],
            login_password=user_config["login_password"],
            trade_passwrod=user_config["trade_passwrod"],
            public_key=user_config["public_key"],
            private_key=user_config["private_key"],
            ws_host=config.get("ws_host"),
            ws_origin=config.get("ws_origin")
        )
    
    def post_with_sign_by_trade(self, api: str, params: Dict[str, Any], 
                                 headers: Optional[Dict[str, str]] = None,
                                 timeout: int = 30) -> Dict[str, Any]:
        """
        交易接口请求
        
        发送交易相关的HTTP POST请求，自动添加签名和认证头。
        签名方式：对body进行MD5withRSA签名，再base64编码。
        
        Args:
            api: API接口路径，如'/user-server/open-api/login'
            params: 请求参数
            headers: 额外的请求头，可选
            timeout: 超时时间，默认30秒
        
        Returns:
            API响应的JSON数据
        """
        url = f"{self.trade_host}{api}"
        body = json.dumps(params)
        
        # 构建请求头（与原版一致）
        # 如果传入了 headers，使用传入的 X-Request-Id，否则生成新的
        request_id = headers.get('X-Request-Id') if headers else None
        if not request_id:
            request_id = self.encryptUtil.gen_serialno_str()
        
        # 生成签名（使用最终的 request_id）
        sign = self.encryptUtil.sign_to_b64str(body)
        
        request_headers = {
            'Content-type': 'application/json; charset=utf-8',
            'X-Lang': self.X_Lang,
            'X-Channel': self.X_Channel,
            'X-Request-Id': request_id,
            'X-Sign': sign,
            'Authorization': self.token  # 直接传token，不需要Bearer前缀
        }
        
        # 合并额外请求头（但不覆盖 X-Request-Id 和 X-Sign）
        if headers:
            for key, value in headers.items():
                if key not in ('X-Request-Id', 'X-Sign'):
                    request_headers[key] = value
        
        response = requests.post(url, data=body, headers=request_headers, timeout=timeout)
        return response.json()
    
    def post_with_sign_by_quote(self, api: str, params: Dict[str, Any],
                                 headers: Optional[Dict[str, str]] = None,
                                 timeout: int = 30) -> Dict[str, Any]:
        """
        行情接口请求
        
        发送行情相关的HTTP POST请求，自动添加签名和认证头。
        签名方式：将Authorization、X-Channel、X-Lang、X-Request-Id、body按顺序拼接，
        然后进行MD5withRSA签名，再URL-safe base64编码。
        
        Args:
            api: API接口路径
            params: 请求参数
            headers: 额外的请求头，可选
            timeout: 超时时间，默认30秒
        
        Returns:
            API响应的JSON数据
        """
        url = f"{self.quote_host}{api}"
        body = json.dumps(params)
        
        # 生成请求ID和时间戳（与原版一致）
        request_id = self.encryptUtil.gen_serialno_str()
        x_time = self.encryptUtil.gen_unix_time_str(10)
        
        # 行情接口签名：拼接特定字段（与原版一致）
        # 格式: Authorization + X-Channel + X-Lang + X-Request-Id + X-Time + body
        auth = self.token if self.token else ''
        row_content = auth + self.X_Channel + self.X_Lang + request_id + x_time + body
        
        sign = self.encryptUtil.sign_with_urlsafe_b64str(row_content)
        
        # 构建请求头（与原版一致）
        # 确保token不为None
        auth_token = self.token if self.token else ""
        request_headers = {
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': auth_token,
            'X-Channel': self.X_Channel,
            'X-Lang': self.X_Lang,
            'X-Request-Id': request_id,
            'X-Time': x_time,
            'X-Sign': sign
        }
        
        # 合并额外请求头
        if headers:
            request_headers.update(headers)
        
        response = requests.post(url, data=body, headers=request_headers, timeout=timeout)
        
        # 检查HTTP状态码
        if response.status_code != 200:
            return {'code': response.status_code, 'msg': f'HTTP错误: {response.status_code}', 'raw': response.text}
        
        try:
            return response.json()
        except Exception as e:
            return {'code': -1, 'msg': f'JSON解析错误: {str(e)}', 'raw': response.text}
    
    def get(self, api: str, params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            host_type: str = 'trade',
            timeout: int = 30) -> Dict[str, Any]:
        """
        GET请求
        
        Args:
            api: API接口路径
            params: URL参数
            headers: 额外的请求头
            host_type: 'trade' 或 'quote'
            timeout: 超时时间
        
        Returns:
            API响应的JSON数据
        """
        host = self.trade_host if host_type == 'trade' else self.quote_host
        url = f"{host}{api}"
        
        # 确保token不为None
        auth_token = self.token if self.token else ""
        request_headers = {
            'Content-type': 'application/json; charset=utf-8',
            'X-Lang': self.X_Lang,
            'X-Channel': self.X_Channel,
            'X-Request-Id': self.encryptUtil.gen_serialno_str(),
            'Authorization': auth_token
        }
        
        if headers:
            request_headers.update(headers)
        
        response = requests.get(url, params=params, headers=request_headers, timeout=timeout)
        return response.json()
