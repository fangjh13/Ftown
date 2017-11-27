### TopHub API

`api`以`/api/v1/tophub`开头，采用Basic Authentication，新用户请到[注册页](https://www.fythonfang.com/auth/register)注册并完成邮箱认证，也支持`token`认证（把token替换成username，password留空），使用`/api/v1/token/`获取`token`

#### github trending

`GET /api/v1/tophub/github`

#### reddit

`GET /api/v1/tophub/reddit`

#### 掘金

`GET /api/v1/tophub/juejin`

#### SegmentFault

`GET /api/v1/tophub/juejin`

#### 豆瓣图书

`GET /api/v1/tophub/douban`

###### Parmeters

|   Name   |   Type   |            Description             |
| :------: | :------: | :--------------------------------: |
| `subcat` | `string` | 虚构类和非虚构类图书，`I`代表非虚构类`F`代表虚构类，默认`F` |

