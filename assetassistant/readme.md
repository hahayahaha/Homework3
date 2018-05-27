# 理财小助手——个人投资管理平台

------

理财小助手是面向个人的投资管理平台，整合多种资源，用户可以在平台上获得多种投资产品的最新详情，买卖投资产品，浏览财经新闻，学习投资知识以及管理个人资产。


#设计
##设计初衷
> 随着生活水平的逐渐提高，人们开始用手上的闲钱做一些投资。但是目前的券商和银行的投资理财平台都过于专业和繁琐，，对于投资入门者并不友好，而一些非大型券商或银行的投资平台又风险太大，投资者容易上当受骗。我们希望能设计一款简洁直观的面向个人的投资管理平台。

> 除了投资操作，使用者还可以在此平台上获得各种财经资讯，学习专业投资知识，不盲目投资。

##平台结构
> * 个人资产管理
> * 新闻浏览
> * 投资教程
> * 金融产品推荐及买卖


##数据表设计
### 用户表单
|User|用户|||||||
|:--|:--|:--|:--|:--|:--|:--|:--|
|username|password|emailaddress||||||
|用户名|密码|邮箱||||||
|CharField|CharField|EmailField||||||
### 新闻及教程

|News|新闻|||||||
|:--|:--|:--|:--|:--|:--|:--|:--|
|title|content|||||||
|标题|内容|||||||
|CharField|TextField|||||||
|||||||||
###股票及基金
|RecommendStock|推荐股票|||||||
|:--|:--|:--|:--|:--|:--|:--|:--|
|code|name|rate||||||
|代码|名字|当日涨跌幅||||||
|CharField|CharField|FloatField||||||
|||||||||
|RecommendFund|推荐基金|||||||
|code|name|annualrate||||||
|代码|名字|年涨跌幅||||||
|CharField|CharField|FloatField||||||
|||||||||
|Stock|股票|||||||
|code|name|price|open|close|high|low|currentrate|
|代码|名字|当前价格|开盘价|收盘价|最高价|最低价|当前涨跌|
|CharField|CharField|FloatField|FloatField|FloatField|FloatField|FloatField|FloatField|
|||||||||
|Fund|基金|||||||
|code|name|price|currentrate|onemrate|threemrate|sixmrate|annualrate|
|代码|名字|当前价格|当前涨跌|当月涨跌|三月涨跌|六月涨跌|本年涨跌|
|CharField|CharField|FloatField|FloatField|FloatField|FloatField|FloatField|FloatField|
|||||||||

###个人收藏
|FavouriteFund|收藏基金|||||||
|:--|:--|:--|:--|:--|:--|:--|:--|
|emailaddress|code|name|rate|||||
|用户邮箱|代码|名字|当日涨跌|||||
|EmailField|CharField|CharField|FloatField|||||
|||||||||
|FavouriteStock|收藏股票|||||||
|emailaddress|code|name|rate|||||
|用户邮箱|代码|名字|当日涨跌|||||
|EmailField|CharField|CharField|FloatField|||||
|||||||||
|Own|当前持有|||||||
|emailaddress|code|name|volume|buy||||
|用户邮箱|代码|名字|持有量|买入价||||
|EmailField|CharField|CharField|FloatField|FloatField||||
###交易记录
|Hist_trade|历史交易|||||||
|:--|:--|:--|:--|:--|:--|:--|:--|
|emailaddress|code|name|volume|price|time|||
|用户邮箱|代码|名字|交易量|交易价格|交易时间|||
|EmailField|CharField|CharField|FloatField|FloatField|DateTimeField|||
|||||||||
|Prosenal_asset|按操作结算资产|||||||
|emailaddress|stock|stockprofit|fund|fundprofit|money|time||
|用户邮箱|股票资产|股票收益|基金资产|基金收益|现金资产|交易时间||
|EmailField|FloatField|FloatField|FloatField|FloatField|FloatField|DateTimeField||
|||||||||
|Hist_asset|按日结算资产|||||||
|emailaddress|stock|fund|money|time||||
|用户邮箱|股票资产|基金资产|现金资产|交易时间||||
|EmailField|FloatField|FloatField|FloatField|DateTimeField||||

##页面逻辑
> * 主页-导航到：新闻；教程；产品推荐；个人资产管理
> * 新闻-浏览新闻-新闻详情
> * 教程-浏览教程-教程详情
> * 产品推荐- 推荐列表-产品详情-产品信息；买卖；收藏
> * 个人资产管理-收藏列表；交易记录；当前资产；历史收益

------
#实现
##用户
发送邮件验证用户注册信息，保证了用户的合法有效性。
##新闻+教程
爬取最新的新闻时实更新财经新闻。
整理了适合新手入门的理财教程及基础的金融知识，循序渐进学习。
##股票+基金
实时爬取股票基金和股票的详情数据，提供可视化分析和买卖代理以及收藏。
## 个人资产管理
将个人资产分为基金、股票、现金三个部分，对每个部分进行可视化的动态跟踪。总结交易记录及收益情况。


#使用

##使用指导
>   如果是小白新手，请先阅读教程，我们会为您推荐合适的金融产品供您选择，如果是熟练的投资者，请从丰富的金融产品中理智选择投资产品。

>   接着可以浏览最新的财经资讯来优化决策。

>   个人资产管理平台提供了优秀的可视化策略，提高您的投资效率。


