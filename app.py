import streamlit as st
import os
import tempfile
import json
from datetime import datetime
import logging
from pathlib import Path
import zipfile
import io

from caption_generator import CaptionGenerator
from translator import Translator
from i18n import i18n

# 配置页面
# 注意：4GB文件上传支持通过启动脚本的命令行参数配置
st.set_page_config(
    page_title="CaptionFlow - 双语字幕生成器",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_session_state():
    """初始化会话状态"""
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'result_data' not in st.session_state:
        st.session_state.result_data = None
    if 'generated_files' not in st.session_state:
        st.session_state.generated_files = {}

def create_download_zip(files_dict):
    """创建下载的ZIP文件"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, filepath in files_dict.items():
            if os.path.exists(filepath):
                zip_file.write(filepath, filename)
    
    zip_buffer.seek(0)
    return zip_buffer

def main():
    """主应用函数"""
    init_session_state()
    
    # 初始化会话状态中的语言设置
    if 'interface_language' not in st.session_state:
        st.session_state.interface_language = 'zh_CN'
    
    # 设置当前语言
    i18n.set_language(st.session_state.interface_language)
    
    # 页面顶部语言选择器
    col1, col2 = st.columns([3, 1])
    with col2:
        available_languages = i18n.get_available_languages()
        selected_language = st.selectbox(
            i18n.t("app.language_selector"),
            options=list(available_languages.keys()),
            format_func=lambda x: available_languages[x],
            index=list(available_languages.keys()).index(st.session_state.interface_language),
            key="language_selector"
        )
        
        if selected_language != st.session_state.interface_language:
            st.session_state.interface_language = selected_language
            i18n.set_language(selected_language)
            st.rerun()
    
    # 标题和描述
    st.title(i18n.t("app.title"))
    st.markdown(f"### {i18n.t('app.subtitle')}")
    st.markdown("---")
    
    # 侧边栏设置
    st.sidebar.header(i18n.t("sidebar.settings"))
    
    # Whisper模型选择
    model_size = st.sidebar.selectbox(
        i18n.t("sidebar.model_selection"),
        ["tiny", "base", "small", "medium", "large-v2"],
        index=1,
        help=i18n.t("sidebar.model_help")
    )
    
    # 翻译服务选择
    translator_service = st.sidebar.selectbox(
        i18n.t("sidebar.translator_selection"),
        ["simple", "google", "libre", "openai"],
        index=0,
        help=i18n.t("sidebar.translator_help")
    )
    
    # 目标语言选择
    language_options = {
        "zh": i18n.t("languages.zh"),
        "en": i18n.t("languages.en"),
        "es": i18n.t("languages.es"),
        "fr": i18n.t("languages.fr"),
        "de": i18n.t("languages.de"),
        "pt": i18n.t("languages.pt"),
        "ru": i18n.t("languages.ru"),
        "ja": i18n.t("languages.ja"),
        "ar": i18n.t("languages.ar"),
        "hi": i18n.t("languages.hi")
    }
    
    target_language = st.sidebar.selectbox(
        i18n.t("sidebar.target_language"),
        options=list(language_options.keys()),
        format_func=lambda x: language_options[x],
        index=0
    )

    # OpenAI API密钥输入
    api_key = None
    if translator_service == "openai":
        api_key = st.sidebar.text_input(
            "OpenAI API Key",
            type="password",
            help="Required for OpenAI translation service"
        )
        if not api_key:
            st.sidebar.warning("⚠️ OpenAI API key required for OpenAI translation")
    
    # 输出选项
    st.sidebar.header("📤 Output Options")
    generate_bilingual = st.sidebar.checkbox(
        i18n.t("sidebar.bilingual"), 
        value=True,
        help=i18n.t("sidebar.bilingual_help")
    )
    
    # 主界面
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header(i18n.t("app.file_upload"))
        
        uploaded_file = st.file_uploader(
            i18n.t("app.file_upload"),
            type=['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'm4v'],
            help=i18n.t("app.file_upload_help")
        )
        
        if uploaded_file is not None:
            # 显示文件信息
            st.success(f"✅ {i18n.t('app.success')}: {uploaded_file.name}")
            file_size = uploaded_file.size / (1024 * 1024)  # MB
            st.info(f"📊 File size: {file_size:.2f} MB")
            
            # 视频播放器
            st.subheader("🎥 Video Preview")
            try:
                # 创建临时文件用于预览
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as preview_file:
                    preview_file.write(uploaded_file.getvalue())
                    preview_file_path = preview_file.name
                
                # 使用Streamlit的video组件播放视频
                with open(preview_file_path, 'rb') as video_file:
                    video_bytes = video_file.read()
                    st.video(video_bytes)
                
                # 清理临时文件
                try:
                    os.unlink(preview_file_path)
                except:
                    pass
                    
            except Exception as e:
                st.warning(f"⚠️ Cannot preview video: {str(e)}")
                st.info("💡 This doesn't affect processing functionality, you can continue with subtitle generation")
            
            # 处理按钮
            if st.button(f"🚀 {i18n.t('app.processing')}", type="primary"):
                if translator_service == "openai" and not api_key:
                    st.error("❌ OpenAI API key required for OpenAI translation")
                    return
                
                # 创建临时文件
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                    # 重新读取文件内容用于处理
                    uploaded_file.seek(0)  # 回到文件开头
                    tmp_file.write(uploaded_file.read())
                    temp_video_path = tmp_file.name
                
                try:
                    # 处理视频
                    process_video(
                        temp_video_path,
                        uploaded_file.name,
                        model_size,
                        translator_service,
                        target_language,
                        api_key,
                        generate_bilingual
                    )
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_video_path):
                        os.unlink(temp_video_path)
    
    with col2:
        st.header("ℹ️ Instructions")
        
        features_text = f"""
        **{i18n.t("app.subtitle")}:**
        - 🎯 Automatic video language detection
        - 🔄 Smart multi-language translation
        - 📝 Generate standard SRT subtitles
        - 🌍 Support bilingual subtitles
        - ⚡ Multiple model options
        - 🎥 Video preview function
        - 📁 Support 4GB large files
        
        **Supported formats:**
        - Video: MP4, AVI, MKV, MOV, etc.
        - File size: Maximum 4GB
        - Output: SRT subtitle files
        
        **Processing flow:**
        1. Upload video file (supports 4GB)
        2. Preview video content
        3. Automatically extract audio
        4. Speech recognition to text
        5. Detect original language
        6. Translate to target language
        7. Generate subtitle files
        """
        
        st.markdown(features_text)
    
    # 显示处理结果
    if st.session_state.processing_complete and st.session_state.result_data:
        display_results()

def process_video(video_path, video_name, model_size, translator_service, target_language, api_key, generate_bilingual):
    """处理视频生成字幕"""
    
    # 创建临时输出目录
    output_dir = tempfile.mkdtemp()
    video_basename = os.path.splitext(video_name)[0]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 步骤1: 初始化字幕生成器
        status_text.text(f"🔧 {i18n.t('processing.extracting_audio')}")
        progress_bar.progress(10)
        
        caption_generator = CaptionGenerator(model_size=model_size)
        
        # 步骤2: 处理视频
        status_text.text(f"🎵 {i18n.t('processing.speech_recognition')}")
        progress_bar.progress(30)
        
        result = caption_generator.process_video(video_path, output_dir)
        
        if not result['success']:
            st.error(f"❌ {i18n.t('errors.processing_failed')}: {result['error']}")
            return
        
        detected_language = result['detected_language']
        segments = result['segments']
        original_srt_path = result['original_srt_path']
        
        progress_bar.progress(50)
        
        files_generated = {
            f"{video_basename}_{detected_language}.srt": original_srt_path
        }
        
        # 步骤3: 翻译
        status_text.text(f"🌍 {i18n.t('processing.translating')}")
        progress_bar.progress(60)
        
        translator = Translator(service=translator_service, api_key=api_key)
        
        status_text.text(f"🔄 {i18n.t('processing.translating')} {translator.get_language_name(target_language)}...")
        progress_bar.progress(70)
        
        translations = translator.translate_segments(
            segments,
            target_language=target_language,
            source_language=detected_language
        )
        
        # 步骤4: 生成翻译字幕
        status_text.text(f"📝 {i18n.t('processing.generating_subtitle')}")
        progress_bar.progress(85)
        
        translated_srt = caption_generator.create_srt_subtitles(
            [{'start': seg['start'], 'end': seg['end'], 'text': trans} 
             for seg, trans in zip(segments, translations)],
            target_language
        )
        
        translated_srt_path = os.path.join(output_dir, f"{video_basename}_{target_language}.srt")
        caption_generator.save_subtitles(translated_srt, translated_srt_path)
        
        files_generated[f"{video_basename}_{target_language}.srt"] = translated_srt_path
        
        # 步骤5: 生成双语字幕（如果需要）
        if generate_bilingual:
            status_text.text(f"🌐 {i18n.t('processing.generating_subtitle')} (Bilingual)")
            progress_bar.progress(95)
            
            bilingual_srt = caption_generator.create_bilingual_srt(
                segments,
                translations,
                detected_language,
                target_language
            )
            
            bilingual_srt_path = os.path.join(output_dir, f"{video_basename}_bilingual.srt")
            caption_generator.save_subtitles(bilingual_srt, bilingual_srt_path)
            
            files_generated[f"{video_basename}_bilingual.srt"] = bilingual_srt_path
        
        # 完成
        status_text.text(f"✅ {i18n.t('processing.completed')}")
        progress_bar.progress(100)
        
        # 保存结果到会话状态
        st.session_state.result_data = {
            'video_name': video_name,
            'detected_language': detected_language,
            'target_language': target_language,
            'segments_count': len(segments),
            'model_used': model_size,
            'translator_used': translator_service,
            'bilingual_generated': generate_bilingual
        }
        st.session_state.generated_files = files_generated
        st.session_state.processing_complete = True
        
        # 清理资源
        caption_generator.cleanup()
        
        # 重新运行以显示结果
        st.rerun()
        
    except Exception as e:
        logger.error(f"Processing error: {e}", exc_info=True)
        st.error(f"❌ {i18n.t('errors.processing_failed')}: {str(e)}")
        progress_bar.progress(0)
        status_text.text("")

def display_results():
    """显示处理结果"""
    st.header(f"🎉 {i18n.t('processing.completed')}")
    
    result = st.session_state.result_data
    files = st.session_state.generated_files
    
    # 显示处理信息
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Video File", result['video_name'])
    
    with col2:
        detected_lang = result['detected_language']
        target_lang = result.get('target_language', '')
        st.metric("Language", f"{detected_lang} → {target_lang}")
    
    with col3:
        st.metric("Subtitle Segments", f"{result['segments_count']} segments")
    
    # 显示生成的文件
    st.subheader("📄 Generated Files")
    
    for filename, filepath in files.items():
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"📝 {filename}")
            with col2:
                st.download_button(
                    label=i18n.t("app.download"),
                    data=content,
                    file_name=filename,
                    mime="text/plain",
                    key=f"download_{filename}"
                )
    
    # 批量下载
    if len(files) > 1:
        st.subheader("📦 Batch Download")
        zip_data = create_download_zip(files)
        
        st.download_button(
            label="📦 Download All Subtitle Files (ZIP)",
            data=zip_data,
            file_name=f"{os.path.splitext(result['video_name'])[0]}_subtitles.zip",
            mime="application/zip"
        )
    
    # 预览字幕内容
    st.subheader("👀 字幕预览")
    
    selected_file = st.selectbox(
        "选择要预览的字幕文件",
        list(files.keys())
    )
    
    if selected_file and selected_file in files:
        filepath = files[selected_file]
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 显示前几行内容
            lines = content.split('\n')
            preview_lines = lines[:50]  # 只显示前50行
            
            st.code('\n'.join(preview_lines), language='srt')
            
            if len(lines) > 50:
                st.info(f"📄 显示前50行，总共{len(lines)}行")
    
    # 重新处理按钮
    if st.button("🔄 处理新视频"):
        st.session_state.processing_complete = False
        st.session_state.result_data = None
        st.session_state.generated_files = {}
        st.rerun()

# 侧边栏信息
with st.sidebar:
    st.markdown("---")
    st.markdown("### 📖 关于")
    st.markdown("""
    **CaptionFlow** 是一个智能的视频字幕生成工具，使用最新的AI技术为视频自动生成高质量的双语字幕。
    
    **技术栈:**
    - 🎵 Faster-Whisper (语音识别)
    - 🌍 Google / Simple / LibreTranslate / OpenAI (翻译)
    - 📝 SRT (字幕格式)
    
    **开源项目:** 
    GitHub: CaptionFlow
    """)

if __name__ == "__main__":
    main() 