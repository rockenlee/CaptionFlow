from faster_whisper import WhisperModel
import os
import srt
from datetime import timedelta
from typing import List, Tuple, Dict
import tempfile
from moviepy.editor import VideoFileClip
from langdetect import detect
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CaptionGenerator:
    def __init__(self, model_size: str = "base"):
        """
        初始化字幕生成器
        
        Args:
            model_size: Whisper模型大小 ("tiny", "base", "small", "medium", "large-v2")
        """
        self.model_size = model_size
        self.model = None
        self.load_model()
    
    def load_model(self):
        """加载Whisper模型"""
        try:
            logger.info(f"正在加载Faster-Whisper模型: {self.model_size}")
            # 使用CPU模式，确保兼容性
            self.model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            logger.info("模型加载完成")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise
    
    def extract_audio(self, video_path: str) -> str:
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            音频文件路径
        """
        try:
            logger.info("正在提取音频...")
            
            # 创建临时音频文件
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_audio_path = temp_audio.name
            temp_audio.close()
            
            # 使用moviepy提取音频
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
            
            video.close()
            audio.close()
            
            logger.info("音频提取完成")
            return temp_audio_path
        except Exception as e:
            logger.error(f"音频提取失败: {e}")
            raise
    
    def transcribe_audio(self, audio_path: str) -> Dict:
        """
        转录音频为文字
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            转录结果字典
        """
        try:
            logger.info("正在进行语音识别...")
            
            # 使用faster-whisper进行转录
            segments, info = self.model.transcribe(audio_path, beam_size=5)
            
            # 转换为兼容格式
            result_segments = []
            full_text = []
            
            for segment in segments:
                segment_dict = {
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text
                }
                result_segments.append(segment_dict)
                full_text.append(segment.text)
            
            result = {
                'language': info.language,
                'segments': result_segments,
                'text': ' '.join(full_text)
            }
            
            logger.info(f"识别到的语言: {result['language']}")
            return result
        except Exception as e:
            logger.error(f"语音识别失败: {e}")
            raise
    
    def detect_language(self, text: str) -> str:
        """
        检测文本语言
        
        Args:
            text: 要检测的文本
            
        Returns:
            语言代码
        """
        try:
            # 使用langdetect作为备选检测
            detected = detect(text)
            logger.info(f"检测到的语言: {detected}")
            return detected
        except Exception as e:
            logger.warning(f"语言检测失败: {e}")
            return "unknown"
    
    def create_srt_subtitles(self, segments: List[Dict], language: str = "") -> str:
        """
        创建SRT格式字幕
        
        Args:
            segments: 语音识别的段落列表
            language: 语言标识
            
        Returns:
            SRT格式字幕字符串
        """
        subtitles = []
        
        for i, segment in enumerate(segments, 1):
            start_time = timedelta(seconds=segment['start'])
            end_time = timedelta(seconds=segment['end'])
            text = segment['text'].strip()
            
            subtitle = srt.Subtitle(
                index=i,
                start=start_time,
                end=end_time,
                content=text
            )
            subtitles.append(subtitle)
        
        return srt.compose(subtitles)
    
    def create_bilingual_srt(self, original_segments: List[Dict], 
                           translated_segments: List[str], 
                           original_lang: str = "", 
                           target_lang: str = "") -> str:
        """
        创建双语SRT字幕
        
        Args:
            original_segments: 原始语言段落
            translated_segments: 翻译后的段落
            original_lang: 原始语言
            target_lang: 目标语言
            
        Returns:
            双语SRT字幕字符串
        """
        subtitles = []
        
        for i, (segment, translation) in enumerate(zip(original_segments, translated_segments), 1):
            start_time = timedelta(seconds=segment['start'])
            end_time = timedelta(seconds=segment['end'])
            
            original_text = segment['text'].strip()
            translated_text = translation.strip()
            
            # 创建双语内容
            bilingual_content = f"{original_text}\n{translated_text}"
            
            subtitle = srt.Subtitle(
                index=i,
                start=start_time,
                end=end_time,
                content=bilingual_content
            )
            subtitles.append(subtitle)
        
        return srt.compose(subtitles)
    
    def save_subtitles(self, subtitles: str, output_path: str):
        """
        保存字幕文件
        
        Args:
            subtitles: 字幕内容
            output_path: 输出文件路径
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(subtitles)
            logger.info(f"字幕已保存到: {output_path}")
        except Exception as e:
            logger.error(f"字幕保存失败: {e}")
            raise
    
    def process_video(self, video_path: str, output_dir: str = None) -> Dict:
        """
        处理视频生成字幕
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录
            
        Returns:
            处理结果字典
        """
        if output_dir is None:
            output_dir = os.path.dirname(video_path)
        
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        
        try:
            # 提取音频
            audio_path = self.extract_audio(video_path)
            
            try:
                # 语音识别
                result = self.transcribe_audio(audio_path)
                
                # 获取语言信息
                detected_language = result.get('language', 'unknown')
                segments = result.get('segments', [])
                
                if not segments:
                    raise ValueError("未能识别到任何语音内容")
                
                # 创建原始语言字幕
                original_srt = self.create_srt_subtitles(segments, detected_language)
                original_srt_path = os.path.join(output_dir, f"{video_name}_{detected_language}.srt")
                self.save_subtitles(original_srt, original_srt_path)
                
                return {
                    'success': True,
                    'detected_language': detected_language,
                    'segments': segments,
                    'original_srt_path': original_srt_path,
                    'original_srt_content': original_srt,
                    'text_content': result.get('text', '')
                }
                
            finally:
                # 清理临时音频文件
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
                    
        except Exception as e:
            logger.error(f"视频处理失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'model'):
            del self.model 