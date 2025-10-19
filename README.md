
# 视频批量字幕生成工具 (gen_subtitle)

本项目是一个利用 OpenAI Whisper 模型为视频文件批量生成SRT字幕的工具。它能够自动处理指定文件夹内的所有视频，提取音频，进行语音识别，并生成与视频文件同名的`.srt`字幕文件。

项目提供了两种使用方式：
1.  **`ui_demo.py`**: 一个基于 Gradio 的图形用户界面，推荐普通用户使用。
2.  **`jp_subtitle.py`**: 一个纯命令行的脚本，适合进阶用户或集成到自动化流程中。

## ✨ 主要功能

*   **批量处理**: 自动扫描并处理指定文件夹内的所有视频文件。
*   **高精度识别**: 基于 OpenAI Whisper 模型，支持多种语言的高质量语音识别。
*   **SRT格式输出**: 生成标准的 `.srt` 字幕文件，兼容绝大多数视频播放器。
*   **灵活的模型选择**: 用户可以在多种 Whisper 模型（tiny, base, small, medium, large）之间选择，以平衡速度和精度。
*   **用户友好的界面**: 提供图形界面，用户无需修改代码即可轻松使用。
*   **跨平台**: 依赖的库均为跨平台库，可在 Windows, macOS, Linux 上运行。

## ⚙️ 环境要求

1.  **Python**: 版本 `>=3.12`
2.  **FFmpeg**: 必须在您的系统上安装，并且其路径已添加到系统环境变量（`PATH`）中。Whisper 需要调用 FFmpeg 来从视频中提取音频。
    *   您可以从 [FFmpeg 官网](https://ffmpeg.org/download.html) 下载并安装。

## 🚀 安装与部署

本项目推荐使用 `uv`，一个由 `ruff` 的作者开发的极速 Python 包安装与管理工具，它可以替代 `pip` 和 `venv`。

1.  **安装 uv (如果尚未安装)**
    如果您还没有 `uv`，可以通过 `pip` 或系统的包管理器进行安装。
    ```bash
    # 通过 pip (通用)
    pip install uv
    ```
    更多安装方式请参考 [uv 官方文档](https://github.com/astral-sh/uv)。

2.  **克隆或下载项目**
    ```bash
    git clone <your-repository-url>
    cd gen_subtitle
    ```

3.  **创建虚拟环境并安装依赖**
    `uv` 可以非常方便地创建虚拟环境并从 `pyproject.toml` 安装依赖。

    ```bash
    # 1. 创建虚拟环境 (会在当前目录创建 .venv 文件夹)
    uv venv

    # 2. 激活虚拟环境
    # Windows (Command Prompt)
    .\.venv\Scripts\activate
    # Windows (PowerShell)
    .\.venv\Scripts\Activate.ps1
    # macOS / Linux
    source .venv/bin/activate

    # 3. 使用 uv 安装所有依赖项
    # 它会自动读取 pyproject.toml 文件
    uv pip install .
    ```
    完成以上步骤后，您的运行环境就准备就绪了。

## 📖 使用说明

### 方式一：使用图形用户界面 (推荐)

这是最简单直接的使用方式。

1.  **启动程序**:
    在激活虚拟环境后，于项目根目录下运行以下命令：
    ```bash
    uv run ui_demo.py
    ```

2.  **操作界面**:
    *   程序运行后，会自动在浏览器中打开一个操作界面。
    *   **视频文件夹路径**: 填入您存放视频文件的文件夹绝对路径 (例如: `D:\Videos`)。
    *   **视频语言**: 从下拉列表中选择视频的原始语言。如果选择 "Auto Detect"，Whisper 会自动检测语言。
    *   **Whisper 模型大小**: 根据您的电脑配置和对精度的要求选择模型。`small` 是一个不错的平衡点，`large` 精度最高但需要较好的硬件和更长的时间。
    *   **开始处理**: 点击按钮，程序将开始处理，并在下方的“处理日志”文本框中实时显示进度。

    处理完成后，生成的 `.srt` 字幕文件会出现在您的视频文件夹中。

### 方式二：使用命令行脚本

此方式需要您直接修改脚本文件。

1.  **修改配置**:
    打开 `jp_subtitle.py` 文件，找到顶部的“配置区域”，并修改以下变量：
    *   `VIDEO_FOLDER`: 设置为您的视频文件夹路径。
    *   `MODEL_SIZE`: 设置您想使用的 Whisper 模型大小。
    *   `LANGUAGE`: 设置视频的语言。

2.  **运行脚本**:
    保存修改后，在已激活的虚拟环境中运行：
    ```bash
    uv run jp_subtitle.py
    ```
    脚本会开始处理指定文件夹中的视频，并在控制台打印进度。

## 📂 项目文件结构

```
gen_subtitle/
├── .gitignore          # Git忽略文件配置
├── .python-version     # 指定Python版本
├── jp_subtitle.py      # 核心功能的命令行脚本
├── pyproject.toml      # 项目配置文件，包含依赖列表
├── README.md           # 本说明文档
└── ui_demo.py          # 基于Gradio的图形用户界面脚本
```