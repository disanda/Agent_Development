# 智能体开发教程

本教程的动机：

>以金融数据处理(交易)为案例，讲解智能体开发技术。

## 1.教程所需配置

### 1.1 开发环境

```
python == 3.10
langchain == 1.0.2
```

### 1.2 所需API

当前还是自学或教学阶段，API都是基于免费的，这里持续更新：

- 大模型
 - GLM: https://www.bigmodel.cn/  (免费2kw+测试 token)

- 金融数据
 - Tushare: https://tushare.pro/ (需要注册，学生有任务)
 - alphavantage：https://www.alphavantage.co/ （未测试过）

## 2.教程目录

### 2.1 案例1:langchain工具测试

实现三个tool：

- 1.让智能体读取网页数据并总结
- 2.让智能体读取本地表格并总结
- 3.让智能体调用api读取股价数据并保存到本地

[本例教程地址](./1.md)

### 2.2 案例2: MCP测试

同样实现三个tool：

- 1.构建mcp server端
- 2.构建mcp client端
- 3.分析两端操作，即大模型api反馈信息

[本例教程地址](./2.md)