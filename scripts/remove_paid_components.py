#!/usr/bin/env python3
"""Remove Memory Orbs activation/payment components from the distributable fork.

This script is intentionally conservative: every executable-code edit requires
an exact marker. It aborts when the upstream bundle shape differs, rather than
silently producing a damaged plugin.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "main.js"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def remove_between(
    text: str,
    start: str,
    end: str,
    label: str,
    replacement: str = "",
) -> str:
    start_index = text.find(start)
    if start_index < 0:
        raise RuntimeError(f"{label}: start marker not found")
    end_index = text.find(end, start_index + len(start))
    if end_index < 0:
        raise RuntimeError(f"{label}: end marker not found")
    return text[:start_index] + replacement + text[end_index:]


def patch_main_js() -> None:
    text = MAIN.read_text(encoding="utf-8")

    # Embedded renderer: remove the activation-only early return.
    text = remove_between(
        text,
        '      if (!this.plugin.settings.activated) {\n',
        '      const allEntries = dayMemories.flatMap((day) => day.entries);\n',
        "embedded activation gate",
    )

    # Main view: use the selected theme and full date range unconditionally.
    text = replace_once(
        text,
        '    const isLimited = !this.plugin.settings.activated;\n'
        '    const vt = isLimited ? "classic" : this.plugin.settings.visualTheme;\n',
        '    const vt = this.plugin.settings.visualTheme;\n',
        "main view activation state",
    )
    text = replace_once(
        text,
        '    if (vt === "cosmos" && !isLimited) {\n',
        '    if (vt === "cosmos") {\n',
        "cosmos theme restriction",
    )
    text = remove_between(
        text,
        '    if (isLimited) {\n      toolbar = container.createDiv({ cls: "mo-toolbar" });\n',
        '    toolbar = container.createDiv({ cls: "mo-toolbar" });\n',
        "locked toolbar",
    )
    text = replace_once(
        text,
        '      const { start, end } = isLimited ? { start: this.getTodayString(), end: this.getTodayString() } : this.getDateRange(effectiveMode);\n',
        '      const { start, end } = this.getDateRange(effectiveMode);\n',
        "today-only date range",
    )
    text = replace_once(
        text,
        '      let displayMemories = dayMemories;\n'
        '      if (isLimited) {\n'
        '        const today = this.getTodayString();\n'
        '        displayMemories = dayMemories.filter((d) => d.date === today);\n'
        '      }\n',
        '      const displayMemories = dayMemories;\n',
        "today-only memory filter",
    )
    text = remove_between(
        text,
        '        if (isLimited) {\n          empty.createDiv({\n',
        '        return;\n',
        "empty-state activation prompt",
    )
    text = replace_once(
        text,
        '      if (isLimited) {\n'
        '        this.renderByDay(orbsContainer, displayMemories);\n'
        '      } else if (effectiveMode === "month") {\n'
        '        this.renderByWeek(orbsContainer, displayMemories);\n'
        '      } else {\n'
        '        this.renderByDay(orbsContainer, displayMemories);\n'
        '      }\n',
        '      if (effectiveMode === "month") {\n'
        '        this.renderByWeek(orbsContainer, displayMemories);\n'
        '      } else {\n'
        '        this.renderByDay(orbsContainer, displayMemories);\n'
        '      }\n',
        "limited rendering branch",
    )
    text = remove_between(
        text,
        '      if (isLimited) {\n        const banner = orbsContainer.createDiv({ cls: "mo-activation-banner" });\n',
        '      if (statsBtn) {\n',
        "activation footer banner",
    )

    # Remove activation state, remote activation/verification and payment links.
    text = replace_once(
        text,
        '  visualTheme: "classic",\n'
        '  customEmotions: [...DEFAULT_EMOTIONS],\n'
        '  activated: false,\n'
        '  activatedEmail: "",\n'
        '  activationCode: "",\n'
        '  lastVerifiedAt: 0,\n'
        '  verifyFailCount: 0\n'
        '};\n',
        '  visualTheme: "classic",\n'
        '  customEmotions: [...DEFAULT_EMOTIONS]\n'
        '};\n',
        "activation settings",
    )
    text = remove_between(
        text,
        'var WEBSITE_BASE = "https://memory-orbs.pages.dev";\n',
        'var MemoryOrbsSettingTab = class extends import_obsidian.PluginSettingTab {\n',
        "activation network functions",
    )

    # Settings tab: retain normal configuration, remove activation/purchase UI.
    text = remove_between(
        text,
        '    containerEl.createEl("h2", { text: "\\u{1F511} \\u6FC0\\u6D3B" });\n',
        '    new import_obsidian.Setting(containerEl).setName("\\u65E5\\u8BB0\\u76EE\\u5F55")',
        "settings activation and purchase section",
        '    containerEl.createEl("h2", { text: "Memory Orbs \\u8BBE\\u7F6E" });\n',
    )

    # Remove activation modal and startup command/check.
    text = remove_between(
        text,
        'var ActivateModal = class extends import_obsidian.Modal {\n',
        'var MemoryOrbsPlugin = class extends import_obsidian.Plugin {\n',
        "activation modal",
    )
    text = replace_once(text, '    checkActivation(this);\n', '', "startup verification")
    text = remove_between(
        text,
        '    this.addCommand({\n      id: "activate-memory-orbs",\n',
        '    this.addSettingTab(new MemoryOrbsSettingTab(this.app, this));\n',
        "activation command",
    )

    # Remove stale authorization data from users who previously ran upstream.
    text = replace_once(
        text,
        '  async loadSettings() {\n'
        '    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());\n',
        '  async loadSettings() {\n'
        '    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());\n'
        '    for (const key of ["activated", "activatedEmail", "activationCode", "lastVerifiedAt", "verifyFailCount"]) {\n'
        '      delete this.settings[key];\n'
        '    }\n',
        "legacy activation data cleanup",
    )
    text = replace_once(
        text,
        'https://raw.githubusercontent.com/HouSiyuan2001/memory-orbs-user/main/SmileySans-Oblique.ttf',
        'https://raw.githubusercontent.com/ShallowForeverDream/memory-orbs-user/main/SmileySans-Oblique.ttf',
        "fork font URL",
    )

    forbidden = {
        "activationCode": "activation code state",
        "activatedEmail": "activation email state",
        "requestActivation(": "activation request",
        "checkActivation(": "activation verification",
        '"/activate"': "activation endpoint",
        '"/verify"': "verification endpoint",
        "WEBSITE_BUY_URL": "purchase URL",
        "new ActivateModal": "activation modal invocation",
        "activate-memory-orbs": "activation command",
        "!this.plugin.settings.activated": "activation gate",
        "isLimited": "limited/free-mode branch",
    }
    leftovers = [description for token, description in forbidden.items() if token in text]
    if leftovers:
        raise RuntimeError("main.js audit failed: " + ", ".join(leftovers))

    MAIN.write_text(text, encoding="utf-8")


def write_readme() -> None:
    content = """# 🧠 Memory Orbs · 记忆球

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
"""
    (ROOT / "README.md").write_text(content, encoding="utf-8")


def patch_user_guide() -> None:
    path = ROOT / "docs" / "USER_GUIDE.md"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "未激活时只显示当天记忆球；激活后可以使用完整时间范围。",
        "此社区分支可直接使用完整时间范围。",
    )
    text = text.replace(
        "https://github.com/HouSiyuan2001/memory-orbs-user",
        "https://github.com/ShallowForeverDream/memory-orbs-user",
    )
    text = text.replace(
        "如果想使用完整功能，需要在插件设置中输入激活码。",
        "安装并启用此社区分支后即可使用完整功能。",
    )
    path.write_text(text, encoding="utf-8")


def write_landing_page() -> None:
    content = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Memory Orbs · 社区分支</title>
  <style>
    body{max-width:760px;margin:64px auto;padding:0 20px;font:17px/1.7 system-ui,-apple-system,"Segoe UI","PingFang SC",sans-serif;color:#e9e9f2;background:#151525}
    main{padding:30px;border:1px solid #34344d;border-radius:18px;background:#202036}a{color:#9fc5ff}code{background:#111120;padding:2px 6px;border-radius:5px}
  </style>
</head>
<body><main>
  <h1>🔮 Memory Orbs</h1>
  <p>这是 Memory Orbs 的社区修改分支。安装后可直接使用完整的日、周、月视图、主题、统计和嵌入功能。</p>
  <h2>BRAT 安装</h2>
  <ol><li>安装并启用 BRAT。</li><li>选择 <code>Add Beta Plugin</code>。</li><li>输入 <a href="https://github.com/ShallowForeverDream/memory-orbs-user">ShallowForeverDream/memory-orbs-user</a>。</li></ol>
  <p>本分支保留原作者署名和 MIT License，不代表原作者的官方发行版。</p>
</main></body></html>
"""
    (ROOT / "index.html").write_text(content, encoding="utf-8")


def patch_manifest() -> None:
    path = ROOT / "manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = "1.0.4"
    data["description"] = "头脑特工队风格记忆球可视化——社区修改分支，可直接使用完整功能"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    versions = ROOT / "versions.json"
    if versions.exists():
        mapping = json.loads(versions.read_text(encoding="utf-8"))
        mapping["1.0.4"] = data.get("minAppVersion", "1.0.0")
        versions.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def remove_payment_backend() -> None:
    targets = [
        ROOT / "functions",
        ROOT / "alipay-qr.png",
        ROOT / "wrangler.toml",
    ]
    for path in targets:
        if path.is_dir():
            shutil.rmtree(path)
        elif path.exists():
            path.unlink()


def write_change_log() -> None:
    content = """# Community Fork Changes

Upstream: `HouSiyuan2001/memory-orbs-user`

Removed from this fork:

- client-side feature locking and today-only filtering;
- authorization email/code/state storage;
- activation and periodic verification requests;
- activation modal, command, purchase links and payment landing page;
- Cloudflare payment/authorization backend and payment QR asset.

Preserved:

- original copyright and MIT License;
- diary parsing, orb rendering, themes, statistics, embedded views and BRAT support;
- original author attribution.

This is an independent community fork, not an official upstream release.
"""
    (ROOT / "FORK_CHANGES.md").write_text(content, encoding="utf-8")


def audit_repository() -> None:
    if (ROOT / "functions").exists():
        raise RuntimeError("payment/authorization backend directory still exists")
    if (ROOT / "alipay-qr.png").exists():
        raise RuntimeError("payment QR asset still exists")

    forbidden_by_file = {
        ROOT / "main.js": [
            "requestActivation(", "checkActivation(", "activationCode",
            "activatedEmail", "WEBSITE_BUY_URL", "activate-memory-orbs",
            '"/activate"', '"/verify"', "new ActivateModal", "isLimited",
        ],
        ROOT / "index.html": ["支付宝", "付款金额", "purchase-modal", "fullscreen-pay-modal"],
    }
    failures = []
    for path, tokens in forbidden_by_file.items():
        text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token in text:
                failures.append(f"{path.relative_to(ROOT)} contains {token!r}")
    if failures:
        raise RuntimeError("repository audit failed:\n- " + "\n- ".join(failures))


if __name__ == "__main__":
    patch_main_js()
    write_readme()
    patch_user_guide()
    write_landing_page()
    patch_manifest()
    remove_payment_backend()
    write_change_log()
    audit_repository()
    print("Paid/activation components removed and repository audit passed.")
