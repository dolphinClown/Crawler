### pyspider ###
pyspider 是一个用python实现的功能强大的网络爬虫系统，能在浏览器界面上进行脚本的编写，功能的调度和爬取结果的实时查看，后端使用常用的数据库进行爬取结果的存储，还能定时设置任务与任务优先级等。

官方参考文档：[http://docs.pyspider.org/en/latest/Quickstart/#quickstart](http://docs.pyspider.org/en/latest/Quickstart/#quickstart)


    from pyspider.libs.base_handler import *
       
    class Handler(BaseHandler):
    crawl_config = {
    }
    
    @every(minutes=24 * 60)
    def on_start(self):
    self.crawl('http://scrapy.org/', callback=self.index_page)
    
    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
    for each in response.doc('a[href^="http"]').items():
    self.crawl(each.attr.href, callback=self.detail_page)
    
    @config(priority=2)
    def detail_page(self, response):
    return {
    "url": response.url,
    "title": response.doc('title').text(),
    }


- `def on_start(self)` 脚本切入点，点击 UI 界面上的开始按钮执行。
self.crawl(url, callback=self.index_page)* 是其中最重要的接口。 它将添加一个要爬取的新任务.大多数的选项将具体通过 self.crawl 参数指定。

- `def index_page(self, response)` 得到一个响应对象 response doc* ，它是一个 <a href="https://pythonhosted.org/pyquery/">pyquery</a> 对象，pyquery 和 jQuery 比较相似，都提取页面元素的 API 。


- `def detail_page(self, response)` 返回结果的字典对象。 结果默认将被捕获到 data\resultdb.db 文件中. 可以重写 on_result(self, result) 来管理自己的结果存储，具体参考 [http://docs.pyspider.org/en/latest/Deployment/](http://docs.pyspider.org/en/latest/Deployment/)

注解：

`@every(minutes=24*60, seconds=0)*` 调度助手，告诉 on_start 方法应该每天都被调用。

`@config(age=10 * 24 * 60 * 60)*` 指定网页类型为 index_page (当 callback=self.index_page)。参数年龄可以通过 `self.crawl(url, age=10*24*60*60)`（具有最高优先级）和 `crawl_config`（具有最低优先级）来指定。

`age=10 * 24 * 60 * 60*` 告诉调度器丢弃请求，如果这个请求在10天中已经爬过这个 URL。pyspider 将默认不会爬取同一个 URL 两次（永远丢弃）。即使你已经修改了代码，但已经爬过就不会再爬了。

`@config(priority=2)*` 标记的详情页将首先被爬取。