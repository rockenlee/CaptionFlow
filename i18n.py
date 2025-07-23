"""
CaptionFlow 国际化模块
支持全球十大主要语言的界面翻译

支持的语言：
1. 中文（简体）- zh_CN
2. 英文 - en_US  
3. 西班牙语 - es_ES
4. 阿拉伯语 - ar_SA
5. 印地语 - hi_IN
6. 葡萄牙语 - pt_BR
7. 俄语 - ru_RU
8. 日语 - ja_JP
9. 德语 - de_DE
10. 法语 - fr_FR
"""

import json
import os
from typing import Dict, Any

class I18n:
    def __init__(self, default_language: str = "zh_CN"):
        """
        初始化国际化系统
        
        Args:
            default_language: 默认语言代码
        """
        self.default_language = default_language
        self.current_language = default_language
        self.translations = {}
        self._load_translations()
    
    def _load_translations(self):
        """加载所有语言翻译"""
        self.translations = {
            "zh_CN": self._get_chinese_translations(),
            "en_US": self._get_english_translations(),
            "es_ES": self._get_spanish_translations(),
            "ar_SA": self._get_arabic_translations(),
            "hi_IN": self._get_hindi_translations(),
            "pt_BR": self._get_portuguese_translations(),
            "ru_RU": self._get_russian_translations(),
            "ja_JP": self._get_japanese_translations(),
            "de_DE": self._get_german_translations(),
            "fr_FR": self._get_french_translations()
        }
    
    def set_language(self, language_code: str):
        """设置当前语言"""
        if language_code in self.translations:
            self.current_language = language_code
        else:
            self.current_language = self.default_language
    
    def get_language_name(self, language_code: str) -> str:
        """获取语言名称"""
        language_names = {
            "zh_CN": "中文（简体）",
            "en_US": "English",
            "es_ES": "Español",
            "ar_SA": "العربية",
            "hi_IN": "हिन्दी",
            "pt_BR": "Português",
            "ru_RU": "Русский",
            "ja_JP": "日本語",
            "de_DE": "Deutsch",
            "fr_FR": "Français"
        }
        return language_names.get(language_code, language_code)
    
    def get_available_languages(self) -> Dict[str, str]:
        """获取所有可用语言"""
        return {
            "zh_CN": "中文（简体）",
            "en_US": "English", 
            "es_ES": "Español",
            "ar_SA": "العربية",
            "hi_IN": "हिन्दी",
            "pt_BR": "Português",
            "ru_RU": "Русский",
            "ja_JP": "日本語",
            "de_DE": "Deutsch",
            "fr_FR": "Français"
        }
    
    def t(self, key: str, **kwargs) -> str:
        """
        翻译文本
        
        Args:
            key: 翻译键
            **kwargs: 格式化参数
            
        Returns:
            翻译后的文本
        """
        translation = self._get_nested_value(
            self.translations.get(self.current_language, {}), 
            key
        )
        
        if translation is None:
            # 回退到默认语言
            translation = self._get_nested_value(
                self.translations.get(self.default_language, {}), 
                key
            )
        
        if translation is None:
            # 如果都没有找到，返回键本身
            return key
        
        # 格式化参数
        try:
            return translation.format(**kwargs)
        except:
            return translation
    
    def _get_nested_value(self, data: Dict, key: str) -> Any:
        """获取嵌套字典的值"""
        keys = key.split('.')
        current = data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None
        
        return current
    
    def _get_chinese_translations(self) -> Dict:
        """中文翻译"""
        return {
            "app": {
                "title": "🎬 CaptionFlow - 智能视频字幕生成器",
                "subtitle": "基于AI的视频字幕自动生成与翻译工具",
                "language_selector": "界面语言",
                "file_upload": "📁 上传视频/音频文件",
                "file_upload_help": "支持MP4、AVI、MOV、MP3、WAV等格式，最大4GB",
                "processing": "正在处理中...",
                "success": "处理完成！",
                "error": "处理出错",
                "download": "下载"
            },
            "sidebar": {
                "settings": "⚙️ 设置",
                "model_selection": "语音识别模型",
                "model_help": "Tiny最快，Large质量最高，Base平衡性能与质量",
                "translator_selection": "翻译服务",
                "translator_help": "Simple本地翻译无需网络，Google翻译质量好但需网络",
                "target_language": "目标语言",
                "bilingual": "生成双语字幕",
                "bilingual_help": "同时包含原文和翻译的字幕文件"
            },
            "languages": {
                "zh": "中文",
                "en": "英文", 
                "es": "西班牙语",
                "fr": "法语",
                "de": "德语",
                "it": "意大利语",
                "pt": "葡萄牙语",
                "ru": "俄语",
                "ja": "日语",
                "ko": "韩语",
                "ar": "阿拉伯语",
                "hi": "印地语"
            },
            "processing": {
                "extracting_audio": "正在提取音频...",
                "speech_recognition": "正在进行语音识别...",
                "translating": "正在翻译字幕...",
                "generating_subtitle": "正在生成字幕文件...",
                "completed": "处理完成！"
            },
            "results": {
                "original_subtitle": "原始字幕",
                "translated_subtitle": "翻译字幕", 
                "bilingual_subtitle": "双语字幕",
                "download_original": "下载原始字幕",
                "download_translated": "下载翻译字幕",
                "download_bilingual": "下载双语字幕"
            },
            "errors": {
                "file_not_supported": "不支持的文件格式",
                "file_too_large": "文件过大",
                "processing_failed": "处理失败",
                "translation_failed": "翻译失败",
                "model_load_failed": "模型加载失败"
            }
        }
    
    def _get_english_translations(self) -> Dict:
        """英文翻译"""
        return {
            "app": {
                "title": "🎬 CaptionFlow - AI Video Subtitle Generator",
                "subtitle": "AI-powered automatic video subtitle generation and translation tool",
                "language_selector": "Interface Language",
                "file_upload": "📁 Upload Video/Audio File",
                "file_upload_help": "Supports MP4, AVI, MOV, MP3, WAV formats, max 4GB",
                "processing": "Processing...",
                "success": "Processing completed!",
                "error": "Processing error",
                "download": "Download"
            },
            "sidebar": {
                "settings": "⚙️ Settings",
                "model_selection": "Speech Recognition Model",
                "model_help": "Tiny is fastest, Large has highest quality, Base balances performance and quality",
                "translator_selection": "Translation Service",
                "translator_help": "Simple local translation without network, Google translation high quality but requires network",
                "target_language": "Target Language",
                "bilingual": "Generate Bilingual Subtitles",
                "bilingual_help": "Subtitle file containing both original and translated text"
            },
            "languages": {
                "zh": "Chinese",
                "en": "English",
                "es": "Spanish", 
                "fr": "French",
                "de": "German",
                "it": "Italian",
                "pt": "Portuguese",
                "ru": "Russian",
                "ja": "Japanese",
                "ko": "Korean",
                "ar": "Arabic",
                "hi": "Hindi"
            },
            "processing": {
                "extracting_audio": "Extracting audio...",
                "speech_recognition": "Performing speech recognition...",
                "translating": "Translating subtitles...",
                "generating_subtitle": "Generating subtitle file...",
                "completed": "Processing completed!"
            },
            "results": {
                "original_subtitle": "Original Subtitles",
                "translated_subtitle": "Translated Subtitles",
                "bilingual_subtitle": "Bilingual Subtitles",
                "download_original": "Download Original",
                "download_translated": "Download Translated",
                "download_bilingual": "Download Bilingual"
            },
            "errors": {
                "file_not_supported": "File format not supported",
                "file_too_large": "File too large",
                "processing_failed": "Processing failed",
                "translation_failed": "Translation failed",
                "model_load_failed": "Model loading failed"
            }
        }
    
    def _get_spanish_translations(self) -> Dict:
        """西班牙语翻译"""
        return {
            "app": {
                "title": "🎬 CaptionFlow - Generador de Subtítulos con IA",
                "subtitle": "Herramienta de generación y traducción automática de subtítulos con IA",
                "language_selector": "Idioma de la Interfaz",
                "file_upload": "📁 Subir Archivo de Video/Audio",
                "file_upload_help": "Soporta formatos MP4, AVI, MOV, MP3, WAV, máximo 4GB",
                "processing": "Procesando...",
                "success": "¡Procesamiento completado!",
                "error": "Error de procesamiento",
                "download": "Descargar"
            },
            "sidebar": {
                "settings": "⚙️ Configuración",
                "model_selection": "Modelo de Reconocimiento de Voz",
                "model_help": "Tiny es el más rápido, Large tiene la mayor calidad, Base equilibra rendimiento y calidad",
                "translator_selection": "Servicio de Traducción",
                "translator_help": "Traducción simple local sin red, Google traducción alta calidad pero requiere red",
                "target_language": "Idioma Objetivo",
                "bilingual": "Generar Subtítulos Bilingües",
                "bilingual_help": "Archivo de subtítulos que contiene tanto el texto original como el traducido"
            },
            "languages": {
                "zh": "Chino",
                "en": "Inglés",
                "es": "Español",
                "fr": "Francés",
                "de": "Alemán",
                "it": "Italiano",
                "pt": "Portugués",
                "ru": "Ruso",
                "ja": "Japonés",
                "ko": "Coreano",
                "ar": "Árabe",
                "hi": "Hindi"
            },
            "processing": {
                "extracting_audio": "Extrayendo audio...",
                "speech_recognition": "Realizando reconocimiento de voz...",
                "translating": "Traduciendo subtítulos...",
                "generating_subtitle": "Generando archivo de subtítulos...",
                "completed": "¡Procesamiento completado!"
            },
            "results": {
                "original_subtitle": "Subtítulos Originales",
                "translated_subtitle": "Subtítulos Traducidos",
                "bilingual_subtitle": "Subtítulos Bilingües",
                "download_original": "Descargar Original",
                "download_translated": "Descargar Traducido",
                "download_bilingual": "Descargar Bilingüe"
            },
            "errors": {
                "file_not_supported": "Formato de archivo no soportado",
                "file_too_large": "Archivo demasiado grande",
                "processing_failed": "Fallo en el procesamiento",
                "translation_failed": "Fallo en la traducción",
                "model_load_failed": "Fallo en la carga del modelo"
            }
        }
    
    def _get_arabic_translations(self) -> Dict:
        """阿拉伯语翻译"""
        return {
            "app": {
                "title": "🎬 CaptionFlow - مولد الترجمة بالذكاء الاصطناعي",
                "subtitle": "أداة توليد وترجمة الترجمة التلقائية للفيديو بالذكاء الاصطناعي",
                "language_selector": "لغة الواجهة",
                "file_upload": "📁 رفع ملف فيديو/صوتي",
                "file_upload_help": "يدعم تنسيقات MP4، AVI، MOV، MP3، WAV، الحد الأقصى 4GB",
                "processing": "جاري المعالجة...",
                "success": "اكتملت المعالجة!",
                "error": "خطأ في المعالجة",
                "download": "تحميل"
            },
            "sidebar": {
                "settings": "⚙️ الإعدادات",
                "model_selection": "نموذج التعرف على الكلام",
                "model_help": "Tiny الأسرع، Large الأعلى جودة، Base يوازن الأداء والجودة",
                "translator_selection": "خدمة الترجمة",
                "translator_help": "الترجمة البسيطة المحلية بدون شبكة، ترجمة Google عالية الجودة لكن تتطلب شبكة",
                "target_language": "اللغة المستهدفة",
                "bilingual": "إنشاء ترجمة ثنائية اللغة",
                "bilingual_help": "ملف ترجمة يحتوي على النص الأصلي والمترجم"
            },
            "languages": {
                "zh": "الصينية",
                "en": "الإنجليزية",
                "es": "الإسبانية",
                "fr": "الفرنسية",
                "de": "الألمانية",
                "it": "الإيطالية",
                "pt": "البرتغالية",
                "ru": "الروسية",
                "ja": "اليابانية",
                "ko": "الكورية",
                "ar": "العربية",
                "hi": "الهندية"
            },
            "processing": {
                "extracting_audio": "استخراج الصوت...",
                "speech_recognition": "تنفيذ التعرف على الكلام...",
                "translating": "ترجمة الترجمة...",
                "generating_subtitle": "إنشاء ملف الترجمة...",
                "completed": "اكتملت المعالجة!"
            },
            "results": {
                "original_subtitle": "الترجمة الأصلية",
                "translated_subtitle": "الترجمة المترجمة",
                "bilingual_subtitle": "الترجمة ثنائية اللغة",
                "download_original": "تحميل الأصلي",
                "download_translated": "تحميل المترجم",
                "download_bilingual": "تحميل ثنائي اللغة"
            },
            "errors": {
                "file_not_supported": "تنسيق الملف غير مدعوم",
                "file_too_large": "الملف كبير جداً",
                "processing_failed": "فشلت المعالجة",
                "translation_failed": "فشلت الترجمة",
                "model_load_failed": "فشل تحميل النموذج"
            }
        }
    
    def _get_hindi_translations(self) -> Dict:
        """印地语翻译"""
        return {
            "app": {
                "title": "🎬 CaptionFlow - AI वीडियो सबटाइटल जेनरेटर",
                "subtitle": "AI-संचालित स्वचालित वीडियो सबटाइटल जेनरेशन और अनुवाद उपकरण",
                "language_selector": "इंटरफेस भाषा",
                "file_upload": "📁 वीडियो/ऑडियो फ़ाइल अपलोड करें",
                "file_upload_help": "MP4, AVI, MOV, MP3, WAV प्रारूपों का समर्थन करता है, अधिकतम 4GB",
                "processing": "प्रसंस्करण...",
                "success": "प्रसंस्करण पूर्ण!",
                "error": "प्रसंस्करण त्रुटि",
                "download": "डाउनलोड"
            },
            "sidebar": {
                "settings": "⚙️ सेटिंग्स",
                "model_selection": "भाषण पहचान मॉडल",
                "model_help": "Tiny सबसे तेज़, Large उच्चतम गुणवत्ता, Base प्रदर्शन और गुणवत्ता को संतुलित करता है",
                "translator_selection": "अनुवाद सेवा",
                "translator_help": "नेटवर्क के बिना सरल स्थानीय अनुवाद, Google अनुवाद उच्च गुणवत्ता लेकिन नेटवर्क की आवश्यकता",
                "target_language": "लक्ष्य भाषा",
                "bilingual": "द्विभाषी सबटाइटल जेनरेट करें",
                "bilingual_help": "मूल और अनुवादित दोनों पाठ वाली सबटाइटल फ़ाइल"
            },
            "languages": {
                "zh": "चीनी",
                "en": "अंग्रेजी",
                "es": "स्पेनिश",
                "fr": "फ्रेंच",
                "de": "जर्मन",
                "it": "इतालवी",
                "pt": "पुर्तगाली",
                "ru": "रूसी",
                "ja": "जापानी",
                "ko": "कोरियाई",
                "ar": "अरबी",
                "hi": "हिंदी"
            },
            "processing": {
                "extracting_audio": "ऑडियो निकाला जा रहा है...",
                "speech_recognition": "भाषण पहचान का प्रदर्शन...",
                "translating": "सबटाइटल का अनुवाद...",
                "generating_subtitle": "सबटाइटल फ़ाइल जेनरेट की जा रही है...",
                "completed": "प्रसंस्करण पूर्ण!"
            },
            "results": {
                "original_subtitle": "मूल सबटाइटल",
                "translated_subtitle": "अनुवादित सबटाइटल",
                "bilingual_subtitle": "द्विभाषी सबटाइटल",
                "download_original": "मूल डाउनलोड करें",
                "download_translated": "अनुवादित डाउनलोड करें",
                "download_bilingual": "द्विभाषी डाउनलोड करें"
            },
            "errors": {
                "file_not_supported": "फ़ाइल प्रारूप समर्थित नहीं",
                "file_too_large": "फ़ाइल बहुत बड़ी",
                "processing_failed": "प्रसंस्करण विफल",
                "translation_failed": "अनुवाद विफल",
                "model_load_failed": "मॉडल लोडिंग विफल"
            }
        }
    
    def _get_portuguese_translations(self) -> Dict:
        """葡萄牙语翻译"""
        return {
            "app": {
                "title": "🎬 CaptionFlow - Gerador de Legendas com IA",
                "subtitle": "Ferramenta de geração e tradução automática de legendas com IA",
                "language_selector": "Idioma da Interface",
                "file_upload": "📁 Enviar Arquivo de Vídeo/Áudio",
                "file_upload_help": "Suporta formatos MP4, AVI, MOV, MP3, WAV, máximo 4GB",
                "processing": "Processando...",
                "success": "Processamento concluído!",
                "error": "Erro de processamento",
                "download": "Baixar"
            },
            "sidebar": {
                "settings": "⚙️ Configurações",
                "model_selection": "Modelo de Reconhecimento de Fala",
                "model_help": "Tiny é o mais rápido, Large tem a maior qualidade, Base equilibra desempenho e qualidade",
                "translator_selection": "Serviço de Tradução",
                "translator_help": "Tradução simples local sem rede, Google tradução alta qualidade mas requer rede",
                "target_language": "Idioma Alvo",
                "bilingual": "Gerar Legendas Bilíngues",
                "bilingual_help": "Arquivo de legendas contendo tanto o texto original quanto o traduzido"
            },
            "languages": {
                "zh": "Chinês",
                "en": "Inglês",
                "es": "Espanhol",
                "fr": "Francês",
                "de": "Alemão",
                "it": "Italiano",
                "pt": "Português",
                "ru": "Russo",
                "ja": "Japonês",
                "ko": "Coreano",
                "ar": "Árabe",
                "hi": "Hindi"
            },
            "processing": {
                "extracting_audio": "Extraindo áudio...",
                "speech_recognition": "Realizando reconhecimento de fala...",
                "translating": "Traduzindo legendas...",
                "generating_subtitle": "Gerando arquivo de legendas...",
                "completed": "Processamento concluído!"
            },
            "results": {
                "original_subtitle": "Legendas Originais",
                "translated_subtitle": "Legendas Traduzidas",
                "bilingual_subtitle": "Legendas Bilíngues",
                "download_original": "Baixar Original",
                "download_translated": "Baixar Traduzido",
                "download_bilingual": "Baixar Bilíngue"
            },
            "errors": {
                "file_not_supported": "Formato de arquivo não suportado",
                "file_too_large": "Arquivo muito grande",
                "processing_failed": "Falha no processamento",
                "translation_failed": "Falha na tradução",
                "model_load_failed": "Falha no carregamento do modelo"
            }
        }
    
    def _get_russian_translations(self) -> Dict:
        """俄语翻译"""
        return {
            "app": {
                "title": "🎬 CaptionFlow - ИИ Генератор Субтитров",
                "subtitle": "Инструмент автоматической генерации и перевода субтитров с ИИ",
                "language_selector": "Язык Интерфейса",
                "file_upload": "📁 Загрузить Видео/Аудио Файл",
                "file_upload_help": "Поддерживает форматы MP4, AVI, MOV, MP3, WAV, максимум 4GB",
                "processing": "Обработка...",
                "success": "Обработка завершена!",
                "error": "Ошибка обработки",
                "download": "Скачать"
            },
            "sidebar": {
                "settings": "⚙️ Настройки",
                "model_selection": "Модель Распознавания Речи",
                "model_help": "Tiny самая быстрая, Large наивысшее качество, Base балансирует производительность и качество",
                "translator_selection": "Служба Перевода",
                "translator_help": "Простой локальный перевод без сети, Google перевод высокого качества но требует сеть",
                "target_language": "Целевой Язык",
                "bilingual": "Создать Двуязычные Субтитры",
                "bilingual_help": "Файл субтитров, содержащий как оригинальный, так и переведенный текст"
            },
            "languages": {
                "zh": "Китайский",
                "en": "Английский",
                "es": "Испанский",
                "fr": "Французский",
                "de": "Немецкий",
                "it": "Итальянский",
                "pt": "Португальский",
                "ru": "Русский",
                "ja": "Японский",
                "ko": "Корейский",
                "ar": "Арабский",
                "hi": "Хинди"
            },
            "processing": {
                "extracting_audio": "Извлечение аудио...",
                "speech_recognition": "Выполнение распознавания речи...",
                "translating": "Перевод субтитров...",
                "generating_subtitle": "Создание файла субтитров...",
                "completed": "Обработка завершена!"
            },
            "results": {
                "original_subtitle": "Оригинальные Субтитры",
                "translated_subtitle": "Переведенные Субтитры",
                "bilingual_subtitle": "Двуязычные Субтитры",
                "download_original": "Скачать Оригинал",
                "download_translated": "Скачать Переведенные",
                "download_bilingual": "Скачать Двуязычные"
            },
            "errors": {
                "file_not_supported": "Формат файла не поддерживается",
                "file_too_large": "Файл слишком большой",
                "processing_failed": "Ошибка обработки",
                "translation_failed": "Ошибка перевода",
                "model_load_failed": "Ошибка загрузки модели"
            }
        }
    
    def _get_japanese_translations(self) -> Dict:
        """日语翻译"""
        return {
            "app": {
                "title": "🎬 CaptionFlow - AI動画字幕ジェネレーター",
                "subtitle": "AI駆動の自動動画字幕生成・翻訳ツール",
                "language_selector": "インターフェース言語",
                "file_upload": "📁 動画/音声ファイルをアップロード",
                "file_upload_help": "MP4、AVI、MOV、MP3、WAVフォーマットをサポート、最大4GB",
                "processing": "処理中...",
                "success": "処理完了！",
                "error": "処理エラー",
                "download": "ダウンロード"
            },
            "sidebar": {
                "settings": "⚙️ 設定",
                "model_selection": "音声認識モデル",
                "model_help": "Tinyが最速、Largeが最高品質、Baseが性能と品質のバランス",
                "translator_selection": "翻訳サービス",
                "translator_help": "シンプルなローカル翻訳はネットワーク不要、Google翻訳は高品質だがネットワークが必要",
                "target_language": "対象言語",
                "bilingual": "バイリンガル字幕を生成",
                "bilingual_help": "原文と翻訳の両方を含む字幕ファイル"
            },
            "languages": {
                "zh": "中国語",
                "en": "英語",
                "es": "スペイン語",
                "fr": "フランス語",
                "de": "ドイツ語",
                "it": "イタリア語",
                "pt": "ポルトガル語",
                "ru": "ロシア語",
                "ja": "日本語",
                "ko": "韓国語",
                "ar": "アラビア語",
                "hi": "ヒンディー語"
            },
            "processing": {
                "extracting_audio": "音声を抽出中...",
                "speech_recognition": "音声認識を実行中...",
                "translating": "字幕を翻訳中...",
                "generating_subtitle": "字幕ファイルを生成中...",
                "completed": "処理完了！"
            },
            "results": {
                "original_subtitle": "元の字幕",
                "translated_subtitle": "翻訳された字幕",
                "bilingual_subtitle": "バイリンガル字幕",
                "download_original": "元ファイルをダウンロード",
                "download_translated": "翻訳をダウンロード",
                "download_bilingual": "バイリンガルをダウンロード"
            },
            "errors": {
                "file_not_supported": "サポートされていないファイル形式",
                "file_too_large": "ファイルが大きすぎます",
                "processing_failed": "処理に失敗しました",
                "translation_failed": "翻訳に失敗しました",
                "model_load_failed": "モデルの読み込みに失敗しました"
            }
        }
    
    def _get_german_translations(self) -> Dict:
        """德语翻译"""
        return {
            "app": {
                "title": "🎬 CaptionFlow - KI Video-Untertitel-Generator",
                "subtitle": "KI-gestütztes automatisches Video-Untertitel-Generierungs- und Übersetzungstool",
                "language_selector": "Oberflächensprache",
                "file_upload": "📁 Video/Audio-Datei hochladen",
                "file_upload_help": "Unterstützt MP4, AVI, MOV, MP3, WAV Formate, maximal 4GB",
                "processing": "Verarbeitung läuft...",
                "success": "Verarbeitung abgeschlossen!",
                "error": "Verarbeitungsfehler",
                "download": "Herunterladen"
            },
            "sidebar": {
                "settings": "⚙️ Einstellungen",
                "model_selection": "Spracherkennungsmodell",
                "model_help": "Tiny ist am schnellsten, Large hat höchste Qualität, Base balanciert Leistung und Qualität",
                "translator_selection": "Übersetzungsdienst",
                "translator_help": "Einfache lokale Übersetzung ohne Netzwerk, Google Übersetzung hohe Qualität aber benötigt Netzwerk",
                "target_language": "Zielsprache",
                "bilingual": "Zweisprachige Untertitel erstellen",
                "bilingual_help": "Untertiteldatei mit sowohl originalem als auch übersetztem Text"
            },
            "languages": {
                "zh": "Chinesisch",
                "en": "Englisch",
                "es": "Spanisch",
                "fr": "Französisch",
                "de": "Deutsch",
                "it": "Italienisch",
                "pt": "Portugiesisch",
                "ru": "Russisch",
                "ja": "Japanisch",
                "ko": "Koreanisch",
                "ar": "Arabisch",
                "hi": "Hindi"
            },
            "processing": {
                "extracting_audio": "Audio wird extrahiert...",
                "speech_recognition": "Spracherkennung wird durchgeführt...",
                "translating": "Untertitel werden übersetzt...",
                "generating_subtitle": "Untertiteldatei wird erstellt...",
                "completed": "Verarbeitung abgeschlossen!"
            },
            "results": {
                "original_subtitle": "Original-Untertitel",
                "translated_subtitle": "Übersetzte Untertitel",
                "bilingual_subtitle": "Zweisprachige Untertitel",
                "download_original": "Original herunterladen",
                "download_translated": "Übersetzung herunterladen",
                "download_bilingual": "Zweisprachig herunterladen"
            },
            "errors": {
                "file_not_supported": "Dateiformat nicht unterstützt",
                "file_too_large": "Datei zu groß",
                "processing_failed": "Verarbeitung fehlgeschlagen",
                "translation_failed": "Übersetzung fehlgeschlagen",
                "model_load_failed": "Modell-Loading fehlgeschlagen"
            }
        }
    
    def _get_french_translations(self) -> Dict:
        """法语翻译"""
        return {
            "app": {
                "title": "🎬 CaptionFlow - Générateur de Sous-titres IA",
                "subtitle": "Outil de génération et traduction automatique de sous-titres alimenté par l'IA",
                "language_selector": "Langue de l'Interface",
                "file_upload": "📁 Télécharger un Fichier Vidéo/Audio",
                "file_upload_help": "Supporte les formats MP4, AVI, MOV, MP3, WAV, maximum 4GB",
                "processing": "Traitement en cours...",
                "success": "Traitement terminé!",
                "error": "Erreur de traitement",
                "download": "Télécharger"
            },
            "sidebar": {
                "settings": "⚙️ Paramètres",
                "model_selection": "Modèle de Reconnaissance Vocale",
                "model_help": "Tiny est le plus rapide, Large a la plus haute qualité, Base équilibre performance et qualité",
                "translator_selection": "Service de Traduction",
                "translator_help": "Traduction simple locale sans réseau, Google traduction haute qualité mais nécessite réseau",
                "target_language": "Langue Cible",
                "bilingual": "Générer des Sous-titres Bilingues",
                "bilingual_help": "Fichier de sous-titres contenant à la fois le texte original et traduit"
            },
            "languages": {
                "zh": "Chinois",
                "en": "Anglais",
                "es": "Espagnol",
                "fr": "Français",
                "de": "Allemand",
                "it": "Italien",
                "pt": "Portugais",
                "ru": "Russe",
                "ja": "Japonais",
                "ko": "Coréen",
                "ar": "Arabe",
                "hi": "Hindi"
            },
            "processing": {
                "extracting_audio": "Extraction de l'audio...",
                "speech_recognition": "Exécution de la reconnaissance vocale...",
                "translating": "Traduction des sous-titres...",
                "generating_subtitle": "Génération du fichier de sous-titres...",
                "completed": "Traitement terminé!"
            },
            "results": {
                "original_subtitle": "Sous-titres Originaux",
                "translated_subtitle": "Sous-titres Traduits",
                "bilingual_subtitle": "Sous-titres Bilingues",
                "download_original": "Télécharger Original",
                "download_translated": "Télécharger Traduit",
                "download_bilingual": "Télécharger Bilingue"
            },
            "errors": {
                "file_not_supported": "Format de fichier non supporté",
                "file_too_large": "Fichier trop volumineux",
                "processing_failed": "Échec du traitement",
                "translation_failed": "Échec de la traduction",
                "model_load_failed": "Échec du chargement du modèle"
            }
        }


# 全局国际化实例
i18n = I18n() 