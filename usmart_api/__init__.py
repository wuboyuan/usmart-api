# -*- coding: utf-8 -*-
"""
uSMART OpenAPI Python SDK

盈立智投 OpenAPI Python 封装库，标准库形式，所有配置通过参数传入。

Features:
    - 用户登录和交易解锁
    - 持仓和资产查询
    - 订单管理（下单、撤单、改单）
    - 行情查询（实时行情、K线、买卖盘等）
    - WebSocket实时行情推送

Quick Start:
    >>> from usmart_api import USmartClient
    >>>
    >>> client = USmartClient(
    ...     X_Channel='your_channel',
    ...     phoneNumber='your_phone',
    ...     login_password='your_password',
    ...     trade_passwrod='your_trade_password',
    ...     public_key='your_public_key',
    ...     private_key='your_private_key'
    ... )
    >>>
    >>> client.login()
    >>> holdings = client.get_holdings(exchange_type='0')

Author: wuboyuan
Email: wuboyuan92@126.com

Disclaimer:
    本库参考 uSMART 官方 API 文档开发，仅供学习交流使用。
    使用本库进行交易产生的任何风险和损失由使用者自行承担，作者不承担任何责任。
"""

from usmart_api.client import USmartClient
from usmart_api.quote_push import QuotePushClient
from usmart_api.core.request import RequestUtil
from usmart_api.core.crypto import EncryptUtil

__version__ = '2.0.2'
__author__ = 'wuboyuan'
__email__ = 'wuboyuan92@126.com'
__all__ = [
    'USmartClient',
    'QuotePushClient',
    'RequestUtil',
    'EncryptUtil',
]
