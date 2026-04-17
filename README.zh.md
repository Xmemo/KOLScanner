# Signal QA for Solana Meme Coin Channels

> 审计导出的 Telegram 频道历史消息，把噪音信号变成证据。

一个面向 Telegram 频道历史导出的信号质量审查工具包。

## 为什么存在

加密 Telegram 里信号很多，但大多数都很嘈杂。  
真正的问题不是“有没有信号”，而是“质量好不好”。

这个工具包的目标是帮助你审查频道，而不是盲信喊单。

## 它能做什么

- 导入 Telegram 频道历史消息导出文件
- 把杂乱消息整理成结构化信号记录
- 将每条信号关联后验市场数据
- 用胜率、EV 代理值、Lift 和稳定性指标给频道打分
- 生成 CSV、JSON、Markdown、HTML 和仪表盘视图

## 它不是什么

- 不是交易机器人
- 不是自动抓 Telegram 的爬虫
- 不是保证盈利的 alpha 工具
- 不是盈利承诺

## 输入方式

1. 从 Telegram Desktop 或类似流程，本地导出频道历史消息
2. 把 JSON 文件或 JSON 文件夹交给命令行工具
3. 可以选择使用 Solana Tracker API key，或者本地市场数据 fixture CSV

## 输出

每个频道会生成：

- `signals.csv`
- `signal_evaluations.csv`
- `channel_summary.json`
- `channel_summary.md`
- `channel_summary.html`

多频道运行时，还会生成：

- `workspace_summary.csv`
- `workspace_summary.json`

## 快速开始

```bash
cd signal_qa_open_source
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
PYTHONPATH=src python3 -m signal_qa examples/sample_telegram_export.json \
  --market-fixture examples/sample_market_prices.csv \
  --output-dir outputs/demo
```

联网 API 模式：

```bash
export SOLANA_TRACKER_API_KEY="your-key"
PYTHONPATH=src python3 -m signal_qa path/to/exported_channel.json --output-dir outputs/live
```

## 仪表盘

仓库里包含一个最小的 Streamlit 仪表盘，用来浏览频道摘要。  
它会显示频道排名、质量分、覆盖率、胜率和等级分布。

运行方式：

```bash
PYTHONPATH=src streamlit run dashboard/app_streamlit.py
```

## 安全姿态

- 不提交 API key
- 不包含私有数据集
- 原始导出文件和生成结果默认忽略
- 真实凭证保留在本地 `.env` 文件中

安全说明见 [`security/README.md`](security/README.md)。

## 仓库结构

```text
signal_qa_open_source/
  src/signal_qa/
  dashboard/
  examples/
  security/
  tests/
```

## 适合谁

- 想过滤噪音频道的交易者
- 想要可复现信号审计的研究者
- 想在加 AI / ML 前先有中性评估层的开发者

## 一句话版本

一个面向 Solana meme 币和山寨币 Telegram 频道的信号质量审查工具包。

