# crawler2
&nbsp;&nbsp;&nbsp; Generally, this is a python tool package for network crawling.<br>
&nbsp;&nbsp;&nbsp; Last month I've just post the first version of the package. Then I felt it intolerable always being waiting to avoid redirected by [weibo.cn](http://weibo.cn/). So I decided to use some proxies to fake the HTTP requests from the package.<br>
&nbsp;&nbsp;&nbsp; Embarrasedly I found it out of date to use official HTTP package urllib2. In fact pythoners tend to use [requests](http://python-requests.org/) which encapsulates urllib3 to do network crawling. So I rewrote crawler with requests in this version.<br>
&nbsp;&nbsp;&nbsp; The package has 5 modules:
- crawler: Functions about crawling web pages start with a specified url.
- weiboParser: Functions about parsing an individual page to get weibo data items.
- weiboLogin: Functions and classes about login procedure of weibo.([weibo.cn](http://weibo.cn/) only for now)
- proxies: Functions and data structures about proxies such as a proxy pool.
- DB: Just 2 functions including init_DB() and write_DB(data_list).

### Depends
&nbsp;&nbsp;&nbsp; This package have only several dependent packages.
&nbsp;&nbsp;&nbsp; You can install them by following commands under Ubuntu:<br>
&nbsp;&nbsp;&nbsp; `sudo apt-get install Python-bs4`<br>
&nbsp;&nbsp;&nbsp; `sudo apt-get install Python-lxml`<br>
&nbsp;&nbsp;&nbsp; `sudo apt-get install Python-requests`<br>
&nbsp;&nbsp;&nbsp; Or you could check [bs4 source](https://pypi.python.org/pypi/beautifulsoup4), [lxml source](https://pypi.python.org/pypi/lxml) and [requests source](https://pypi.python.org/pypi/requests) on [PyPI](https://pypi.python.org/pypi).

### Usage
- You could run the package by executing command `python crawler2` at the directory where the package is.
- You may need to modify some config arguments in \_\_init\_\_.py.
- The parser module may need to be rewrote by yourself if necessary.
