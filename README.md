# dnsdb-python-sdk

**dnsdb-python-sdk** 是[DnsDB](https://dnsdb.io)为开发者提供的python SDK。使用该SDK，您可以方便的将DnsDB的查询服务集成到您的python应用中，您也可以利用它来导出查询结果。


* [DnsDB官网](https://dnsdb.io)
* [DnsDB API服务介绍](https://dnsdb.io/apiservice)
* [DnsDB Web API](https://dnsdb.io/apidoc/)

# Install

```shell
git clone https://github.com/dnsdb-team/dnsdb-python-sdk.git
cd dnsdb-python-sdk
sudo python setup.py install
```

# Quick Start:

```python
from __future__ import print_function
from dnsdb.api import APIClient

client = APIClient()
auth = client.authorize("your username", "your password")
if auth.success:
    access_token = auth.access_token
    response = client.search_dns(access_token=access_token, domain="github.com")
    if response.success:
        print(response.content['data'])
    else:
        print(response.error)
else:
    print(auth.error)
```