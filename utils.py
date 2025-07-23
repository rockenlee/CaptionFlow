"""
工具函数模块
包含文件处理、格式转换、时间处理等辅助功能
"""

import os
import re
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
from datetime import timedelta
import srt

logger = logging.getLogger(__name__)

def format_time(seconds: float) -> str:
    """
    将秒数格式化为时间字符串
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化的时间字符串 (HH:MM:SS)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def parse_srt_time(time_str: str) -> float:
    """
    解析SRT时间字符串为秒数
    
    Args:
        time_str: SRT时间字符串 (HH:MM:SS,mmm)
        
    Returns:
        秒数
    """
    try:
        # 移除毫秒部分
        time_part = time_str.split(',')[0]
        hours, minutes, seconds = map(int, time_part.split(':'))
        return hours * 3600 + minutes * 60 + seconds
    except Exception as e:
        logger.error(f"时间解析失败: {e}")
        return 0.0

def validate_video_file(file_path: str) -> bool:
    """
    验证视频文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否为有效的视频文件
    """
    if not os.path.exists(file_path):
        return False
    
    video_extensions = {
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', 
        '.flv', '.webm', '.m4v', '.3gp', '.asf'
    }
    
    file_ext = Path(file_path).suffix.lower()
    return file_ext in video_extensions

def get_file_size_mb(file_path: str) -> float:
    """
    获取文件大小（MB）
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件大小（MB）
    """
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0

def create_safe_filename(filename: str) -> str:
    """
    创建安全的文件名（移除特殊字符）
    
    Args:
        filename: 原始文件名
        
    Returns:
        安全的文件名
    """
    # 移除或替换不安全的字符
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    safe_name = re.sub(r'_+', '_', safe_name)  # 合并多个下划线
    return safe_name.strip('_')

def split_text_by_length(text: str, max_length: int = 80) -> List[str]:
    """
    按长度分割文本（用于字幕换行）
    
    Args:
        text: 要分割的文本
        max_length: 最大长度
        
    Returns:
        分割后的文本列表
    """
    if len(text) <= max_length:
        return [text]
    
    # 尝试在单词边界分割
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        if len(current_line + " " + word) <= max_length:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines

def merge_subtitle_lines(lines: List[str], max_lines: int = 2) -> str:
    """
    合并字幕行
    
    Args:
        lines: 字幕行列表
        max_lines: 最大行数
        
    Returns:
        合并后的字幕文本
    """
    if len(lines) <= max_lines:
        return '\n'.join(lines)
    
    # 如果超过最大行数，合并为指定行数
    merged_lines = []
    chars_per_line = sum(len(line) for line in lines) // max_lines
    
    current_line = ""
    for line in lines:
        if len(current_line + " " + line) <= chars_per_line * 1.2:  # 允许20%的弹性
            if current_line:
                current_line += " " + line
            else:
                current_line = line
        else:
            if current_line:
                merged_lines.append(current_line)
            current_line = line
            
            if len(merged_lines) >= max_lines - 1:
                break
    
    if current_line:
        merged_lines.append(current_line)
    
    return '\n'.join(merged_lines[:max_lines])

def validate_srt_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    验证SRT文件格式
    
    Args:
        file_path: SRT文件路径
        
    Returns:
        (是否有效, 错误信息)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 尝试解析SRT内容
        subtitles = list(srt.parse(content))
        
        if not subtitles:
            return False, "SRT文件为空或格式错误"
        
        # 检查时间顺序
        for i in range(1, len(subtitles)):
            if subtitles[i].start < subtitles[i-1].end:
                return False, f"字幕时间重叠: 第{i}段和第{i+1}段"
        
        return True, None
        
    except Exception as e:
        return False, f"SRT文件验证失败: {str(e)}"

def convert_to_vtt(srt_content: str) -> str:
    """
    将SRT内容转换为VTT格式
    
    Args:
        srt_content: SRT格式内容
        
    Returns:
        VTT格式内容
    """
    try:
        subtitles = list(srt.parse(srt_content))
        
        vtt_lines = ["WEBVTT", ""]
        
        for subtitle in subtitles:
            start = str(subtitle.start).replace(',', '.')
            end = str(subtitle.end).replace(',', '.')
            
            # 添加毫秒格式
            if '.' not in start:
                start += '.000'
            if '.' not in end:
                end += '.000'
            
            vtt_lines.append(f"{start} --> {end}")
            vtt_lines.append(subtitle.content)
            vtt_lines.append("")
        
        return '\n'.join(vtt_lines)
        
    except Exception as e:
        logger.error(f"VTT转换失败: {e}")
        return ""

def clean_subtitle_text(text: str) -> str:
    """
    清理字幕文本（移除多余空格、特殊字符等）
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    # 移除多余的空格和换行
    text = re.sub(r'\s+', ' ', text.strip())
    
    # 移除一些常见的语音识别错误
    text = re.sub(r'\b(um|uh|er|ah)\b', '', text, flags=re.IGNORECASE)
    
    # 清理标点符号
    text = re.sub(r'[,，]\s*[,，]+', ',', text)  # 多个逗号
    text = re.sub(r'[.。]\s*[.。]+', '.', text)  # 多个句号
    
    return text.strip()

def estimate_reading_time(text: str, wpm: int = 200) -> float:
    """
    估算文本阅读时间
    
    Args:
        text: 文本内容
        wpm: 每分钟阅读单词数
        
    Returns:
        估算的阅读时间（秒）
    """
    # 简单的单词计数（对中文字符每个字算作一个单词）
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    
    total_words = chinese_chars + english_words
    return (total_words / wpm) * 60

def adjust_subtitle_timing(segments: List[Dict], min_duration: float = 1.0, 
                          max_duration: float = 7.0) -> List[Dict]:
    """
    调整字幕时间
    
    Args:
        segments: 字幕段落列表
        min_duration: 最小持续时间
        max_duration: 最大持续时间
        
    Returns:
        调整后的段落列表
    """
    adjusted_segments = []
    
    for i, segment in enumerate(segments):
        start = segment['start']
        end = segment['end']
        text = segment['text']
        
        # 计算当前持续时间
        duration = end - start
        
        # 估算理想持续时间
        ideal_duration = max(min_duration, estimate_reading_time(text))
        ideal_duration = min(ideal_duration, max_duration)
        
        # 调整时间
        if duration < min_duration:
            # 扩展结束时间
            new_end = start + ideal_duration
            # 确保不与下一个段落重叠
            if i + 1 < len(segments):
                next_start = segments[i + 1]['start']
                new_end = min(new_end, next_start - 0.1)
            end = new_end
        elif duration > max_duration:
            # 缩短持续时间
            end = start + ideal_duration
        
        adjusted_segments.append({
            'start': start,
            'end': end,
            'text': text
        })
    
    return adjusted_segments

def export_to_json(data: Dict, output_path: str) -> bool:
    """
    导出数据到JSON文件
    
    Args:
        data: 要导出的数据
        output_path: 输出文件路径
        
    Returns:
        是否成功
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"JSON导出失败: {e}")
        return False

def load_from_json(file_path: str) -> Optional[Dict]:
    """
    从JSON文件加载数据
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        加载的数据或None
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"JSON加载失败: {e}")
        return None 