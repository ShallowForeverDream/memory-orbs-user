# 🧠 Memory Orbs · 记忆球

> 将日记中的情绪标签变成发光的记忆球。灵感来自《头脑特工队》。

这是 [`HouSiyuan2001/memory-orbs-user`](https://github.com/HouSiyuan2001/memory-orbs-user) 的社区修改分支。插件核心代码采用 MIT License；本分支保留原作者署名与许可证声明。

## 本分支变化

- 可直接使用日、周、月视图和自定义日期范围；
- 可直接使用全部视觉主题、情绪统计和笔记嵌入；
- 删除邮箱、授权码和授权状态存储；
- 删除远程授权请求、周期复验、购买入口和支付后端；
- 不调用原作者的授权或支付服务。

本分支是独立社区版本，不代表原作者的官方发行版。

## 通过 BRAT 安装

1. 在 Obsidian 中安装并启用 BRAT；
2. 打开 BRAT 设置，选择 `Add Beta Plugin`；
3. 输入：`https://github.com/ShallowForeverDream/memory-orbs-user`；
4. 下载完成后启用 Memory Orbs。

也可以将 `main.js`、`styles.css`、`manifest.json` 和字体文件复制到：

```text
<Vault>/.obsidian/plugins/memory-orbs/
```

## 基本用法

默认日记目录为：

```text
01. Daily/Day
```

示例：

```markdown
- 今天完成了一个重要任务。 #Note/life/mood/Joy #Note/life/mood/Core
- 调试时遇到了一些问题。 #Note/life/mood/Anxiety
```

详细说明见 [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)。

## 原作者

**骰子（Touzi）** — [B站：骰子xCosmology](https://b23.tv/a89jLec)

## License

MIT License。版权与许可声明见 [`LICENSE`](LICENSE)。
