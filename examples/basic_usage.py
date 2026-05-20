# -*- coding: utf-8 -*-
"""
基础使用示例
"""

from usmart_api import USmartClient


def basic_usage():
    """基础用法示例"""
    
    # 创建客户端
    client = USmartClient(
        X_Channel='your_channel',
        phoneNumber='your_phone',
        login_password='your_password',
        trade_passwrod='your_trade_password',
        public_key='your_public_key',
        private_key='your_private_key'
    )
    
    # 登录
    result = client.login()
    if not result['success']:
        print(f"登录失败: {result.get('error')}")
        return
    
    print("登录成功！")
    
    # 查询持仓
    holdings = client.get_holdings(exchange_type='0')  # 0=港股
    print(f"持仓: {holdings}")
    
    # 查询资产
    assets = client.query_asset(money_type=2)  # 2=港币
    print(f"资产: {assets}")
    
    # 查询实时行情
    quote = client.get_quote(['hk00700'])
    print(f"行情: {quote}")


def trading_example():
    """交易示例"""
    
    client = USmartClient(
        X_Channel='your_channel',
        phoneNumber='your_phone',
        login_password='your_password',
        trade_passwrod='your_trade_password',
        public_key='your_public_key',
        private_key='your_private_key'
    )
    
    client.login()
    
    # 买入
    result = client.buy(
        stock_code='00700',
        price='400.0',
        quantity='100',
        exchange_type=0
    )
    print(f"买入结果: {result}")
    
    # 查询今日订单
    orders = client.get_today_orders(exchange_type='0')
    print(f"今日订单: {orders}")


def quote_example():
    """行情查询示例"""
    
    client = USmartClient(
        X_Channel='your_channel',
        phoneNumber='your_phone',
        login_password='your_password',
        trade_passwrod='your_trade_password',
        public_key='your_public_key',
        private_key='your_private_key'
    )
    
    client.login()
    
    # 实时行情
    quote = client.get_quote(['hk00700', 'usTSLA'])
    print(f"实时行情: {quote}")
    
    # K线
    kline = client.get_kline('hk00700', kline_type=5, count=10)
    print(f"K线: {kline}")
    
    # 买卖盘
    orderbook = client.get_orderbook('hk00700')
    print(f"买卖盘: {orderbook}")
    
    # 逐笔成交
    ticks = client.get_tick('hk00700', count=10)
    print(f"逐笔: {ticks}")


if __name__ == '__main__':
    # basic_usage()
    # trading_example()
    # quote_example()
    pass
