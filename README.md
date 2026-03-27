# weather-fx-agent
这是一款进行实时天气查询及计算汇率的软件
这个 Agent 可以自动识别你是在问**实时天气**还是**特定汇率**，然后调用免费 API 获取数据并用自然语言回复。

## 功能
- 天气查询（Open-Meteo，免费，无需 Key）
- 汇率查询（open.er-api.com，免费，无需 Key）
- 自动意图识别 + 工具调用（由大模型决定何时调用）

## 1) 安装
`powershell
cd e:\ai\weather-fx-agent，这里的路径是可以选择的，根据喜好
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
`

## 2) 配置
把 .env.example 复制为 .env 并填入你的模型 API Key：#.env.example是环境变量

`powershell
Copy-Item .env.example .env
`

编辑 .env：注意：.env文件中这三个东西是对应的，KEY是大模型对应的API，URL是对应的网址，MODEL是对应的模型
`env
OPENAI_API_KEY=你的key
OPENAI_BASE_URL=https://api.openai.com/v1，注意这里是大模型的地址，如这里写的是OPENAI的网址
MODEL=gpt-4o-mini，这里是对应的GPT模型。
`
大模型的选择这里：
	
能注册外网、想省事	        先试 Groq（网上常见「免费额度」），在 Groq Console 注册 → 创建 API Key（一般是 gsk- 开头）。
不想绑卡、不想走外网 API	用 Ollama（这里是走电脑本地，直接下载就好，目前最划算！！！！）
以后有预算再切回	               OpenAI 官方




## 3) 运行。在powershell直接运行，这个
`powershell
python agent.py
`

## 4) 示例问题
- 北京现在天气怎么样？
- 上海今天风大吗？
- 人民币对伊拉克第纳尔汇率是多少？
- 100 CNY 能换多少 IQD？

## 5) 说明
- 该项目主要展示“Agent 自动识别意图并调用工具”。
- 如果 API 临时不可用，程序会返回错误信息并继续可交互。
