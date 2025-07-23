#!/usr/bin/env python3
"""
CaptionFlow - 视频双语字幕自动生成器
支持自动语音识别、语言检测、翻译和双语字幕生成
"""

import argparse
import os
import sys
from pathlib import Path
import logging
from caption_generator import CaptionGenerator
from translator import Translator
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_argument_parser():
    """设置命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="CaptionFlow - 视频双语字幕自动生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py -i video.mp4                              # 基本使用
  python main.py -i video.mp4 -o output/                  # 指定输出目录
  python main.py -i video.mp4 -m large-v2 -t openai      # 使用大模型和OpenAI翻译
  python main.py -i video.mp4 -t google                   # 使用Google翻译（推荐）
  python main.py -i video.mp4 -t simple                   # 使用简单翻译（最稳定）
  python main.py -i video.mp4 --bilingual                 # 生成双语字幕
  python main.py -i video.mp4 --no-translate              # 只生成原语言字幕
        """
    )
    
    # 必需参数
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="输入视频文件路径"
    )
    
    # 可选参数
    parser.add_argument(
        "-o", "--output",
        help="输出目录路径（默认为视频文件所在目录）"
    )
    
    parser.add_argument(
        "-m", "--model",
        choices=["tiny", "base", "small", "medium", "large-v2"],
        default="base",
        help="Whisper模型大小（默认: base）"
    )
    
    parser.add_argument(
        "-t", "--translator",
        choices=["simple", "google", "libre", "openai"],
        default="simple",
        help="翻译服务（默认: simple，离线可用）"
    )
    
    parser.add_argument(
        "--bilingual",
        action="store_true",
        help="生成双语字幕文件"
    )
    
    parser.add_argument(
        "--no-translate",
        action="store_true",
        help="不进行翻译，只生成原语言字幕"
    )
    
    parser.add_argument(
        "--target-lang",
        help="目标翻译语言（默认自动检测：中英互译）"
    )
    
    parser.add_argument(
        "--api-key",
        help="OpenAI API密钥（使用OpenAI翻译时需要）"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出"
    )
    
    return parser

def validate_input_file(file_path: str) -> bool:
    """验证输入文件"""
    if not os.path.exists(file_path):
        logger.error(f"输入文件不存在: {file_path}")
        return False
    
    # 检查文件扩展名
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.m4v'}
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext not in video_extensions:
        logger.warning(f"文件扩展名 {file_ext} 可能不是支持的视频格式")
    
    return True

def create_output_directory(output_dir: str) -> bool:
    """创建输出目录"""
    try:
        os.makedirs(output_dir, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建输出目录失败: {e}")
        return False

def main():
    """主函数"""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 验证输入文件
    if not validate_input_file(args.input):
        sys.exit(1)
    
    # 设置输出目录
    if args.output:
        output_dir = args.output
    else:
        output_dir = os.path.dirname(os.path.abspath(args.input))
    
    if not create_output_directory(output_dir):
        sys.exit(1)
    
    video_name = os.path.splitext(os.path.basename(args.input))[0]
    
    try:
        # 初始化字幕生成器
        logger.info("初始化字幕生成器...")
        caption_generator = CaptionGenerator(model_size=args.model)
        
        # 处理视频
        logger.info(f"开始处理视频: {args.input}")
        result = caption_generator.process_video(args.input, output_dir)
        
        if not result['success']:
            logger.error(f"视频处理失败: {result['error']}")
            sys.exit(1)
        
        detected_language = result['detected_language']
        segments = result['segments']
        original_srt_path = result['original_srt_path']
        
        logger.info(f"语音识别完成，检测到语言: {detected_language}")
        logger.info(f"原始字幕已保存: {original_srt_path}")
        
        # 如果不需要翻译，直接退出
        if args.no_translate:
            logger.info("跳过翻译，处理完成")
            print(f"\n✅ 字幕生成完成!")
            print(f"📄 原始字幕: {original_srt_path}")
            return
        
        # 初始化翻译器
        logger.info("初始化翻译器...")
        try:
            translator = Translator(service=args.translator, api_key=args.api_key)
        except Exception as e:
            logger.error(f"翻译器初始化失败: {e}")
            if args.translator == "openai":
                logger.info("提示: 使用OpenAI翻译需要设置API密钥")
            sys.exit(1)
        
        # 确定目标语言
        target_language = args.target_lang or translator.detect_target_language(detected_language)
        target_lang_name = translator.get_language_name(target_language)
        
        logger.info(f"开始翻译到: {target_lang_name}")
        
        # 翻译字幕
        translations = translator.translate_segments(
            segments, 
            target_language=target_language,
            source_language=detected_language
        )
        
        # 创建翻译后的字幕
        translated_srt = caption_generator.create_srt_subtitles(
            [{'start': seg['start'], 'end': seg['end'], 'text': trans} 
             for seg, trans in zip(segments, translations)],
            target_language
        )
        
        # 保存翻译字幕
        translated_srt_path = os.path.join(output_dir, f"{video_name}_{target_language}.srt")
        caption_generator.save_subtitles(translated_srt, translated_srt_path)
        
        logger.info(f"翻译字幕已保存: {translated_srt_path}")
        
        # 如果需要生成双语字幕
        if args.bilingual:
            logger.info("生成双语字幕...")
            bilingual_srt = caption_generator.create_bilingual_srt(
                segments, 
                translations,
                detected_language,
                target_language
            )
            
            # 保存双语字幕
            bilingual_srt_path = os.path.join(output_dir, f"{video_name}_bilingual.srt")
            caption_generator.save_subtitles(bilingual_srt, bilingual_srt_path)
            
            logger.info(f"双语字幕已保存: {bilingual_srt_path}")
        
        # 生成处理报告
        report = {
            "video_file": args.input,
            "detected_language": detected_language,
            "target_language": target_language,
            "model_used": args.model,
            "translator_used": args.translator,
            "segments_count": len(segments),
            "files_generated": {
                "original": original_srt_path,
                "translated": translated_srt_path,
            }
        }
        
        if args.bilingual:
            report["files_generated"]["bilingual"] = bilingual_srt_path
        
        # 保存报告
        report_path = os.path.join(output_dir, f"{video_name}_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 输出结果
        print(f"\n✅ 双语字幕生成完成!")
        print(f"🎯 检测语言: {translator.get_language_name(detected_language)}")
        print(f"🔄 翻译语言: {target_lang_name}")
        print(f"📊 字幕段落: {len(segments)} 段")
        print(f"\n📄 生成的文件:")
        print(f"  - 原始字幕: {original_srt_path}")
        print(f"  - 翻译字幕: {translated_srt_path}")
        if args.bilingual:
            print(f"  - 双语字幕: {bilingual_srt_path}")
        print(f"  - 处理报告: {report_path}")
        
    except KeyboardInterrupt:
        logger.info("用户中断处理")
        sys.exit(1)
    except Exception as e:
        logger.error(f"处理过程中发生错误: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # 清理资源
        if 'caption_generator' in locals():
            caption_generator.cleanup()

if __name__ == "__main__":
    main() 