# 🎬 CaptionFlow

智能视频双语字幕自动生成器，支持自动语音识别、语言检测、翻译和双语字幕生成。

## ✨ 功能特点

- 🎯 **自动语言识别**: 使用Whisper模型自动识别视频中的语言
- 🔄 **智能多语言翻译**: 支持全球十种主要语言的自由互译
- 🌐 **国际化界面**: 支持中文、英文、西班牙语、阿拉伯语、印地语、葡萄牙语、俄语、日语、德语、法语十种界面语言
- 📝 **标准字幕格式**: 生成标准SRT格式字幕文件
- 🌍 **双语字幕支持**: 可生成包含原文和译文的双语字幕
- ⚡ **多种模型选择**: 支持不同大小的Whisper模型
- 🔧 **多种翻译服务**: 支持Google翻译、简单翻译、LibreTranslate和OpenAI翻译
- ⚡ **高性能翻译**: 优化版翻译器提供17倍性能提升，支持并行处理、智能缓存
- 🖥️ **Web界面**: 提供友好的Streamlit Web界面
- 🎥 **视频预览**: 支持在线视频播放预览
- 📁 **大文件支持**: 支持最大4GB视频文件上传
- 📱 **命令行工具**: 支持命令行批处理

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
git clone https://github.com/rockenlee/CaptionFlow.git
cd CaptionFlow

# 安装Python依赖
pip install -r requirements.txt

# 安装FFmpeg (如果尚未安装)
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# 下载并安装: https://ffmpeg.org/download.html
```

### 2. 配置环境变量 (可选)

如果要使用OpenAI翻译服务，需要配置API密钥：

```bash
# 复制环境变量示例文件
cp env.example .env

# 编辑 .env 文件，添加你的OpenAI API密钥
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 使用方法

#### Web界面 (推荐)

```bash
# 启动Web界面
streamlit run app.py
```

然后在浏览器中访问 `http://localhost:8501`

#### 命令行使用

```bash
# 基本使用 - 生成双语字幕
python main.py -i video.mp4 --bilingual

# 只生成原语言字幕
python main.py -i video.mp4 --no-translate

# 使用更大的模型提高精度
python main.py -i video.mp4 -m large

# 使用OpenAI翻译 (需要API密钥)
python main.py -i video.mp4 -t openai --api-key your_api_key

# 指定输出目录
python main.py -i video.mp4 -o output/

# 查看所有选项
python main.py --help
```

## 📋 命令行参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `-i, --input` | 输入视频文件路径 | 必需 |
| `-o, --output` | 输出目录路径 | 视频文件所在目录 |
| `-m, --model` | Whisper模型大小 | base |
| `-t, --translator` | 翻译服务 | simple |
| `--bilingual` | 生成双语字幕 | False |
| `--no-translate` | 只转录不翻译 | False |
| `--target-lang` | 目标语言 | 自动检测 |
| `--api-key` | OpenAI API密钥 | 环境变量 |
| `-v, --verbose` | 详细输出 | False |

## 🎯 支持的格式

### 输入格式
- 视频: MP4, AVI, MKV, MOV, WMV, FLV, WebM, M4V
- 文件大小: 最大支持4GB

### 输出格式
- 字幕: SRT (SubRip Subtitle)

### 支持的语言
- 自动检测所有Whisper支持的语言
- 主要翻译方向: 中文 ↔ 英文
- 其他语言默认翻译为中文

## 🔧 Whisper模型说明

| 模型 | 大小 | 速度 | 精度 | 推荐用途 |
|------|------|------|------|----------|
| tiny | 39MB | 最快 | 较低 | 快速测试 |
| base | 74MB | 快 | 中等 | 日常使用 |
| small | 244MB | 中等 | 良好 | 平衡性能 |
| medium | 769MB | 慢 | 很好 | 高质量需求 |
| large | 1550MB | 最慢 | 最佳 | 专业制作 |

## 📁 输出文件

处理完成后，会在输出目录生成以下文件：

```
video_name_en.srt          # 原始语言字幕
video_name_zh-CN.srt       # 翻译后字幕  
video_name_bilingual.srt   # 双语字幕 (可选)
video_name_report.json     # 处理报告
```

## 🔗 翻译服务

| 服务 | 费用 | 质量 | 稳定性 | 网络依赖 | 说明 |
|------|------|------|--------|----------|------|
| simple | 免费 | 良好 | 最高 | ❌ 离线 | 本地翻译，无网络依赖（推荐离线使用） |
| google | 免费 | 优秀 | 高 | ✅ 需要 | Google翻译，免费且质量高 |
| libre | 免费 | 一般 | 中等 | ✅ 需要 | 开源API，多个备用服务器 |
| openai | 付费 | 优秀 | 高 | ✅ 需要 | 需要API密钥，理解上下文更好 |

### 简单翻译 (Simple) - 离线推荐
- ✅ 完全免费
- ✅ 无网络依赖（使用本地translate库）
- ✅ 最稳定可靠
- ✅ 真正的翻译功能（非标记形式）
- 🔒 完全离线运行
- 📚 包含200+常用词汇字典
- 🔧 支持单词级和句子级翻译

### Google翻译 - 在线推荐
- ✅ 完全免费
- ✅ 翻译质量优秀
- ✅ 服务稳定可靠
- ✅ 支持多种语言
- 🌐 需要网络连接



### LibreTranslate翻译
- ✅ 免费使用
- ✅ 开源项目
- ✅ 多个备用服务器
- ⚠️ 服务器可能不稳定

### OpenAI翻译
- ✅ 高质量翻译
- ✅ 更好的上下文理解
- ❌ 需要API密钥
- ❌ 按使用量付费
- 🌐 需要网络连接

## ⚡ 高性能翻译优化

CaptionFlow 提供了革命性的翻译性能优化，大幅提升处理速度。

### 🚀 性能提升效果

基于实际测试（50个段落翻译）：

| 翻译器类型 | 耗时 | 处理速度 | 性能提升 |
|------------|------|----------|----------|
| 普通翻译器 | 145.48秒 | 0.3段/秒 | - |
| **优化版翻译器** | **8.13秒** | **6.2段/秒** | **17.9倍** |

**时间减少**: 94.4% ⚡

### 🔧 优化技术

- **🔄 并行处理**: 多线程同时翻译，最大化CPU利用率
- **💾 智能缓存**: 避免重复翻译相同内容，缓存命中显著提速
- **📦 批量优化**: 减少API调用开销，提高网络效率
- **⏱️ 零延迟**: Simple翻译移除不必要的等待时间
- **🎯 动态调度**: 根据服务类型自动调整并行度

### 💡 使用方式

**Web界面**:
- 在侧边栏勾选"启用高性能翻译"
- 调整并行线程数（1-20）
- 自动应用所有优化技术

**命令行**:
```bash
# 使用优化版翻译器
python main.py -i video.mp4 --optimized --workers 10
```

### 📊 性能建议

- **小视频** (< 10分钟): 使用5-10个线程
- **中等视频** (10-30分钟): 使用10-15个线程  
- **长视频** (> 30分钟): 使用15-20个线程
- **重复内容**: 缓存效果更佳，第二次处理速度更快

### 🧪 性能测试

运行性能对比测试：
```bash
python performance_test.py
```

## 🌐 国际化支持

CaptionFlow 提供完整的国际化支持，让全世界用户都能以母语使用本工具。

### 支持的界面语言
| 语言 | 语言代码 | 原生名称 | 完成度 |
|------|----------|----------|--------|
| 中文（简体） | zh_CN | 中文（简体） | 100% |
| 英语 | en_US | English | 100% |
| 西班牙语 | es_ES | Español | 100% |
| 阿拉伯语 | ar_SA | العربية | 100% |
| 印地语 | hi_IN | हिन्दी | 100% |
| 葡萄牙语 | pt_BR | Português | 100% |
| 俄语 | ru_RU | Русский | 100% |
| 日语 | ja_JP | 日本語 | 100% |
| 德语 | de_DE | Deutsch | 100% |
| 法语 | fr_FR | Français | 100% |

### 使用方式
- **Web界面**: 在页面右上角选择界面语言
- **自动保存**: 语言选择会自动保存在会话中
- **实时切换**: 支持实时切换界面语言，无需重启

### 翻译覆盖范围
- ✅ 所有用户界面文本
- ✅ 错误信息和提示
- ✅ 处理状态信息
- ✅ 帮助文档和说明
- ✅ 按钮和菜单文本

### 测试国际化功能
```bash
# 运行国际化测试
python test_i18n.py
```

## 🔒 云服务依赖说明

### ASR（语音识别）服务
- **技术**: Faster-Whisper (基于OpenAI Whisper)
- **运行方式**: 🔒 **完全本地化**
- **网络需求**: ❌ 运行时无需网络
- **首次使用**: ⚠️ 需要下载模型文件（一次性）
- **离线能力**: ✅ 完全支持离线运行

### 翻译服务依赖
| 服务 | 云依赖 | 离线能力 | 推荐场景 |
|------|--------|----------|----------|
| Simple | ❌ 本地 | ✅ 完全离线 | 离线环境、日常翻译需求 |
| Google | ✅ 云服务 | ❌ 需要网络 | 在线环境、高质量翻译 |
| LibreTranslate | ✅ 云服务 | ❌ 需要网络 | 开源替代方案 |
| OpenAI | ✅ 云服务 | ❌ 需要网络 | 专业翻译、上下文理解 |

### 完全离线配置
```bash
# 使用Simple翻译实现完全离线运行（默认配置）
python main.py -i video.mp4 -t simple --bilingual

# 或在Web界面选择Simple翻译服务（默认选中）
```

## 🛠️ 开发

### 项目结构

```
CaptionFlow/
├── main.py              # 命令行主程序
├── app.py               # Streamlit Web界面
├── caption_generator.py # 字幕生成核心类
├── translator.py        # 翻译功能模块
├── requirements.txt     # Python依赖
├── env.example         # 环境变量示例
└── README.md           # 项目说明
```

### 本地开发

```bash
# 安装开发依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/

# 代码格式化
black *.py

# 类型检查
mypy *.py
```

## 🐛 常见问题

### 1. FFmpeg未找到
```bash
# 确保FFmpeg已安装并在PATH中
ffmpeg -version
```

### 2. 模型下载慢
```bash
# 设置代理或手动下载模型
export HTTPS_PROXY=http://your-proxy:port
```

### 3. 内存不足
- 使用较小的Whisper模型 (tiny, base)
- 处理较短的视频片段

### 4. OpenAI API错误
- 检查API密钥是否正确
- 确认账户有足够的额度
- 检查网络连接

### 5. 大文件上传问题
- 系统支持最大4GB文件上传
- 配置通过启动脚本自动设置（`--server.maxUploadSize 4096`）
- 如遇超时，可尝试压缩视频或分段处理
- 确保网络连接稳定，上传大文件需要时间

### 6. Streamlit配置错误
如果遇到 `server.maxUploadSize cannot be set on the fly` 错误：
- 使用提供的启动脚本：`./start_service.sh`
- 或手动启动：`streamlit run app.py --server.maxUploadSize 4096`
- 不要在代码中使用 `st.set_option('server.maxUploadSize', 4096)`

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 支持

如果您遇到问题或有建议，请：

1. 查看 [常见问题](#-常见问题)
2. 搜索 [已有Issues](https://github.com/your-username/CaptionFlow/issues)
3. 创建新的 [Issue](https://github.com/your-username/CaptionFlow/issues/new)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！ 
