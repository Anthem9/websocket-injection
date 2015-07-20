WebSocket Injection
=========
WebSocket 中转注入 Proxy(for SQL Injection tools: sqlmap, etc.)

### Installation

    git clone https://github.com/RicterZ/websocket-injection
    cd websocket-injection
    pip install -r requirements.txt

### Usage for SQLMap

    python main.py --port=9999
    python sqlmap.py -u "http://localhost:9999/sqlmap?url=[target]&data=[sqli]" -p data


![](https://github.com/RicterZ/websocket-injection/raw/dev/docs/usage.png)  

### Usage for Webpage

    python main.py --port=9999

![](https://github.com/RicterZ/websocket-injection/raw/dev/docs/usage2.png)  

### License
MIT
