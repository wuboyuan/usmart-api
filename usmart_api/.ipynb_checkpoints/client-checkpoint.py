# -*- coding: utf-8 -*-
"""
统一客户端模块

提供简洁的API调用方式,整合登录、交易解锁、行情查询等功能。
设计为标准库形式,所有配置通过参数传入,无需配置文件。

使用示例:
    >>> from usmart_api import USmartClient
    >>>
    >>> # 创建客户端(所有配置通过参数传入)
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
    >>>
    >>> # 查询持仓
    >>> holdings = client.get_holdings(exchange_type='0')

Author: wuboyuan
Email: wuboyuan92@126.com

Disclaimer:
    本库参考 uSMART 官方 API 文档开发，仅供学习交流使用。
    使用本库进行交易产生的任何风险和损失由使用者自行承担，作者不承担任何责任。
"""

import os
import json
from typing import Optional, List, Dict, Any, Callable

from usmart_api.core.request import RequestUtil
from usmart_api.quote_push import QuotePushClient


class USmartClient:
    """
    uSMART OpenAPI 统一客户端

    整合用户登录、交易解锁、行情查询等功能,所有配置通过参数传入。

    Attributes:
        token (str): 登录token
        trade_unlocked (bool): 交易是否已解锁
        _request (RequestUtil): 底层请求工具实例

    Example:
        >>> client = USmartClient(
        ...     X_Channel='your_channel',
        ...     phoneNumber='your_phone',
        ...     login_password='your_password',
        ...     trade_passwrod='your_trade_password',
        ...     public_key='your_public_key',
        ...     private_key='your_private_key'
        ... )
        >>> client.login()
        >>> holdings = client.get_holdings('0')
    """

    # 默认服务器地址
    DEFAULT_TRADE_HOST = 'https://open-jy.yxzq.com'
    DEFAULT_QUOTE_HOST = 'https://open-hz.yxzq.com:8443'
    DEFAULT_WS_HOST = 'wss://open-hz.yxzq.com:8443/wss/v1'
    DEFAULT_WS_ORIGIN = 'https://open-hz.yxzq.com'

    # 测试环境地址
    DEFAULT_UAT_QUOTE_HOST = 'https://open-hz-uat.yxzq.com'

    def __init__(self,
                 # 必填参数
                 X_Channel: str,
                 phoneNumber: str,
                 login_password: str,
                 trade_passwrod: str,
                 public_key: str,
                 private_key: str,
                 # 可选参数
                 areaCode: str = '86',
                 X_Lang: str = '1',
                 trade_host: Optional[str] = None,
                 quote_host: Optional[str] = None,
                 ws_host: Optional[str] = None,
                 ws_origin: Optional[str] = None):
        """
        初始化客户端

        Args:
            X_Channel: 渠道标识,由盈立分配(必填)
            phoneNumber: 手机号(必填)
            login_password: 登录密码(必填)
            trade_passwrod: 交易密码(必填)
            public_key: RSA公钥,由盈立分配(必填)
            private_key: RSA私钥,由盈立分配(必填)
            areaCode: 区号,默认'86'
            X_Lang: 语言设置,'1'-简体 '2'-繁体 '3'-英文,默认'1'
            trade_host: 交易接口服务器地址,默认生产环境
            quote_host: 行情接口服务器地址,默认生产环境
            ws_host: WebSocket服务器地址,默认生产环境
            ws_origin: WebSocket来源地址,默认生产环境
        """
        self.token: Optional[str] = None
        self.trade_unlocked: bool = False
        self.trade_password: str = trade_passwrod

        # 使用默认服务器地址或自定义地址
        self._trade_host = trade_host or self.DEFAULT_TRADE_HOST
        self._quote_host = quote_host or self.DEFAULT_QUOTE_HOST
        self._ws_host = ws_host or self.DEFAULT_WS_HOST
        self._ws_origin = ws_origin or self.DEFAULT_WS_ORIGIN

        # 初始化请求工具
        self._request = RequestUtil(
            trade_host=self._trade_host,
            quote_host=self._quote_host,
            X_Lang=X_Lang,
            X_Channel=X_Channel,
            areaCode=areaCode,
            phoneNumber=phoneNumber,
            login_password=login_password,
            trade_passwrod=trade_passwrod,
            public_key=public_key,
            private_key=private_key,
            ws_host=self._ws_host,
            ws_origin=self._ws_origin
        )

        # WebSocket行情推送客户端
        self._quote_push: Optional[QuotePushClient] = None

    @classmethod
    def from_config(cls, config_path: str, user_key: str = "default_user"):
        """
        从配置文件创建客户端(兼容旧版)

        Args:
            config_path: 配置文件路径
            user_key: 配置文件中的用户key

        Returns:
            USmartClient实例
        """
        with open(config_path, 'r') as f:
            config = json.load(f)

        user_config = config.get(user_key, config.get("default_user"))

        return cls(
            X_Channel=user_config["X-Channel"],
            phoneNumber=user_config["phoneNumber"],
            login_password=user_config["login_password"],
            trade_passwrod=user_config["trade_passwrod"],
            public_key=user_config["public_key"],
            private_key=user_config["private_key"],
            areaCode=user_config.get("areaCode", "86"),
            X_Lang=user_config.get("X-Lang", "1"),
            trade_host=config.get("trade_host"),
            quote_host=config.get("quote_host"),
            ws_host=config.get("ws_host"),
            ws_origin=config.get("ws_origin")
        )

    def login(self) -> Dict[str, Any]:
        """
        用户登录并自动解锁交易

        调用此方法后,客户端会自动:
        1. 使用手机号和密码登录获取token
        2. 使用交易密码解锁交易功能
        3. 后续接口调用无需再次登录或解锁

        Returns:
            dict: 登录结果
                - success (bool): 是否成功
                - token (str): 登录token
        """
        # 1. 登录获取token
        # 注意:原版API参数是 phoneNumber/password/areaCode
        params = {
            'phoneNumber': self._request.encryptUtil.rsa_encrypt(self._request.phoneNumber),
            'password': self._request.encryptUtil.rsa_encrypt(self._request.login_password),
            'areaCode': self._request.areaCode
        }

        result = self._request.post_with_sign_by_trade(
            '/user-server/open-api/login', params
        )

        # 支持字符串或整数类型的code
        code = result.get('code')
        if code in ('0', 0) and result.get('data'):
            self.token = result['data'].get('token')
            self._request.token = self.token

            # 2. 解锁交易
            self._trade_login()

            return {
                'success': True,
                'token': self.token,
                'trade_unlocked': self.trade_unlocked,
                'raw': result
            }
        else:
            return {
                'success': False,
                'error': result.get('msg', '登录失败'),
                'raw': result
            }

    def _trade_login(self) -> bool:
        """
        交易解锁

        Returns:
            bool: 是否解锁成功
        """
        params = {
            'password': self._request.encryptUtil.rsa_encrypt(self.trade_password)
        }

        result = self._request.post_with_sign_by_trade(
            '/user-server/open-api/trade-login', params
        )

        # 支持字符串或整数类型的code
        code = result.get('code')
        if code in ('0', 0):
            self.trade_unlocked = True
            return True
        else:
            print(f"交易解锁失败: code={code}, msg={result.get('msg')}")
        return False

    def get_trade_status(self) -> Dict[str, Any]:
        """
        获取交易解锁状态

        Returns:
            dict: 交易状态
        """
        result = self._request.post_with_sign_by_trade(
            '/user-server/open-api/get-trade-status', {}
        )
        return result

    # ============ 持仓和资产 ============

    def get_holdings(self, exchange_type: int = 0) -> Dict[str, Any]:
        """
        查询持仓

        Args:
            exchange_type: 交易类别(0-香港,5-美股, 67-A股, 100-查询所有), int32

        Returns:
            dict: 持仓列表
        """
        params = {'exchangeType': int(exchange_type)}
        return self._request.post_with_sign_by_trade(
            '/stock-order-server/open-api/stock-holding', params
        )

    def get_assets(self, exchange_type: str = '') -> Dict[str, Any]:
        """
        查询资产(旧接口)

        Args:
            exchange_type: 市场类型,可选

        Returns:
            dict: 资产信息
        """
        params = {}
        if exchange_type:
            params['exchangeType'] = exchange_type
        return self._request.post_with_sign_by_trade(
            '/stock-order-server/open-api/stock-asset', params
        )

    def query_asset(self, money_type: Optional[int] = None) -> Dict[str, Any]:
        """
        查询资产(新接口)

        Args:
            money_type: 币种类型 (0:人民币; 1:美元; 2:港币),可选, integer(int32)

        Returns:
            dict: 资产信息
        """
        params = {}
        if money_type is not None:
            params['moneyType'] = int(money_type)
        return self._request.post_with_sign_by_trade(
            '/asset-center-server/open-api/open-assetQuery/v1', params
        )

    # ============ 订单查询 ============

    def get_today_orders(self, exchange_type: int = 0,
                         page_num: int = 1,
                         page_size: int = 20,
                         stock_code: str = '') -> Dict[str, Any]:
        """
        查询今日订单

        Args:
            exchange_type: 交易类别(0-香港,5-美股, 67-A股, 100-查询所有), int32
            page_num: 当前页,1开始,默认值1, int32
            page_size: 每页结果数,默认值10, int32
            stock_code: 证券代码,可选, string

        Returns:
            dict: 订单列表
        """
        params = {
            'exchangeType': int(exchange_type),
            'pageNum': int(page_num),
            'pageSize': int(page_size),
            'stockCode': stock_code
        }
        return self._request.post_with_sign_by_trade(
            '/stock-order-server/open-api/today-entrust', params
        )

    def get_his_orders(self, exchange_type: int = 0,
                       date_flag: str = '7',
                       start_date: str = '',
                       end_date: str = '',
                       page_num: int = 1,
                       page_size: int = 10,
                       stock_code: str = '') -> Dict[str, Any]:
        """
        查询历史订单

        Args:
            exchange_type: 交易类别(0-香港,5-美股, 67-A股, 100-查询所有), int32
            date_flag: 1:一周,2:一个月,3:三个月,4:近一年,5:今年,6:自选时间,7:查询全部, string
            start_date: 开始日期 (yyyy-MM-dd), string
            end_date: 结束日期 (yyyy-MM-dd), string
            page_num: 当前页,1开始,默认值1, int32
            page_size: 每页结果数,默认值10, int32
            stock_code: 证券代码,可选, string

        Returns:
            dict: 订单列表
        """
        params = {
            'exchangeType': int(exchange_type),
            'dateFlag': date_flag,
            'entrustBeginDate': start_date,
            'entrustEndDate': end_date,
            'pageNum': int(page_num),
            'pageSize': int(page_size),
            'stockCode': stock_code
        }

        return self._request.post_with_sign_by_trade(
            '/stock-order-server/open-api/his-entrust', params
        )

    def get_order_detail(self, serial_no: Optional[str] = None,
                         entrust_id: Optional[str] = None) -> Dict[str, Any]:
        """
        查询订单明细

        Args:
            serial_no: 订单流水号
            entrust_id: 委托ID

        Returns:
            dict: 订单明细
        """
        params = {}
        if serial_no:
            params['serialNo'] = serial_no
        if entrust_id:
            params['entrustId'] = entrust_id

        return self._request.post_with_sign_by_trade(
            '/stock-order-server/open-api/order-detail', params
        )

    def get_stock_records(self, exchange_type: str = '0',
                          start_date: str = '',
                          end_date: str = '',
                          page_num: str = '0',
                          page_size: str = '20',
                          stock_code: str = '') -> Dict[str, Any]:
        """
        查询成交流水

        Args:
            exchange_type: 市场类型
            start_date: 开始日期 (yyyy-MM-dd)
            end_date: 结束日期 (yyyy-MM-dd)
            page_num: 页码,从0开始
            page_size: 每页数量
            stock_code: 股票代码,可选

        Returns:
            dict: 成交记录
        """
        params = {
            'exchangeType': exchange_type,
            'startDate': start_date,
            'endDate': end_date,
            'pageNum': page_num,
            'pageSize': page_size,
            'stockCode': stock_code
        }

        return self._request.post_with_sign_by_trade(
            '/stock-order-server/open-api/stock-record', params
        )

    # ============ 交易接口 ============

    def buy(self, stock_code: str, price: str, quantity: str,
            exchange_type: int = 0, entrust_prop: str = '0',
            force_entrust_flag: bool = False,
            force_entrust: bool = None) -> Dict[str, Any]:
        """
        买入股票

        Args:
            stock_code: 股票代码,如'00700', string
            price: 委托价格, number
            quantity: 委托数量, number
            exchange_type: 交易类别(0-香港,5-美股, 67-A股), int32
            entrust_prop: 委托属性,'0'-限价 'e'-增强限价单 'w'-市价, string
            force_entrust_flag: 是否强制委托, boolean

        Returns:
            dict: 委托结果
        """
        params = {
            'serialNo': self._request.encryptUtil.gen_serialno_str(),
            'stockCode': stock_code,
            'entrustPrice': float(price),
            'entrustAmount': int(quantity),
            'exchangeType': int(exchange_type),
            'entrustProp': entrust_prop,
            'entrustType': 0,  # 0-买入, int32
            'password': self._request.encryptUtil.rsa_encrypt(self.trade_password),
            'forceEntrustFlag': force_entrust if force_entrust is not None else force_entrust_flag
        }
        return self._request.post_with_sign_by_trade(
            '/stock-order-server/open-api/entrust-order', params
        )

    def sell(self, stock_code: str, price: str, quantity: str,
             exchange_type: int = 0, entrust_prop: str = '0',
             force_entrust_flag: bool = False,
             force_entrust: bool = None) -> Dict[str, Any]:
        """
        卖出股票

        Args:
            stock_code: 股票代码, string
            price: 委托价格, number
            quantity: 委托数量, number
            exchange_type: 交易类别(0-香港,5-美股, 67-A股), int32
            entrust_prop: 委托属性,'0'-限价 'e'-增强限价单 'w'-市价, string
            force_entrust_flag: 是否强制委托, boolean

        Returns:
            dict: 委托结果
        """
        params = {
            'serialNo': self._request.encryptUtil.gen_serialno_str(),
            'stockCode': stock_code,
            'entrustPrice': float(price),
            'entrustAmount': int(quantity),
            'exchangeType': int(exchange_type),
            'entrustProp': entrust_prop,
            'entrustType': 1,  # 1-卖出, int32
            'password': self._request.encryptUtil.rsa_encrypt(self.trade_password),
            'forceEntrustFlag': force_entrust if force_entrust is not None else force_entrust_flag
        }
        return self._request.post_with_sign_by_trade(
            '/stock-order-server/open-api/entrust-order', params
        )

    def cancel_order(self, entrust_id: str, force_entrust_flag: bool = False, force_entrust: bool = None) -> Dict[str, Any]:
        """
        撤单

        Args:
            entrust_id: 委托ID
            force_entrust_flag: 是否强制委托

        Returns:
            dict: 撤单结果
        """
        headers = {
            'Authorization': self.token,
            'X-Request-Id': self._request.encryptUtil.gen_unix_time_str(16)
        }
        params = {
            'actionType': 0,  # 0-撤单 (int32)
            'entrustAmount': 0,  # 撤单时传0 (number)
            'entrustId': int(entrust_id),  # int64
            'entrustPrice': 0,   # 撤单时传0 (number)
            'forceEntrustFlag': force_entrust if force_entrust is not None else force_entrust_flag,
            'password': self._request.encryptUtil.rsa_encrypt(self.trade_password)
        }


        return self._request.post_with_sign_by_trade(
            '/stock-order-server/open-api/modify-order', params, headers
        )

    def modify_order(self, entrust_id: str, new_price: str,
                     new_quantity: str, force_entrust_flag: bool = False,
                     force_entrust: bool = None) -> Dict[str, Any]:
        """
        改单

        Args:
            entrust_id: 委托ID
            new_price: 新价格
            new_quantity: 新数量
            force_entrust_flag: 是否强制委托

        Returns:
            dict: 改单结果
        """
        headers = {
            'Authorization': self.token,
            'X-Request-Id': self._request.encryptUtil.gen_unix_time_str(16)
        }
        params = {
            'actionType': 1,  # 1-改单 (int32)
            'entrustAmount': int(new_quantity),  # number
            'entrustId': int(entrust_id),  # int64
            'entrustPrice': float(new_price),   # number
            'forceEntrustFlag': force_entrust if force_entrust is not None else force_entrust_flag,
            'password': self._request.encryptUtil.rsa_encrypt(self.trade_password)
        }
        return self._request.post_with_sign_by_trade(
            '/stock-order-server/open-api/modify-order', params, headers
        )

    def get_max_quantity(self, stock_code: str, price: str,
                         exchange_type: int = 0, entrust_prop: str = '0') -> Dict[str, Any]:
        """
        查询最大可买/卖数量

        Args:
            stock_code: 股票代码, string
            price: 委托价格, number
            exchange_type: 交易类别(0-香港,5-美股, 67-A股), int32
            entrust_prop: 委托属性,'0'-限价 'e'-增强限价单 'w'-市价, string

        Returns:
            dict: 最大数量信息
        """
        params = {
            'stockCode': stock_code,
            'entrustPrice': float(price),
            'exchangeType': int(exchange_type),
            'entrustProp': entrust_prop
        }
        return self._request.post_with_sign_by_trade(
            '/stock-order-server/open-api/trade-quantity', params
        )

    # ============ 行情接口 ============

    def get_quote(self, secu_ids: List[str]) -> Dict[str, Any]:
        """
        查询实时行情

        Args:
            secu_ids: 股票ID列表,如['hk00700', 'usAAPL']

        Returns:
            dict: 行情数据
        """
        params = {'secuIds': secu_ids}
        return self._request.post_with_sign_by_quote(
            '/quotes-openservice/api/v1/realtime', params
        )

    def get_kline(self, secu_id: str, kline_type: int = 5,
                  count: int = 100, start: int = 0, right: int = 0) -> Dict[str, Any]:
        """
        查询K线数据

        Args:
            secu_id: 股票ID,如'hk00700'
            kline_type: K线类型
                0 - 1分钟
                1 - 5分钟
                2 - 15分钟
                3 - 30分钟
                4 - 60分钟
                5 - 日K
                6 - 周K
                7 - 月K
                8 - 季K
                9 - 年K
            count: 返回条数
            start: 起始时间戳,格式如 20240509160000000
            right: 复权类型,0-不复权,1-前复权,2-后复权

        Returns:
            dict: K线数据
        """
        params = {
            'secuId': secu_id,
            'type': kline_type,
            'start': start,
            'right': right,
            'count': count
        }
        return self._request.post_with_sign_by_quote(
            '/quotes-openservice/api/v1/kline', params
        )

    def get_orderbook(self, secu_id: str) -> Dict[str, Any]:
        """
        查询买卖盘

        Args:
            secu_id: 股票ID

        Returns:
            dict: 买卖盘数据
        """
        params = {'secuId': secu_id}
        return self._request.post_with_sign_by_quote(
            '/quotes-openservice/api/v1/orderbook', params
        )

    def get_tick(self, secu_id: str, trade_time: int = 0,
                 seq: int = 0, count: int = 20, sort_direction: int = 2) -> Dict[str, Any]:
        """
        查询逐笔成交

        Args:
            secu_id: 股票ID,如'hk00700'
            trade_time: 交易时间,格式如20201221160000000
            seq: 起始序号
            count: 返回条数
            sort_direction: 排序方向,1-升序,2-降序,默认2

        Returns:
            dict: 逐笔成交数据
        """
        params = {
            'secuId': secu_id,
            'tradeTime': trade_time,
            'seq': seq,
            'count': count,
            'sortDirection': sort_direction
        }
        return self._request.post_with_sign_by_quote(
            '/quotes-openservice/api/v1/tick', params
        )

    def get_timeline(self, secu_id: str, timeline_type: int = 0) -> Dict[str, Any]:
        """
        查询分时数据

        Args:
            secu_id: 股票ID,如'hk00700'
            timeline_type: 分时类型,0-当日分时,1-五日分时

        Returns:
            dict: 分时数据
        """
        params = {
            'secuId': secu_id,
            'type': timeline_type
        }
        return self._request.post_with_sign_by_quote(
            '/quotes-openservice/api/v1/timeline', params
        )

    def get_market_state(self, market: str = 'hk') -> Dict[str, Any]:
        """
        查询市场状态

        Args:
            market: 市场代码,如'hk'、'us'

        Returns:
            dict: 市场状态
        """
        params = {'market': market}
        return self._request.post_with_sign_by_quote(
            '/quotes-openservice/api/v1/marketstate', params
        )

    def get_basic_info(self, market: str = 'hk', page_num: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """
        查询股票基础信息

        Args:
            market: 市场代码,如'hk'、'us'
            page_num: 页码,默认1
            page_size: 每页数量,默认50

        Returns:
            dict: 基础信息列表
        """
        params = {
            'market': market,
            'pageNum': page_num,
            'pageSize': page_size
        }
        return self._request.post_with_sign_by_quote(
            '/quotes-openservice/api/v1/basicinfo', params
        )

    # ============ WebSocket行情推送 ============

    def start_quote_push(self, handler: Optional[Callable[[str, str], None]] = None) -> 'USmartClient':
        """
        启动WebSocket行情推送

        启动后可以通过 subscribe_quote() 订阅实时行情。

        Args:
            handler: 数据接收回调函数，接收(topic, data)两个参数。
                    如果为None，使用默认打印处理器。

        Returns:
            self: 支持链式调用

        Example:
            >>> def my_handler(topic, data):
            ...     print(f"收到 {topic}: {data}")
            >>>
            >>> client.start_quote_push(my_handler)
            >>> client.subscribe_quote(["rt.us.TSLA", "ob.us.TSLA"])
        """
        if not self.token:
            raise RuntimeError("请先调用 login() 获取token")

        if self._quote_push is not None:
            print("[QuotePush] 已经启动")
            return self

        self._quote_push = QuotePushClient(
            token=self.token,
            ws_host=self._ws_host,
            ws_origin=self._ws_origin,
            handler=handler
        )
        self._quote_push.start()
        return self

    def stop_quote_push(self) -> 'USmartClient':
        """
        停止WebSocket行情推送

        Returns:
            self: 支持链式调用
        """
        if self._quote_push:
            self._quote_push.stop()
            self._quote_push = None
        return self

    def subscribe_quote(self, topics: List[str]) -> 'USmartClient':
        """
        订阅行情主题

        需要先调用 start_quote_push() 启动推送服务。

        Args:
            topics: 主题列表，格式为["类型.市场.代码", ...]
                - 类型: rt(实时行情), ob(买卖盘), tk(逐笔)
                - 市场: hk(港股), us(美股), sh(上海), sz(深圳)

        Returns:
            self: 支持链式调用

        Example:
            >>> client.subscribe_quote(["rt.us.TSLA", "ob.us.TSLA"])
            >>> # 订阅港股腾讯
            >>> client.subscribe_quote(["rt.hk.00700", "ob.hk.00700"])
        """
        if not self._quote_push:
            raise RuntimeError("请先调用 start_quote_push() 启动推送服务")

        self._quote_push.subscribe(topics)
        return self

    def unsubscribe_quote(self, topics: List[str]) -> 'USmartClient':
        """
        取消订阅行情主题

        Args:
            topics: 要取消订阅的主题列表

        Returns:
            self: 支持链式调用
        """
        if self._quote_push:
            self._quote_push.unsubscribe(topics)
        return self

    def set_quote_handler(self, handler: Callable[[str, str], None]) -> 'USmartClient':
        """
        设置行情数据接收回调函数

        Args:
            handler: 回调函数，接收(topic, data)两个参数

        Returns:
            self: 支持链式调用
        """
        if not self._quote_push:
            raise RuntimeError("请先调用 start_quote_push() 启动推送服务")

        self._quote_push.set_handler(handler)
        return self
