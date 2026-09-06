# Stickman Explainer Video Skill

一个用于生成竖屏火柴人 AI 教学视频的 Codex Skill，覆盖选题、概念确认、旁白、分镜、渲染与成片质检。

## 主要能力

- 支持“一键生成完整视频”和“逐步确认”两种工作模式
- 默认采用“总—分—总”教学结构
- 统一生成 1440×2560、45fps 的 9:16 竖屏视频
- 自动预留顶部 10%、右侧 20%、底部 20% 平台安全区域
- 提供痛点前置、悬念提问、猎奇揭秘、场景代入四种生活映射开场 Hook
- 根据实测旁白时长安排镜头，而不是截断尾音
- 支持 Windows 默认中文语音；可选接入本地 MamboTTS
- 检查分辨率、帧率、音轨、镜头停顿、字幕策略和完整解码

## 安装

将仓库克隆或复制到 Codex 的 Skills 目录：

```text
%CODEX_HOME%/skills/stickman-explainer-video
```

重新打开 Codex 后，在对话中提出“生成火柴人教学视频”一类请求即可自动触发，也可以显式使用：

```text
$stickman-explainer-video
```

## 依赖

- Python 3
- Pillow
- FFmpeg 与 FFprobe
- Windows 默认旁白需要 `System.Speech`
- MamboTTS 为可选本地依赖，本仓库不包含语音模型或权重文件

## 目录结构

```text
stickman-explainer-video-skill/
├── SKILL.md
├── agents/
├── references/
└── scripts/
```

具体工作流、制作规范和可复用脚本请查看 [SKILL.md](SKILL.md)。
