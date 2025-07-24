"""
优化版翻译器 - 大幅提升翻译性能
支持并行处理、缓存、批量翻译等性能优化
"""

import openai
import logging
import time
import requests
import json
import hashlib
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import os
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

try:
    from translate import Translator as TranslateLibTranslator
    TRANSLATE_LIB_AVAILABLE = True
except ImportError:
    TRANSLATE_LIB_AVAILABLE = False

# 加载环境变量
load_dotenv()

# 设置日志
logger = logging.getLogger(__name__)

class OptimizedTranslator:
    """优化版翻译器 - 高性能翻译处理"""
    
    def __init__(self, service: str = "simple", api_key: Optional[str] = None, max_workers: int = 10):
        """
        初始化优化版翻译器
        
        Args:
            service: 翻译服务类型
            api_key: API密钥
            max_workers: 最大并行工作线程数
        """
        self.service = service
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.max_workers = max_workers
        
        # 翻译缓存
        self.translation_cache = {}
        
        # 初始化服务
        self._init_service()
        
        # 性能统计
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'total_translations': 0,
            'parallel_batches': 0
        }
    
    def _init_service(self):
        """初始化翻译服务"""
        if self.service == "openai":
            self._init_openai()
        elif self.service == "google":
            self._init_google()
        elif self.service == "libre":
            self._init_libre()
        elif self.service == "simple":
            self._init_simple()
        
        logger.info(f"优化版{self.service}翻译服务初始化完成")
    
    def _init_simple(self):
        """初始化简单翻译"""
        # 扩展词典（只保留最常用的词汇以提高查找速度）
        self.simple_dict = {
            # 核心词汇
            'hello': '你好', 'hi': '嗨', 'thank you': '谢谢', 'thanks': '谢谢',
            'goodbye': '再见', 'bye': '再见', 'yes': '是', 'no': '不',
            'please': '请', 'sorry': '对不起', 'welcome': '欢迎',
            'good': '好', 'bad': '坏', 'great': '很棒', 'nice': '不错',
            'beautiful': '美丽', 'wonderful': '精彩', 'amazing': '惊人',
            
            # 常用动词
            'is': '是', 'are': '是', 'was': '是', 'were': '是',
            'have': '有', 'has': '有', 'had': '有', 'do': '做', 'does': '做', 'did': '做',
            'will': '将', 'would': '会', 'can': '能', 'could': '能',
            'should': '应该', 'must': '必须', 'may': '可能',
            'go': '去', 'come': '来', 'see': '看', 'look': '看',
            'get': '得到', 'take': '拿', 'give': '给', 'make': '做',
            'know': '知道', 'think': '想', 'say': '说', 'tell': '告诉',
            
            # 常用名词
            'time': '时间', 'day': '天', 'week': '周', 'month': '月', 'year': '年',
            'today': '今天', 'tomorrow': '明天', 'yesterday': '昨天',
            'morning': '早上', 'afternoon': '下午', 'evening': '晚上', 'night': '夜晚',
            'water': '水', 'food': '食物', 'money': '钱', 'work': '工作',
            'home': '家', 'school': '学校', 'company': '公司', 'friend': '朋友',
            
            # 代词
            'i': '我', 'you': '你', 'he': '他', 'she': '她', 'it': '它',
            'we': '我们', 'they': '他们', 'this': '这', 'that': '那',
            'these': '这些', 'those': '那些', 'here': '这里', 'there': '那里',
            
            # 数字
            'one': '一', 'two': '二', 'three': '三', 'four': '四', 'five': '五',
            'six': '六', 'seven': '七', 'eight': '八', 'nine': '九', 'ten': '十',
            'first': '第一', 'second': '第二', 'third': '第三', 'last': '最后',
            
            # 形容词
            'big': '大', 'small': '小', 'new': '新', 'old': '老',
            'hot': '热', 'cold': '冷', 'fast': '快', 'slow': '慢',
            'easy': '容易', 'difficult': '困难', 'important': '重要',
            'different': '不同', 'same': '相同', 'right': '对', 'wrong': '错',
            
            # 连词和介词
            'and': '和', 'or': '或', 'but': '但是', 'because': '因为',
            'if': '如果', 'when': '当', 'where': '哪里', 'how': '如何',
            'what': '什么', 'who': '谁', 'why': '为什么', 'which': '哪个',
            'in': '在', 'on': '在', 'at': '在', 'to': '到', 'for': '为了',
            'with': '和', 'from': '从', 'about': '关于', 'like': '像'
        }
    
    def _init_google(self):
        """初始化Google翻译"""
        pass  # GoogleTranslator在使用时初始化
    
    def _init_libre(self):
        """初始化LibreTranslate"""
        self.libre_urls = [
            "https://libretranslate.de/translate",
            "https://translate.argosopentech.com/translate",
            "https://translate.api.skitzen.com/translate"
        ]
    
    def _init_openai(self):
        """初始化OpenAI"""
        if self.api_key:
            openai.api_key = self.api_key
    
    def _get_cache_key(self, text: str, target_lang: str, source_lang: str) -> str:
        """生成缓存键"""
        cache_input = f"{text}|{target_lang}|{source_lang}|{self.service}"
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def translate_text_cached(self, text: str, target_language: str, source_language: str = "") -> str:
        """
        带缓存的文本翻译
        """
        if not text.strip():
            return text
        
        # 检查缓存
        cache_key = self._get_cache_key(text, target_language, source_language)
        if cache_key in self.translation_cache:
            self.stats['cache_hits'] += 1
            return self.translation_cache[cache_key]
        
        # 执行翻译
        self.stats['cache_misses'] += 1
        translation = self._translate_single(text, target_language, source_language)
        
        # 存入缓存
        self.translation_cache[cache_key] = translation
        return translation
    
    def _translate_single(self, text: str, target_language: str, source_language: str = "") -> str:
        """单个文本翻译"""
        if self.service == "simple":
            return self._translate_simple(text, target_language, source_language)
        elif self.service == "google":
            return self._translate_google(text, target_language, source_language)
        elif self.service == "libre":
            return self._translate_libre(text, target_language, source_language)
        elif self.service == "openai":
            return self._translate_openai(text, target_language, source_language)
        else:
            return text
    
    def _translate_simple(self, text: str, target_language: str, source_language: str = "") -> str:
        """增强Simple翻译 - Microsoft Translator API + 本地缓存优化"""
        try:
            # 1. 初始化增强翻译器（懒加载 + 缓存）
            if not hasattr(self, '_enhanced_translator'):
                from translator_enhanced import MicrosoftTranslatorEnhanced
                self._enhanced_translator = MicrosoftTranslatorEnhanced(max_workers=self.max_workers)
                logger.info("Microsoft Translator增强版翻译器已加载（优化版）")
            
            # 2. 使用增强版翻译器
            result = self._enhanced_translator.translate_text(text, target_language, source_language)
            return result
            
        except ImportError:
            logger.warning("无法导入增强翻译器，使用本地优化回退方案")
            return self._translate_simple_optimized_fallback(text, target_language, source_language)
        except Exception as e:
            logger.error(f"增强Simple翻译失败: {e}，使用本地优化回退方案")
            return self._translate_simple_optimized_fallback(text, target_language, source_language)
    
    def _translate_simple_optimized_fallback(self, text: str, target_language: str, source_language: str = "") -> str:
        """本地优化回退翻译（完全离线，性能优化）"""
        text_clean = text.strip()
        text_lower = text_clean.lower()
        
        # 1. 完整短语查找
        if text_lower in self.simple_dict:
            return self.simple_dict[text_lower]
        
        # 2. 查找常见句型模式（本地规则）
        translated_sentence = self._translate_by_patterns(text_clean, target_language)
        if translated_sentence != text_clean:
            return translated_sentence
        
        # 3. 单词级翻译（快速版本）
        words = text_clean.split()
        if len(words) <= 5:  # 只对短句进行单词级翻译
            translated_words = []
            has_translation = False
            
            for word in words:
                clean_word = word.lower().strip('.,!?;:"()[]{}')
                if clean_word in self.simple_dict:
                    translated_words.append(self.simple_dict[clean_word])
                    has_translation = True
                else:
                    translated_words.append(word)
            
            if has_translation:
                return " ".join(translated_words)
        
        # 4. 使用模式翻译（改进版）
        if target_language in ['zh', 'zh-CN']:
            return f"[优化中译] {text_clean}"
        elif target_language == 'en':
            return f"[Opt EN] {text_clean}"
        else:
            return f"[{target_language}] {text_clean}"
    
    def _translate_google(self, text: str, target_language: str, source_language: str = "") -> str:
        """Google翻译"""
        try:
            # 标准化语言代码
            google_target = self._normalize_language_code_for_google(target_language)
            google_source = self._normalize_language_code_for_google(source_language) if source_language else 'auto'
            
            translator = GoogleTranslator(source=google_source, target=google_target)
            result = translator.translate(text)
            return result if result else text
        except Exception as e:
            logger.error(f"Google翻译失败: {text[:50]}... --> {e}")
            return self._translate_simple(text, target_language, source_language)
    
    def _translate_libre(self, text: str, target_language: str, source_language: str = "") -> str:
        """LibreTranslate翻译"""
        for url in self.libre_urls:
            try:
                data = {
                    'q': text,
                    'source': source_language or 'auto',
                    'target': target_language,
                    'format': 'text'
                }
                
                response = requests.post(url, json=data, timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    return result.get('translatedText', text)
            except Exception:
                continue
        
        # 所有服务器都失败，回退到simple翻译
        return self._translate_simple(text, target_language, source_language)
    
    def _translate_openai(self, text: str, target_language: str, source_language: str = "") -> str:
        """OpenAI翻译"""
        try:
            prompt = f"请将以下文本翻译成{self.get_language_name(target_language)}：\n{text}"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI翻译失败: {e}")
            return self._translate_simple(text, target_language, source_language)
    
    def translate_segments_optimized(self, segments: List[Dict], target_language: str = None, 
                                   source_language: str = "", batch_size: int = 20) -> List[str]:
        """
        优化版段落翻译 - 并行处理 + 缓存 + 批量处理
        """
        if not target_language:
            target_language = self.detect_target_language(source_language)
        
        total_segments = len(segments)
        logger.info(f"🚀 开始优化翻译 {total_segments} 个段落，目标语言: {target_language}")
        
        # 准备翻译任务
        tasks = []
        for i, segment in enumerate(segments):
            text = segment.get('text', '').strip()
            if text:
                tasks.append((i, text, target_language, source_language))
        
        translations = [''] * total_segments  # 初始化结果数组
        
        # 并行翻译处理
        if self.service == "simple":
            # Simple翻译使用更多线程，因为没有API限制
            max_workers = min(self.max_workers * 2, 20)
        else:
            # 其他服务使用较少线程避免API限制
            max_workers = min(self.max_workers, 5)
        
        start_time = time.time()
        completed_count = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有翻译任务
            future_to_index = {
                executor.submit(self.translate_text_cached, text, target_lang, source_lang): index
                for index, text, target_lang, source_lang in tasks
            }
            
            # 收集结果
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    translation = future.result()
                    translations[index] = translation
                    completed_count += 1
                    
                    # 显示进度（减少日志频率）
                    if completed_count % 50 == 0 or completed_count == len(tasks):
                        progress = (completed_count / len(tasks)) * 100
                        elapsed = time.time() - start_time
                        rate = completed_count / elapsed if elapsed > 0 else 0
                        logger.info(f"⚡ 翻译进度: {completed_count}/{len(tasks)} ({progress:.1f}%) - 速度: {rate:.1f}/秒")
                        
                except Exception as e:
                    logger.error(f"翻译任务失败 (索引 {index}): {e}")
                    translations[index] = f"[翻译失败] {segments[index].get('text', '')}"
        
        # 填充空白段落
        for i, segment in enumerate(segments):
            if not segment.get('text', '').strip():
                translations[i] = ""
        
        elapsed_time = time.time() - start_time
        logger.info(f"✅ 翻译完成！总耗时: {elapsed_time:.2f}秒, 平均: {elapsed_time/total_segments:.3f}秒/段")
        logger.info(f"📊 缓存统计: 命中 {self.stats['cache_hits']}, 未命中 {self.stats['cache_misses']}")
        
        return translations
    
    def detect_target_language(self, source_language: str) -> str:
        """检测目标语言"""
        if source_language.startswith('zh'):
            return 'en'
        else:
            return 'zh'
    
    def get_language_name(self, language_code: str) -> str:
        """获取语言名称"""
        language_map = {
            'zh': '中文', 'zh-CN': '中文', 'zh-TW': '繁体中文',
            'en': '英文', 'ja': '日文', 'ko': '韩文',
            'fr': '法文', 'de': '德文', 'es': '西班牙文', 'ru': '俄文'
        }
        return language_map.get(language_code, language_code)
    
    def _normalize_language_code_for_google(self, language_code: str) -> str:
        """为Google翻译标准化语言代码"""
        if not language_code:
            return 'auto'
        
        # Google翻译需要的标准语言代码
        google_lang_map = {
            'zh': 'zh-CN',
            'chinese': 'zh-CN',
            'en': 'en', 
            'english': 'en',
            'ja': 'ja',
            'japanese': 'ja', 
            'ko': 'ko',
            'korean': 'ko',
            'fr': 'fr',
            'french': 'fr',
            'de': 'de', 
            'german': 'de',
            'es': 'es',
            'spanish': 'es',
            'ru': 'ru',
            'russian': 'ru'
        }
        
        # 直接返回映射后的语言代码，如果没有映射则返回原值
        return google_lang_map.get(language_code.lower(), language_code)
    
    def _translate_by_patterns(self, text: str, target_language: str) -> str:
        """
        使用本地模式规则翻译常见句型
        """
        if target_language not in ['zh', 'zh-CN']:
            return text
        
        text_lower = text.lower().strip()
        
        # 常见句型模式（完全本地规则）
        patterns = {
            # 问候语
            'how are you': '你好吗',
            'how are you?': '你好吗？',
            'good morning': '早上好',
            'good afternoon': '下午好',
            'good evening': '晚上好',
            'good night': '晚安',
            'nice to meet you': '很高兴见到你',
            
            # 感谢和道歉
            'thank you very much': '非常感谢',
            'thanks a lot': '非常感谢',
            'i am sorry': '对不起',
            'excuse me': '打扰一下',
            'you are welcome': '不客气',
            
            # 常见表达
            'i love you': '我爱你',
            'see you later': '再见',
            'have a good day': '祝你今天愉快',
            'have a nice day': '祝你今天愉快',
            
            # 疑问句
            'what is your name': '你叫什么名字',
            'what is your name?': '你叫什么名字？',
            'how old are you': '你多大了',
            'how old are you?': '你多大了？',
            'where are you from': '你来自哪里',
            'where are you from?': '你来自哪里？',
        }
        
        return patterns.get(text_lower, text)
    
    def clear_cache(self):
        """清空翻译缓存"""
        self.translation_cache.clear()
        self.stats = {
            'cache_hits': 0, 'cache_misses': 0,
            'total_translations': 0, 'parallel_batches': 0
        }
        logger.info("翻译缓存已清空")
    
    def get_performance_stats(self) -> Dict:
        """获取性能统计"""
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        cache_hit_rate = (self.stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
            'cache_size': len(self.translation_cache)
        } 