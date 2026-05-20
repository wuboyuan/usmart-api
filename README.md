# uSMART OpenAPI Python SDK

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

盈立智投 OpenAPI Python 封装库，提供简洁的API调用方式，支持股票交易、行情查询和实时数据推送。

> **作者**: wuboyuan  
> **联系方式**: wuboyuan92@126.com  
> **免责声明**: 本库参考 [uSMART 官方 API 文档](https://api-doc.usmart8.com) 开发，仅供学习交流使用。使用本库进行交易产生的任何风险和损失由使用者自行承担，作者不承担任何责任。

## Features

- ✅ **用户认证** - 登录、交易解锁
- ✅ **持仓资产** - 查询持仓、资产信息
- ✅ **订单管理** - 下单、撤单、改单、查询
- ✅ **行情数据** - 实时行情、K线、买卖盘、逐笔成交
- ✅ **WebSocket推送** - 实时行情推送（实时行情、买卖盘、逐笔成交）
- ✅ **标准库设计** - 所有配置通过参数传入，无需配置文件

## Installation

```bash
pip install usmart-api
```

Or install from source:

```bash
git clone https://github.com/usmart/usmart-api-python.git
cd usmart-api-python
pip install -e .
```

## Quick Start

### 1. 基础用法

```python
from usmart_api import USmartClient

# 创建客户端
client = USmartClient(
    X_Channel='your_channel',
    phoneNumber='your_phone',
    login_password='your_password',
    trade_passwrod='your_trade_password',
    public_key='your_public_key',
    private_key='your_private_key'
)

# 登录（自动获取token并解锁交易）
result = client.login()
if result['success']:
    print("登录成功！")
    
    # 查询持仓
    holdings = client.get_holdings(exchange_type='0')  # 0=港股
    print(holdings)
    
    # 查询资产
    assets = client.query_asset(money_type=2)  # 2=港币
    print(assets)
else:
    print(f"登录失败: {result.get('error')}")
```

### 2. 交易操作

```python
# 买入股票
result = client.buy(
    stock_code='00700',
    price='400.0',
    quantity='100',
    exchange_type=0  # 港股
)

# 卖出股票
result = client.sell(
    stock_code='00700',
    price='410.0',
    quantity='100',
    exchange_type=0
)

# 撤单
result = client.cancel_order(entrust_id='123456')

# 查询今日订单
orders = client.get_today_orders(exchange_type='0')
```

### 3. 行情查询

```python
# 实时行情
quote = client.get_quote(['hk00700', 'usTSLA'])

# K线数据
kline = client.get_kline(
    secu_id='hk00700',
    kline_type=5,  # 日K
    count=100
)

# 买卖盘
orderbook = client.get_orderbook('hk00700')

# 逐笔成交
ticks = client.get_tick('hk00700', count=20)
```

### 4. WebSocket实时行情推送

```python
import time

# 定义数据回调函数
def my_handler(topic: str, data: str):
    """
    处理收到的行情数据
    
    Args:
        topic: 主题，如 "rt.us.TSLA"
        data: JSON格式的行情数据
    """
    import json
    data_obj = json.loads(data)
    
    if topic.startswith("rt."):
        # 实时行情
        price = data_obj.get('latestPrice')
        print(f"[实时行情] {topic}: 最新价={price}")
    elif topic.startswith("ob."):
        # 买卖盘
        bids = data_obj.get('data', [])
        if bids:
            print(f"[买卖盘] {topic}: 买一={bids[0].get('bidPrice')}, 卖一={bids[0].get('askPrice')}")

# 启动WebSocket推送
client.start_quote_push(handler=my_handler)
time.sleep(3)  # 等待连接建立

# 订阅行情
client.subscribe_quote(["rt.us.TSLA", "ob.us.TSLA"])

# 保持运行...
time.sleep(60)

# 取消订阅并停止
client.unsubscribe_quote(["rt.us.TSLA", "ob.us.TSLA"])
client.stop_quote_push()
```

## API Reference

### USmartClient

主客户端类，整合所有功能。

#### 初始化参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| X_Channel | str | ✅ | 渠道标识 |
| phoneNumber | str | ✅ | 手机号 |
| login_password | str | ✅ | 登录密码 |
| trade_passwrod | str | ✅ | 交易密码 |
| public_key | str | ✅ | RSA公钥 |
| private_key | str | ✅ | RSA私钥 |
| areaCode | str | ❌ | 区号，默认'86' |
| X_Lang | str | ❌ | 语言，默认'1'（简体） |

#### 主要方法

| 方法 | 说明 |
|------|------|
| `login()` | 登录并解锁交易 |
| `get_holdings()` | 查询持仓 |
| `query_asset()` | 查询资产 |
| `buy()` / `sell()` | 买入/卖出 |
| `cancel_order()` | 撤单 |
| `get_quote()` | 查询实时行情 |
| `get_kline()` | 查询K线 |
| `start_quote_push()` | 启动WebSocket推送 |
| `subscribe_quote()` | 订阅行情主题 |
| `stop_quote_push()` | 停止推送 |

### 主题格式

WebSocket订阅主题格式：`<类型>.<市场>.<代码>`

| 类型 | 说明 |
|------|------|
| rt | 实时行情 (realtime) |
| ob | 买卖盘 (orderbook) |
| tk | 逐笔成交 (tick) |

| 市场 | 说明 |
|------|------|
| hk | 港股 |
| us | 美股 |
| sh | 上海 |
| sz | 深圳 |

示例：
- `rt.hk.00700` - 腾讯实时行情
- `ob.us.TSLA` - 特斯拉买卖盘
- `tk.hk.00700` - 腾讯逐笔成交

## Examples

See `examples/` directory for more usage examples.

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference with real-world examples.

## 作者信息

- **作者**: wuboyuan
- **邮箱**: wuboyuan92@126.com
- **GitHub**: https://github.com/wuboyuan

## 免责声明

本库参考 [uSMART 官方 API 文档](https://api-doc.usmart8.com) 开发，仅供学习交流使用。

**使用本库进行交易产生的任何风险和损失由使用者自行承担，作者不承担任何责任。**

- 投资有风险，入市需谨慎
- 请确保您了解所使用接口的风险
- 建议在实盘交易前充分测试

## License

MIT License - see LICENSE file for details.
