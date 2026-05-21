# uSMART OpenAPI Python SDK 示例教程

> 本教程结合官方 API 文档 (https://api-doc.usmart8.com) 和实际使用案例编写

**作者**: wuboyuan  
**联系方式**: wuboyuan92@126.com

---

## ⚠️ 免责声明

**本库参考 [uSMART 官方 API 文档](https://api-doc.usmart8.com) 开发，仅供学习交流使用。**

- 使用本库进行交易产生的任何风险和损失由使用者自行承担，作者不承担任何责任
- 投资有风险，入市需谨慎
- 请确保您了解所使用接口的风险
- 建议在实盘交易前充分测试

---

## 目录

1. [快速开始](#快速开始)
2. [用户认证](#用户认证)
3. [持仓与资产](#持仓与资产)
4. [交易操作](#交易操作)
5. [订单查询](#订单查询)
6. [行情数据](#行情数据)
7. [WebSocket实时推送](#websocket实时推送)
8. [实战案例](#实战案例)

---

## 快速开始

### 安装

```bash
pip install usmart-api
```

### 初始化客户端

```python
from usmart_api import USmartClient

client = USmartClient(
    X_Channel='your_channel',           # 渠道标识，由盈立分配
    phoneNumber='your_phone',           # 手机号
    login_password='your_password',     # 登录密码
    trade_passwrod='your_password',     # 交易密码
    public_key='your_public_key',       # RSA公钥
    private_key='your_private_key'      # RSA私钥
)
```

---

## 用户认证

### 1. 登录

**官方接口**: `POST /user-server/open-api/login`

**功能**: 使用手机号/邮箱+密码登录，获取 token 并自动解锁交易。

```python
result = client.login()
print(result)
```

**输出示例**:
```python
{
    'success': True,
    'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
    'trade_unlocked': True,
    'raw': {
        'code': 0,
        'data': {
            'areaCode': '86',
            'expiration': 1781840621247,        # token过期时间
            'invitationCode': 'xxxxx',
            'nickname': '138****1234',
            'openedAccount': True,               # 是否已开户
            'phoneNumber': '13812345678',
            'token': 'eyJ0eXAiOiJKV1Qi...',
            'tradePassword': True,               # 是否设置交易密码
            'uuid': '1234567890123456789'
        },
        'msg': '成功'
    }
}
```

**注意事项**:
- 登录成功后，token 会自动保存到 client 中
- 交易会自动解锁，后续接口调用无需再次登录
- token 有过期时间，过期后需要重新登录

---

## 持仓与资产

### 2. 查询持仓

**官方接口**: `POST /stock-order-server/open-api/stock-holding`

**功能**: 查询指定市场的持仓股票列表。

```python
# 查询美股持仓 (exchange_type='5')
result = client.get_holdings(exchange_type='5')
print(result)
```

**入参说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| exchange_type | str | ✅ | 交易类别：'0'=港股, '5'=美股, '67'=A股, '100'=所有 |

**输出示例**:
```python
{
    'code': 0,
    'msg': '操作成功',
    'data': [
        {
            'exchangeType': 5,                   # 市场类型
            'stockCode': 'ZTG',                  # 股票代码
            'stockName': 'Zenta Group Co. Ltd.', # 股票名称
            'currentAmount': '5225.000000',      # 当前持仓数量
            'oddAmount': '0.0000',               # 零股数量
            'lastPrice': '2.770000',             # 最新价格
            'costPriceAccurate': '2.100000000',  # 成本价
            'dailyBalance': '-313.500000',       # 当日盈亏金额
            'dailyBalancePercent': '-0.021201',  # 当日盈亏比例
            'holdingBalance': '3500.750000',     # 持仓盈亏金额
            'holdingBalancePercent': '0.319048', # 持仓盈亏比例
            'enableAmount': 0.0,                 # 可卖数量
            'frozenAmount': 5225.0               # 冻结数量
        }
    ]
}
```

**常用字段说明**:
- `currentAmount`: 当前持仓数量
- `costPriceAccurate`: 成本价
- `lastPrice`: 最新价
- `holdingBalance`: 持仓盈亏
- `enableAmount`: 可卖数量（可用于卖出）

---

### 3. 查询资产（新接口）

**官方接口**: `POST /asset-center-server/open-api/open-assetQuery/v1`

**功能**: 查询账户资产信息，支持多币种。

```python
# 查询港币资产 (money_type=2)
result = client.query_asset(money_type=2)
print(result)
```

**入参说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| money_type | int | ❌ | 币种：0=人民币, 1=美元, 2=港币 |

**输出示例**:
```python
{
    'code': 0,
    'data': {
        'assetSingleInfoRespVOS': [              # 各账户资产详情
            {
                'asset': '9950.05',              # 总资产
                'availableBalance': '9950.05',   # 可用资金
                'cashBalance': '9950.05',        # 现金余额
                'marketValue': '0.00',           # 市值
                'frozenBalance': '0.0000',       # 冻结资金
                'purchasePower': '33895.97',     # 购买力
                'todayProfit': '0.00',           # 今日盈亏
                'holdingProfit': '0.00',         # 持仓盈亏
                'withdrawBalance': '9950.05',    # 可取资金
                'moneyType': 2,                  # 币种
                'fundAccount': '80182874',       # 资金账号
                'riskStatusCode': 1,             # 风险状态
                'mvLevelDesc': '安全'             # 风险等级描述
            }
        ],
        'moneyType': 2,
        'totalAssetValue': '121553.92',          # 总资产
        'totalCashBalance': '10168.79',          # 总现金
        'totalMarketValue': '111385.13',         # 总市值
        'userId': '1152281476134805504'
    },
    'msg': '成功'
}
```

**关键字段**:
- `totalAssetValue`: 总资产
- `totalCashBalance`: 总现金
- `totalMarketValue`: 总市值
- `purchasePower`: 购买力（可用于买入）

---

### 4. 查询资产（旧接口）

**官方接口**: `POST /stock-order-server/open-api/stock-asset`

**功能**: 查询指定市场的资产信息。

```python
# 查询美股资产
result = client.get_assets(exchange_type='5')
print(result)
```

**输出示例**:
```python
{
    'code': 0,
    'msg': '操作成功',
    'data': {
        'exchangeType': 5,
        'asset': '14501.160000',                 # 总资产
        'marketValue': '14473.250000',           # 市值
        'enableBalance': '27.91',                # 可用资金
        'withdrawBalance': '27.91',              # 可取资金
        'frozenBalance': '0.000000',             # 冻结资金
        'purchasePower': '4324.90',              # 购买力
        'riskStatusCode': 1,                     # 风险状态码
        'riskStatusName': '安全',                 # 风险状态名
        'totalDailyBalance': '-313.500000',      # 总日盈亏
        'stockHoldingList': [...]                # 持仓列表
    }
}
```

---

## 交易操作

### 5. 买入股票

**官方接口**: `POST /stock-order-server/open-api/entrust-order`

**功能**: 提交买入委托单。

```python
# 买入港股丽珠医药 (增强限价单)
result = client.buy(
    stock_code='01513',           # 股票代码
    price='25.7',                 # 委托价格
    quantity='100',               # 委托数量
    exchange_type='0',            # 市场：'0'=港股
    entrust_prop='e',             # 委托属性：'e'=增强限价单
    force_entrust=True            # 强制委托
)
print(result)
```

**入参说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| stock_code | str | ✅ | 股票代码 |
| price | str | ✅ | 委托价格 |
| quantity | str | ✅ | 委托数量 |
| exchange_type | str | ✅ | 市场：'0'=港股, '5'=美股, '67'=A股 |
| entrust_prop | str | ❌ | '0'=限价, 'e'=增强限价, 'w'=市价 |
| force_entrust | bool | ❌ | 是否强制委托 |

**委托属性说明**:
- `'0'` - 限价单：按指定价格或更好价格成交
- `'e'` - 增强限价单（港股）：允许在指定价格或更优价格成交，最多可同时与10个轮候队伍进行对盘
- `'w'` - 市价单：按市场最优价格成交

**输出示例**:
```python
{
    'code': 0,
    'msg': '操作成功',
    'data': {
        'entrustId': '2056216257909501952',    # 委托ID（用于撤单）
        'status': 1,                            # 状态：1=等待提交
        'statusName': '等待提交'
    }
}
```

---

### 6. 卖出股票

**官方接口**: `POST /stock-order-server/open-api/entrust-order`

**功能**: 提交卖出委托单。

```python
result = client.sell(
    stock_code='00700',
    price='450.0',
    quantity='100',
    exchange_type='0',
    entrust_prop='e'
)
```

**参数说明**: 同 `buy()`

---

### 7. 撤单

**官方接口**: `POST /stock-order-server/open-api/modify-order`

**功能**: 撤销未成交的委托单。

```python
result = client.cancel_order(
    entrust_id='2056216257909501952',
    force_entrust_flag=True
)
```

**入参说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| entrust_id | str | ✅ | 委托ID（下单时返回） |
| force_entrust_flag | bool | ❌ | 是否强制撤单 |

---

### 8. 改单

**官方接口**: `POST /stock-order-server/open-api/modify-order`

**功能**: 修改未成交委托单的价格或数量。

```python
result = client.modify_order(
    entrust_id='2056216257909501952',
    new_price='410.0',
    new_quantity='200'
)
```

---

## 订单查询

### 9. 查询今日订单

**官方接口**: `POST /stock-order-server/open-api/today-entrust`

**功能**: 查询当日所有委托订单。

```python
result = client.get_today_orders(
    exchange_type='100',      # '100'=所有市场
    page_num=1,
    page_size=20,
    stock_code=''             # 可选：筛选特定股票
)
print(result)
```

**输出示例**:
```python
{
    'code': 0,
    'msg': '操作成功',
    'data': {
        'pageNum': 1,
        'pageSize': 20,
        'total': 0,
        'list': [
            {
                'entrustId': '2056216257909501952',
                'stockCode': '01513',
                'stockName': '丽珠医药',
                'entrustType': 0,                # 0=买入, 1=卖出
                'entrustProp': 'e',              # 委托属性
                'entrustPrice': '25.7',
                'entrustAmount': 100.0,          # 委托数量
                'businessAmount': 0.0,           # 成交数量
                'status': 1,                     # 订单状态
                'statusName': '等待提交',
                'createTime': '10:44:10',
                'createDate': '20260514'
            }
        ]
    }
}
```

**订单状态码说明**:

| 状态码 | 说明 |
|--------|------|
| -1 | 下单失败 |
| 0 | 待成交 |
| 1 | 部分成交 |
| 2 | 已成交 |
| 3 | 已撤单 |
| 8 | 废单 |

---

### 10. 查询历史订单

**官方接口**: `POST /stock-order-server/open-api/his-entrust`

**功能**: 查询历史委托订单。

```python
result = client.get_his_orders(
    exchange_type='100',
    date_flag='1',            # 1=一周, 2=一个月, 3=三个月, 7=全部
    start_date='2024-01-01',  # date_flag=6时使用
    end_date='2024-12-31',
    page_num=1,
    page_size=20
)
print(result)
```

**date_flag 说明**:
- `'1'` - 一周
- `'2'` - 一个月
- `'3'` - 三个月
- `'4'` - 近一年
- `'5'` - 今年
- `'6'` - 自选时间（需传 start_date 和 end_date）
- `'7'` - 查询全部

**输出示例**:
```python
{
    'code': 0,
    'msg': '操作成功',
    'data': {
        'pageNum': 1,
        'pageSize': 20,
        'total': 17,
        'list': [
            {
                'entrustId': '2054749872708001792',
                'orderId': None,
                'entrustNo': '28306',
                'status': 8,                      # 8=废单
                'statusName': '废单',
                'exchangeType': 0,
                'entrustType': 0,                 # 0=买入
                'entrustProp': 'e',
                'entrustAmount': 1000.0,
                'businessAmount': 0.0,
                'entrustPrice': '22.0',
                'businessAveragePrice': 0,
                'stockCode': '00883',
                'stockName': '中国海洋石油',
                'moneyType': 2,                   # 2=港币
                'createTime': '10:25:20',
                'createDate': '20260514',
                'businessType': 'S'               # S=普通交易
            }
        ]
    }
}
```

---

### 11. 查询订单详情

**官方接口**: `POST /stock-order-server/open-api/order-detail`

**功能**: 查询单个订单的详细信息。

```python
result = client.get_order_detail(entrust_id='2056216257909501952')
```

---

### 12. 查询成交流水

**官方接口**: `POST /stock-order-server/open-api/stock-record`

**功能**: 查询成交记录。

```python
result = client.get_stock_records(
    exchange_type='0',
    start_date='2024-01-01',
    end_date='2024-12-31'
)
```

---

### 13. 查询最大可买/卖数量

**官方接口**: `POST /stock-order-server/open-api/trade-quantity`

**功能**: 查询指定股票的最大可买/卖数量。

```python
result = client.get_max_quantity(
    stock_code='00700',
    price='400.0',
    exchange_type=0
)
```

---

## 行情数据

### 14. 查询实时行情

**官方接口**: `POST /quotes-openservice/api/v1/realtime`

**功能**: 获取股票的实时行情数据。

**频率限制**: 120次/分钟

```python
result = client.get_quote(['hk00700', 'usAAPL'])
print(result)
```

**入参说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| secu_ids | List[str] | ✅ | 股票ID列表，格式：市场+代码，如'hk00700' |

**输出示例**:
```python
{
    'code': 0,
    'msg': 'success',
    'data': {
        'list': [
            {
                'market': 'hk',
                'symbol': '00700',
                'latestPrice': '460.4',          # 最新价
                'changeRate': '2.5',             # 涨跌幅%
                'changeAmount': '11.00',         # 涨跌额
                'volume': 3720176,               # 成交量
                'turnOver': 1716875706.54,       # 成交额
                'open': '460',                   # 开盘价
                'high': '463.4',                 # 最高价
                'low': '459.6',                  # 最低价
                'preClose': '460',               # 昨收价
                'bidPrice': '460.2',             # 买一价
                'askPrice': '460.4',             # 卖一价
                'bidSize': 10300,                # 买一量
                'askSize': 6800,                 # 卖一量
                'mktCap': 4197927464269.6,       # 市值
                'pe': 16,                        # 市盈率
                'pb': 3,                         # 市净率
                'trdStatus': 6                   # 交易状态：6=交易中
            },
            {
                'market': 'us',
                'symbol': 'AAPL',
                'latestPrice': '298.97',
                'volume': 42243561,
                'high': '300.51',
                'low': '296.35',
                'mktCap': 4391078823320,
                'pe': 40,
                'pb': 41
            }
        ]
    }
}
```

**交易状态说明**:

| 状态码 | 说明 |
|--------|------|
| 0 | 未知 |
| 1 | 停牌 |
| 2 | 港股波动中断 |
| 3 | 未上市 |
| 4 | 暂停上市 |
| 5 | 退市 |
| 6 | 交易中 |

---

### 15. 查询K线数据

**官方接口**: `POST /quotes-openservice/api/v1/kline`

**功能**: 获取股票的K线数据。

**频率限制**: 120次/分钟

```python
result = client.get_kline(
    secu_id='hk00700',
    kline_type=5,        # 5=日K
    count=100,           # 返回100条
    start=0,
    right=0              # 0=不复权, 1=前复权, 2=后复权
)
```

**kline_type 说明**:

| 类型值 | 说明 |
|--------|------|
| 0 | 1分钟 |
| 1 | 5分钟 |
| 2 | 15分钟 |
| 3 | 30分钟 |
| 4 | 60分钟 |
| 5 | 日K |
| 6 | 周K |
| 7 | 月K |
| 8 | 季K |
| 9 | 年K |

**输出示例**:
```python
{
    'code': 0,
    'data': {
        'list': [
            {
                'time': '20240101160000000',     # 时间戳
                'open': '440.00',                # 开盘价
                'high': '460.00',                # 最高价
                'low': '435.00',                 # 最低价
                'close': '450.00',               # 收盘价
                'volume': '1000000'              # 成交量
            }
        ]
    }
}
```

---

### 16. 查询买卖盘

**官方接口**: `POST /quotes-openservice/api/v1/orderbook`

**功能**: 获取股票的买卖盘（十档）。

**频率限制**: 120次/分钟

```python
result = client.get_orderbook('hk00700')
```

**输出示例**:
```python
{
    'code': 0,
    'data': {
        'bidList': [                         # 买盘（从高到低）
            {'price': '460.2', 'volume': 10300},
            {'price': '460.0', 'volume': 5000},
            # ... 最多10档
        ],
        'askList': [                         # 卖盘（从低到高）
            {'price': '460.4', 'volume': 6800},
            {'price': '460.6', 'volume': 3000},
            # ... 最多10档
        ]
    }
}
```

---

### 17. 查询逐笔成交

**官方接口**: `POST /quotes-openservice/api/v1/tick`

**功能**: 获取股票的逐笔成交明细。

**频率限制**: 120次/分钟

```python
result = client.get_tick(
    secu_id='hk00700',
    trade_time=0,
    seq=0,
    count=20,
    sort_direction=2      # 2=降序
)
```

---

### 18. 查询分时数据

**官方接口**: `POST /quotes-openservice/api/v1/timeline`

**功能**: 获取股票的分时数据。

**频率限制**: 120次/分钟

```python
result = client.get_timeline('hk00700', timeline_type=0)  # 0=当日, 1=五日
```

---

### 19. 查询市场状态

**官方接口**: `POST /quotes-openservice/api/v1/marketstate`

**功能**: 获取市场状态信息。

**频率限制**: 120次/分钟

```python
result = client.get_market_state('hk')  # 'hk', 'us', 'sh', 'sz'
```

**市场状态码说明**:

| 状态码 | 说明 |
|--------|------|
| 0 | 未知 |
| 1 | 启动、开市前 |
| 2 | 开盘集合竞价 |
| 3 | 暂停 |
| 4 | 连续竞价 |
| 5 | 午间休市 |
| 6 | 收盘集合竞价 |
| 7 | 已收盘 |
| 20-27 | 港股特有状态 |
| 31 | 美股盘前 |
| 32 | 美股盘后 |

---

### 20. 查询股票基础信息

**官方接口**: `POST /quotes-openservice/api/v1/basicinfo`

**功能**: 获取股票的基础信息列表。

**频率限制**: 20次/分钟

```python
result = client.get_basic_info('hk', page_num=1, page_size=50)
```

---

## WebSocket实时推送

### 21. 启动行情推送

**官方文档**: WebSocket 行情推送接口

**功能**: 通过 WebSocket 实时接收行情数据。

```python
import time
import json

# 定义数据回调函数
def my_handler(topic: str, data: str):
    """
    处理收到的行情数据
    
    Args:
        topic: 主题，如 "rt.us.TSLA"
        data: JSON格式的行情数据
    """
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
            
    elif topic.startswith("tk."):
        # 逐笔成交
        print(f"[逐笔] {topic}: {data_obj}")

# 启动推送
client.start_quote_push(handler=my_handler)
time.sleep(3)  # 等待连接建立

# 订阅行情
client.subscribe_quote(["rt.us.TSLA", "ob.us.TSLA"])

# 保持运行
time.sleep(60)

# 取消订阅
client.unsubscribe_quote(["rt.us.TSLA", "ob.us.TSLA"])

# 停止推送
client.stop_quote_push()
```

**主题格式**: `类型.市场.代码`

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

**示例主题**:
- `rt.hk.00700` - 腾讯实时行情
- `ob.us.TSLA` - 特斯拉买卖盘
- `tk.hk.00700` - 腾讯逐笔成交

---

## 实战案例

### 案例1：完整的交易流程

```python
from usmart_api import USmartClient

# 1. 创建客户端
client = USmartClient(
    X_Channel='your_channel',
    phoneNumber='your_phone',
    login_password='your_password',
    trade_passwrod='your_trade_password',
    public_key='your_public_key',
    private_key='your_private_key'
)

# 2. 登录
result = client.login()
if not result['success']:
    print(f"登录失败: {result['error']}")
    exit()

print("✅ 登录成功")

# 3. 查询资产
assets = client.query_asset()
total = assets['data']['totalAssetValue']
print(f"💰 总资产: {total}")

# 4. 查询持仓
holdings = client.get_holdings(exchange_type='5')
for stock in holdings.get('data', []):
    print(f"📈 {stock['stockCode']}: {stock['currentAmount']}股, 盈亏{stock['holdingBalance']}")

# 5. 获取行情
quote = client.get_quote(['hk00700'])
price = quote['data']['list'][0]['latestPrice']
print(f"📊 腾讯最新价: {price}")

# 6. 买入
result = client.buy(
    stock_code='00700',
    price=str(float(price) * 0.99),  # 比现价低1%买入
    quantity='100',
    exchange_type='0',
    entrust_prop='e'
)

if result['code'] == 0:
    print(f"✅ 买入委托成功，委托ID: {result['data']['entrustId']}")
else:
    print(f"❌ 买入失败: {result['msg']}")
```

---

### 案例2：定时查询持仓盈亏

```python
import time

def monitor_holdings():
    while True:
        holdings = client.get_holdings(exchange_type='100')
        total_profit = 0
        
        for stock in holdings.get('data', []):
            code = stock['stockCode']
            name = stock['stockName']
            profit = float(stock.get('holdingBalance', 0))
            total_profit += profit
            
            emoji = '📈' if profit >= 0 else '📉'
            print(f"{emoji} {code} {name}: 盈亏 {profit:.2f}")
        
        print(f"💵 总盈亏: {total_profit:.2f}")
        print("-" * 50)
        
        time.sleep(60)  # 每分钟更新

# monitor_holdings()
```

---

### 案例3：条件单（价格触发买入）

```python
import time

def conditional_buy(stock_code, target_price, quantity):
    """当价格低于目标价时买入"""
    while True:
        quote = client.get_quote([f'hk{stock_code}'])
        current_price = float(quote['data']['list'][0]['latestPrice'])
        
        print(f"当前价: {current_price}, 目标价: {target_price}")
        
        if current_price <= target_price:
            result = client.buy(
                stock_code=stock_code,
                price=str(current_price),
                quantity=quantity,
                exchange_type='0',
                entrust_prop='e'
            )
            print(f"🎯 触发买入: {result}")
            break
        
        time.sleep(5)

# conditional_buy('00700', 450.0, '100')
```

---

### 案例4：清仓所有持仓

```python
def sell_all_holdings():
    """卖出所有持仓股票"""
    holdings = client.get_holdings(exchange_type='100')
    
    for stock in holdings.get('data', []):
        code = stock['stockCode']
        qty = int(float(stock['currentAmount']))
        
        if qty > 0:
            result = client.sell(
                stock_code=code,
                price=stock['lastPrice'],
                quantity=str(qty),
                exchange_type=str(stock['exchangeType']),
                entrust_prop='e'
            )
            print(f"卖出 {code} {qty}股: {result['msg']}")

# sell_all_holdings()
```

---

### 案例5：获取K线并计算技术指标

```python
import pandas as pd

# 获取日K线
kline = client.get_kline('hk00700', kline_type=5, count=30)

# 转换为DataFrame
df = pd.DataFrame(kline['data']['list'])
df['close'] = df['close'].astype(float)

# 计算技术指标
df['ma5'] = df['close'].rolling(5).mean()    # 5日均线
df['ma10'] = df['close'].rolling(10).mean()  # 10日均线
df['ma20'] = df['close'].rolling(20).mean()  # 20日均线

# 计算MACD
exp1 = df['close'].ewm(span=12, adjust=False).mean()
exp2 = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = exp1 - exp2
df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()

print(df[['time', 'close', 'ma5', 'ma10', 'macd']].tail())
```

---

## 注意事项

1. **频率限制**: 行情接口 120次/分钟，基础信息接口 20次/分钟
2. **交易时间**: 只有在交易时段才能下单（PRO账户除外）
3. **价格格式**: 价格必须是字符串，不要传 float
4. **数量格式**: 数量必须是整数，以股为单位
5. **港股代码**: 不需要前导零（如'700'而不是'00700'）
6. **错误处理**: 始终检查返回结果中的 `code` 字段

---

## 参考链接

- [官方 API 文档](https://api-doc.usmart8.com/zh-cn/)
- [PyPI 包页面](https://pypi.org/project/usmart-api/)
- [GitHub 仓库](https://github.com/usmart/usmart-api-python)
