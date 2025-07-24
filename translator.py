import openai
import logging
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import time
import requests
import json
from deep_translator import GoogleTranslator
try:
    from translate import Translator as TranslateLibTranslator
    TRANSLATE_LIB_AVAILABLE = True
except ImportError:
    TRANSLATE_LIB_AVAILABLE = False

load_dotenv()
logger = logging.getLogger(__name__)

class Translator:
    def __init__(self, service: str = "simple", api_key: Optional[str] = None):
        """
        初始化翻译器
        
        Args:
            service: 翻译服务 ("google", "openai", "libre" 或 "simple")
            api_key: API密钥 (仅OpenAI需要)
        """
        self.service = service.lower()
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        # 初始化简单翻译字典（作为所有服务的备选）
        self._init_simple_dict()
        
        if self.service == "openai":
            self._init_openai()
        elif self.service == "libre":
            self._init_libre()
        elif self.service == "simple":
            self._init_simple()
        elif self.service == "google":
            self._init_google()
        else:
            raise ValueError(f"不支持的翻译服务: {service}，支持的服务: google, openai, libre, simple")
    
    def _init_openai(self):
        """初始化OpenAI客户端"""
        if not self.api_key:
            raise ValueError("使用OpenAI翻译需要提供API密钥")
        
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
        logger.info("OpenAI翻译服务初始化完成")
    
    def _init_google(self):
        """初始化Google翻译客户端"""
        # Google翻译语言代码映射
        self.google_lang_map = {
            'zh': 'zh-CN',
            'zh-cn': 'zh-CN', 
            'zh-CN': 'zh-CN',
            'zh-tw': 'zh-TW',
            'zh-TW': 'zh-TW',
            'en': 'en',
            'english': 'en',
            'chinese': 'zh-CN',
            'ja': 'ja',
            'ko': 'ko',
            'fr': 'fr',
            'de': 'de',
            'es': 'es',
            'ru': 'ru'
        }
        logger.info("Google翻译服务初始化完成")
    
    def _init_libre(self):
        """初始化LibreTranslate客户端"""
        # 多个LibreTranslate服务器，按优先级排序
        self.libre_urls = [
            "https://translate.astian.org/translate",  # Astian提供的LibreTranslate
            "https://libretranslate.com/translate",    # 官方付费版
            "https://translate.terraprint.co/translate", # 第三方服务
            "https://libretranslate.de/translate",     # 原始的德国服务器
        ]
        self.current_libre_url = None
        self._test_libre_servers()
    
    def _init_simple_dict(self):
        """初始化简单翻译字典（所有服务的备选）"""
        # 扩展的本地翻译字典
        self.simple_dict = {
            # 基础问候语
            'hello': '你好',
            'hi': '嗨',
            'thank you': '谢谢',
            'thanks': '谢谢',
            'goodbye': '再见',
            'bye': '再见',
            'yes': '是',
            'no': '不',
            'please': '请',
            'sorry': '对不起',
            'excuse me': '不好意思',
            'welcome': '欢迎',
            'good morning': '早上好',
            'good evening': '晚上好',
            'good night': '晚安',
            
            # 常用词汇
            'the': '这个',
            'this': '这个',
            'that': '那个',
            'is': '是',
            'are': '是',
            'was': '是',
            'were': '是',
            'will': '将',
            'would': '会',
            'can': '可以',
            'could': '能够',
            'should': '应该',
            'must': '必须',
            'have': '有',
            'has': '有',
            'had': '有',
            'do': '做',
            'does': '做',
            'did': '做',
            'get': '得到',
            'go': '去',
            'come': '来',
            'see': '看',
            'know': '知道',
            'think': '认为',
            'say': '说',
            'tell': '告诉',
            'make': '制作',
            'take': '拿',
            'give': '给',
            'want': '想要',
            'need': '需要',
            'like': '喜欢',
            'love': '爱',
            'feel': '感觉',
            'look': '看',
            'find': '找到',
            'work': '工作',
            'play': '玩',
            'study': '学习',
            'learn': '学习',
            'teach': '教',
            'help': '帮助',
            'use': '使用',
            'try': '尝试',
            'start': '开始',
            'stop': '停止',
            'end': '结束',
            'open': '打开',
            'close': '关闭',
            'read': '读',
            'write': '写',
            'listen': '听',
            'speak': '说',
            'eat': '吃',
            'drink': '喝',
            'sleep': '睡觉',
            'walk': '走',
            'run': '跑',
            'sit': '坐',
            'stand': '站',
            'buy': '买',
            'sell': '卖',
            'pay': '付款',
            'cost': '花费',
            'price': '价格',
            'money': '钱',
            
            # 时间相关
            'today': '今天',
            'tomorrow': '明天',
            'yesterday': '昨天',
            'now': '现在',
            'then': '然后',
            'time': '时间',
            'day': '天',
            'week': '周',
            'month': '月',
            'year': '年',
            'hour': '小时',
            'minute': '分钟',
            'second': '秒',
            'morning': '早上',
            'afternoon': '下午',
            'evening': '晚上',
            'night': '夜晚',
            
            # 地点相关
            'here': '这里',
            'there': '那里',
            'where': '哪里',
            'home': '家',
            'school': '学校',
            'office': '办公室',
            'store': '商店',
            'restaurant': '餐厅',
            'hotel': '酒店',
            'hospital': '医院',
            'bank': '银行',
            'city': '城市',
            'country': '国家',
            'world': '世界',
            
            # 人物相关
            'i': '我',
            'you': '你',
            'he': '他',
            'she': '她',
            'we': '我们',
            'they': '他们',
            'people': '人们',
            'person': '人',
            'man': '男人',
            'woman': '女人',
            'boy': '男孩',
            'girl': '女孩',
            'friend': '朋友',
            'family': '家庭',
            'teacher': '老师',
            'student': '学生',
            'doctor': '医生',
            'nurse': '护士',
            'driver': '司机',
            'worker': '工人',
            
            # 情感相关
            'happy': '高兴',
            'sad': '悲伤',
            'angry': '生气',
            'tired': '累',
            'excited': '兴奋',
            'worried': '担心',
            'surprised': '惊讶',
            'afraid': '害怕',
            'good': '好',
            'bad': '坏',
            'great': '很棒',
            'wonderful': '精彩',
            'terrible': '糟糕',
            'beautiful': '美丽',
            'ugly': '丑陋',
            'interesting': '有趣',
            'boring': '无聊',
            'easy': '容易',
            'difficult': '困难',
            'hard': '困难',
            'simple': '简单',
            'complex': '复杂',
            'important': '重要',
            'useful': '有用',
            'helpful': '有帮助',
            
            # 数字和量词
            'one': '一',
            'two': '二',
            'three': '三',
            'four': '四',
            'five': '五',
            'six': '六',
            'seven': '七',
            'eight': '八',
            'nine': '九',
            'ten': '十',
            'first': '第一',
            'second': '第二',
            'third': '第三',
            'last': '最后',
            'many': '许多',
            'much': '许多',
            'some': '一些',
            'few': '一些',
            'little': '一点',
            'all': '所有',
            'every': '每个',
            'each': '每个',
            'both': '两个',
            'none': '没有',
            
            # 常用短语
            'how are you': '你好吗',
            'what is your name': '你叫什么名字',
            'nice to meet you': '很高兴见到你',
            'see you later': '回头见',
            'have a good day': '祝你有美好的一天',
            'excuse me': '不好意思',
            'i am sorry': '我很抱歉',
            'you are welcome': '不客气',
            'how much': '多少钱',
            'what time': '什么时间',
            'where is': '在哪里',
            'how to': '如何',
            'i don\'t know': '我不知道',
            'i understand': '我明白',
            'i don\'t understand': '我不明白',
            'can you help me': '你能帮助我吗',
            'of course': '当然',
            'no problem': '没问题'
        }
    
    def _init_simple(self):
        """初始化简单翻译器"""
        # simple_dict已在_init_simple_dict中初始化
        logger.info("简单翻译服务初始化完成")
    
    def _test_libre_servers(self):
        """测试LibreTranslate服务器可用性"""
        for url in self.libre_urls:
            try:
                test_payload = {
                    'q': 'test',
                    'source': 'en',
                    'target': 'zh',
                    'format': 'text'
                }
                
                response = requests.post(
                    url, 
                    json=test_payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=5
                )
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if 'translatedText' in result:
                            self.current_libre_url = url
                            logger.info(f"LibreTranslate服务初始化完成: {url}")
                            return
                    except json.JSONDecodeError:
                        continue
                        
            except Exception as e:
                logger.debug(f"LibreTranslate服务器 {url} 不可用: {e}")
                continue
        
        logger.warning("所有LibreTranslate服务器都不可用，将使用简单翻译作为备选")
        self.current_libre_url = None
    
    def detect_target_language(self, source_language: str) -> str:
        """
        根据源语言确定目标翻译语言
        
        Args:
            source_language: 源语言代码
            
        Returns:
            目标语言代码
        """
        # 中英互译逻辑
        if source_language.startswith('zh') or source_language == 'chinese':
            return 'en'  # 中文翻译成英文
        elif source_language.startswith('en') or source_language == 'english':
            return 'zh'  # 英文翻译成中文
        else:
            # 其他语言默认翻译成中文
            return 'zh'
    
    def _map_language_code(self, lang_code: str, service: str = None) -> str:
        """
        将语言代码映射到特定服务的格式
        
        Args:
            lang_code: 原始语言代码
            service: 目标服务 (如果不指定，使用当前服务)
            
        Returns:
            映射后的语言代码
        """
        if service is None:
            service = self.service
            
        # 标准化输入
        lang_code = lang_code.lower().strip()
        
        if service == "google":
            return self.google_lang_map.get(lang_code, lang_code)
        elif service == "libre":
            # LibreTranslate使用简单的代码
            if lang_code.startswith('zh'):
                return 'zh'
            elif lang_code.startswith('en'):
                return 'en'
            else:
                return lang_code
        else:
            return lang_code
    
    def translate_text_google(self, text: str, target_language: str, source_language: str = "") -> str:
        """
        使用Google翻译文本
        
        Args:
            text: 要翻译的文本
            target_language: 目标语言
            source_language: 源语言
            
        Returns:
            翻译后的文本
        """
        try:
            # 映射语言代码
            source_lang = self._map_language_code(source_language, "google") if source_language else 'auto'
            target_lang = self._map_language_code(target_language, "google")
            
            # 如果目标语言是'zh'，映射为'zh-CN'
            if target_lang == 'zh':
                target_lang = 'zh-CN'
            
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            result = translator.translate(text)
            return result
            
        except Exception as e:
            logger.error(f"Google翻译失败: {e}")
            # 如果Google翻译失败，使用简单翻译作为备选
            return self.translate_text_simple(text, target_language, source_language)
    
    def translate_text_openai(self, text: str, target_language: str, source_language: str = "") -> str:
        """
        使用OpenAI翻译文本
        
        Args:
            text: 要翻译的文本
            target_language: 目标语言
            source_language: 源语言
            
        Returns:
            翻译后的文本
        """
        try:
            # 构建提示词
            if target_language == 'zh' or target_language.startswith('zh'):
                target_lang_name = "中文"
            elif target_language == 'en':
                target_lang_name = "英文"
            else:
                target_lang_name = target_language
            
            prompt = f"请将以下文本翻译成{target_lang_name}，保持原意和语调，不要添加额外的解释:\n\n{text}"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的翻译助手，能够准确地在中英文之间进行翻译。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            translation = response.choices[0].message.content.strip()
            return translation
            
        except Exception as e:
            logger.error(f"OpenAI翻译失败: {e}")
            raise
    
    def translate_text_libre(self, text: str, target_language: str, source_language: str = "") -> str:
        """
        使用LibreTranslate翻译文本
        
        Args:
            text: 要翻译的文本
            target_language: 目标语言
            source_language: 源语言
            
        Returns:
            翻译后的文本
        """
        if not self.current_libre_url:
            # 如果没有可用的LibreTranslate服务器，使用Google翻译
            return self.translate_text_google(text, target_language, source_language)
        
        try:
            # LibreTranslate语言代码映射
            source_lang = self._map_language_code(source_language, "libre") if source_language else 'auto'
            target_lang = self._map_language_code(target_language, "libre")
            
            payload = {
                'q': text,
                'source': source_lang,
                'target': target_lang,
                'format': 'text'
            }
            
            response = requests.post(
                self.current_libre_url, 
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    return result.get('translatedText', text)
                except json.JSONDecodeError as e:
                    logger.error(f"LibreTranslate JSON解析失败: {e}, 响应内容: {response.text[:200]}")
                    # 尝试下一个服务器
                    self._switch_libre_server()
                    if self.current_libre_url:
                        return self.translate_text_libre(text, target_language, source_language)
                    else:
                        return self.translate_text_google(text, target_language, source_language)
            else:
                logger.error(f"LibreTranslate API错误: {response.status_code}, 响应: {response.text[:200]}")
                # 尝试下一个服务器
                self._switch_libre_server()
                if self.current_libre_url:
                    return self.translate_text_libre(text, target_language, source_language)
                else:
                    return self.translate_text_google(text, target_language, source_language)
                
        except Exception as e:
            logger.error(f"LibreTranslate翻译失败: {e}")
            # 使用Google翻译作为备选
            return self.translate_text_google(text, target_language, source_language)
    
    def _switch_libre_server(self):
        """切换到下一个LibreTranslate服务器"""
        if not self.current_libre_url or not self.libre_urls:
            self.current_libre_url = None
            return
        
        try:
            current_index = self.libre_urls.index(self.current_libre_url)
            next_index = (current_index + 1) % len(self.libre_urls)
            
            # 尝试下一个服务器
            for i in range(len(self.libre_urls) - 1):
                test_index = (next_index + i) % len(self.libre_urls)
                url = self.libre_urls[test_index]
                
                try:
                    test_payload = {
                        'q': 'test',
                        'source': 'en',
                        'target': 'zh',
                        'format': 'text'
                    }
                    
                    response = requests.post(
                        url, 
                        json=test_payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        try:
                            result = response.json()
                            if 'translatedText' in result:
                                self.current_libre_url = url
                                logger.info(f"切换到LibreTranslate服务器: {url}")
                                return
                        except json.JSONDecodeError:
                            continue
                            
                except Exception:
                    continue
            
            # 所有服务器都不可用
            self.current_libre_url = None
            logger.warning("所有LibreTranslate服务器都不可用")
            
        except ValueError:
            self.current_libre_url = None
    
    def translate_text_simple(self, text: str, target_language: str, source_language: str = "") -> str:
        """
        增强Simple翻译（Microsoft Translator API + 本地词典备用）
        免费配额：200万字符/月
        
        Args:
            text: 要翻译的文本
            target_language: 目标语言
            source_language: 源语言
            
        Returns:
            翻译后的文本
        """
        if not text.strip():
            return text
        
        try:
            # 1. 初始化增强翻译器（懒加载）
            if not hasattr(self, '_enhanced_translator'):
                from translator_enhanced import MicrosoftTranslatorEnhanced
                self._enhanced_translator = MicrosoftTranslatorEnhanced()
                logger.info("Microsoft Translator增强版翻译器已加载")
            
            # 2. 使用增强版翻译器
            result = self._enhanced_translator.translate_text(text, target_language, source_language)
            
            # 3. 记录翻译统计（如果可用）
            if hasattr(self._enhanced_translator, 'get_performance_stats'):
                stats = self._enhanced_translator.get_performance_stats()
                if stats['total_translations'] % 50 == 0:  # 每50次翻译记录一次统计
                    logger.info(f"翻译统计: {stats}")
            
            return result
            
        except ImportError:
            logger.warning("无法导入增强翻译器，使用本地回退方案")
            return self._translate_text_simple_fallback(text, target_language, source_language)
        except Exception as e:
            logger.error(f"增强Simple翻译失败: {e}，使用本地回退方案")
            return self._translate_text_simple_fallback(text, target_language, source_language)
    
    def _translate_text_simple_fallback(self, text: str, target_language: str, source_language: str = "") -> str:
        """
        本地回退翻译（完全离线，无API调用）
        """
        text_clean = text.strip()
        text_lower = text_clean.lower()
        
        # 1. 优先查找完整短语
        if text_lower in self.simple_dict:
            return self.simple_dict[text_lower]
        
        # 2. 查找常见句型模式（本地规则）
        translated_sentence = self._translate_by_patterns(text_clean, target_language)
        if translated_sentence != text_clean:
            return translated_sentence
        
        # 3. 单词级别翻译（处理句子）
        words = text_clean.split()
        translated_words = []
        has_translation = False
        
        for word in words:
            # 移除标点符号进行查找
            clean_word = word.lower().strip('.,!?;:"()[]{}')
            if clean_word in self.simple_dict:
                # 保持原始的大小写和标点
                translated = self.simple_dict[clean_word]
                # 保留原始标点符号
                punctuation = ''.join(c for c in word if c in '.,!?;:"()[]{}')
                translated_words.append(translated + punctuation)
                has_translation = True
            else:
                translated_words.append(word)
        
        if has_translation:
            return " ".join(translated_words)
        
        # 4. 如果没有匹配，使用模式标记（完全本地）
        if target_language in ['zh', 'zh-CN']:
            return f"[本地中译] {text_clean}"
        elif target_language == 'en':
            return f"[Local EN] {text_clean}"
        else:
            return f"[{target_language}] {text_clean}"
    
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
            'how do you do': '你好',
            'nice to meet you': '很高兴见到你',
            'good morning': '早上好',
            'good afternoon': '下午好',
            'good evening': '晚上好',
            'good night': '晚安',
            
            # 感谢和道歉
            'thank you very much': '非常感谢',
            'thanks a lot': '非常感谢',
            'i am sorry': '对不起',
            'excuse me': '打扰一下',
            'you are welcome': '不客气',
            
            # 常见表达
            'i love you': '我爱你',
            'i miss you': '我想你',
            'see you later': '再见',
            'see you soon': '再见',
            'take care': '保重',
            'have a good day': '祝你今天愉快',
            'have a nice day': '祝你今天愉快',
            
            # 疑问句
            'what is your name': '你叫什么名字',
            'what is your name?': '你叫什么名字？',
            'how old are you': '你多大了',
            'how old are you?': '你多大了？',
            'where are you from': '你来自哪里',
            'where are you from?': '你来自哪里？',
            
            # 常见动作
            'i want to go': '我想去',
            'i need help': '我需要帮助',
            'can you help me': '你能帮助我吗',
            'can you help me?': '你能帮助我吗？',
        }
        
        return patterns.get(text_lower, text)
    
    def translate_text(self, text: str, target_language: str = None, source_language: str = "") -> str:
        """
        翻译文本（统一接口）
        
        Args:
            text: 要翻译的文本
            target_language: 目标语言（如果不指定，会自动检测）
            source_language: 源语言
            
        Returns:
            翻译后的文本
        """
        if not text.strip():
            return text
        
        # 如果没有指定目标语言，根据源语言自动确定
        if not target_language:
            target_language = self.detect_target_language(source_language)
        
        if self.service == "google":
            return self.translate_text_google(text, target_language, source_language)
        elif self.service == "openai":
            return self.translate_text_openai(text, target_language, source_language)
        elif self.service == "libre":
            return self.translate_text_libre(text, target_language, source_language)
        elif self.service == "simple":
            return self.translate_text_simple(text, target_language, source_language)
    
    def translate_segments(self, segments: List[Dict], target_language: str = None, 
                         source_language: str = "", batch_size: int = 5) -> List[str]:
        """
        翻译字幕段落列表
        
        Args:
            segments: 字幕段落列表
            target_language: 目标语言
            source_language: 源语言
            batch_size: 批处理大小
            
        Returns:
            翻译后的文本列表
        """
        translations = []
        
        # 如果没有指定目标语言，根据源语言自动确定
        if not target_language:
            target_language = self.detect_target_language(source_language)
        
        logger.info(f"开始翻译 {len(segments)} 个段落，目标语言: {target_language}")
        
        for i, segment in enumerate(segments):
            try:
                text = segment.get('text', '').strip()
                if not text:
                    translations.append("")
                    continue
                
                # 翻译文本
                translation = self.translate_text(text, target_language, source_language)
                translations.append(translation)
                
                # 显示进度
                if (i + 1) % 10 == 0:
                    logger.info(f"翻译进度: {i + 1}/{len(segments)}")
                
                # 如果使用OpenAI，添加短暂延迟避免频率限制
                if self.service == "openai":
                    time.sleep(0.5)
                # 如果使用Google翻译，添加更短的延迟
                elif self.service == "google":
                    time.sleep(0.1)
                # 如果使用LibreTranslate，添加更短的延迟
                elif self.service == "libre":
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"翻译第{i+1}个段落时出错: {e}")
                # 使用原文或标记
                translations.append(f"[翻译失败] {segment.get('text', '')}")
        
        logger.info("翻译完成")
        return translations
    
    def get_language_name(self, language_code: str) -> str:
        """
        获取语言名称
        
        Args:
            language_code: 语言代码
            
        Returns:
            语言名称
        """
        language_map = {
            'zh': '中文',
            'zh-CN': '中文',
            'zh-TW': '繁体中文',
            'en': '英文',
            'english': '英文',
            'chinese': '中文',
            'ja': '日文',
            'ko': '韩文',
            'fr': '法文',
            'de': '德文',
            'es': '西班牙文',
            'ru': '俄文'
        }
        return language_map.get(language_code, language_code) 