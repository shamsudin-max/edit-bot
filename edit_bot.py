#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EditBot - Telegram бот для создания видео-едитов
Версия: 6.2 (20+ идей, распределенные приложения)
"""

import asyncio
import json
import logging
import os
import random
from datetime import datetime
from typing import Dict, List, Optional

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    Message, 
    CallbackQuery, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ============================================
# ТОКЕН (БЕРЁТСЯ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ)
# ============================================
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("❌ ОШИБКА: Не задан BOT_TOKEN в переменных окружения!")

ADMIN_ID = 8570314493  # ТВОЙ TELEGRAM ID

# ============================================
# НАСТРОЙКИ ЛОГИРОВАНИЯ
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# БАЗА ДАННЫХ (20+ ИДЕЙ ДЛЯ ЕДИТОВ)
# ============================================

IDEAS = [
    # Оригинальные 8 идей
    {
        "id": 1,
        "title": "🌅 Закат на пляже",
        "description": "Красивые кадры заката, волны, песок. Добавить замедленные съемки.",
        "style": "aesthetic",
        "mood": "romantic",
        "music": "Frank Ocean - Nights",
        "effects": ["Замедление", "Теплые тона", "Свечение"],
        "transitions": ["Плавное затухание"],
        "duration": "15-30 секунд",
        "difficulty": "Легкий",
        "likes": 45
    },
    {
        "id": 2,
        "title": "🌃 Город ночью",
        "description": "Неон, огни, дождь, отражения в лужах. Атмосферный ночной город.",
        "style": "cyberpunk",
        "mood": "mysterious",
        "music": "The Weeknd - Blinding Lights (Slowed)",
        "effects": ["Неон", "Глитч", "Хром. аберрация"],
        "transitions": ["Вспышка", "Вытеснение"],
        "duration": "20-40 секунд",
        "difficulty": "Средний",
        "likes": 67
    },
    {
        "id": 3,
        "title": "🎮 Игровые моменты",
        "description": "Клип из лучших моментов игры с киллами и мувами.",
        "style": "gaming",
        "mood": "energetic",
        "music": "Phonk music",
        "effects": ["Ускорение", "Замедление", "Screen shake"],
        "transitions": ["Резкие переходы под бит", "Zoom"],
        "duration": "30-60 секунд",
        "difficulty": "Сложный",
        "likes": 89
    },
    {
        "id": 4,
        "title": "👥 Воспоминания с друзьями",
        "description": "Теплые моменты, смех, объятия, совместные фото/видео.",
        "style": "vibe",
        "mood": "happy",
        "music": "Joji - Glimpse of Us",
        "effects": ["Винтаж", "VHS эффект"],
        "transitions": ["Слайд-шоу", "Перемотка"],
        "duration": "20-30 секунд",
        "difficulty": "Легкий",
        "likes": 34
    },
    {
        "id": 5,
        "title": "🌸 Эстетика аниме",
        "description": "Кадры из аниме под лиричную музыку. Акцент на глаза, природу, эмоции.",
        "style": "anime",
        "mood": "sad",
        "music": "Kenshi Yonezu - Lemon",
        "effects": ["Акварель", "Свечение", "Яркие цвета"],
        "transitions": ["Растворение", "Плавный переход"],
        "duration": "15-25 секунд",
        "difficulty": "Средний",
        "likes": 92
    },
    {
        "id": 6,
        "title": "🏋️ Спортивные достижения",
        "description": "Нарезка тренировок, побед, моментов преодоления себя.",
        "style": "dark",
        "mood": "epic",
        "music": "NF - The Search",
        "effects": ["Замедление", "Ч/Б с акцентом", "Контраст"],
        "transitions": ["Whip", "Push"],
        "duration": "30-45 секунд",
        "difficulty": "Средний",
        "likes": 56
    },
    {
        "id": 7,
        "title": "✈️ Путешествие",
        "description": "Разные локации, перелеты, еда, природа, люди.",
        "style": "aesthetic",
        "mood": "happy",
        "music": "Tame Impala - The Less I Know The Better",
        "effects": ["Цветокоррекция", "Параллакс"],
        "transitions": ["Разрез", "Совпадение по движению"],
        "duration": "40-60 секунд",
        "difficulty": "Сложный",
        "likes": 71
    },
    {
        "id": 8,
        "title": "📼 Ретро 90-е",
        "description": "VHS стиль, старые кадры, шумы, пиксели.",
        "style": "retro",
        "mood": "mysterious",
        "music": "Macintosh Plus - Lisa Frank 420",
        "effects": ["VHS", "Шум", "Помехи"],
        "transitions": ["Глитч", "Полосы"],
        "duration": "15-30 секунд",
        "difficulty": "Средний",
        "likes": 43
    },
    
    # НОВЫЕ ИДЕИ (12 штук)
    {
        "id": 9,
        "title": "🌧️ Дождливый день",
        "description": "Капли дождя на стекле, мокрые улицы, зонты, отражения. Меланхоличная атмосфера.",
        "style": "aesthetic",
        "mood": "sad",
        "music": "Lana Del Rey - Summertime Sadness",
        "effects": ["Замедление", "Холодные тона", "Размытие"],
        "transitions": ["Плавные переходы"],
        "duration": "20-35 секунд",
        "difficulty": "Средний",
        "likes": 38
    },
    {
        "id": 10,
        "title": "🎂 День рождения",
        "description": "Праздник, торт, свечи, подарки, улыбки, веселье с друзьями.",
        "style": "vibe",
        "mood": "happy",
        "music": "Pharrell Williams - Happy",
        "effects": ["Яркие цвета", "Вспышки", "Замедление"],
        "transitions": ["Слайд-шоу", "Вытеснение"],
        "duration": "30-45 секунд",
        "difficulty": "Легкий",
        "likes": 52
    },
    {
        "id": 11,
        "title": "🏎️ Дрифт на машинах",
        "description": "Гонки, дрифт, заносы, выхлоп, ночные трассы, скорость.",
        "style": "gaming",
        "mood": "energetic",
        "music": "Drift Phonk",
        "effects": ["Screen shake", "Замедление", "Неон"],
        "transitions": ["Резкие", "Zoom"],
        "duration": "25-40 секунд",
        "difficulty": "Средний",
        "likes": 77
    },
    {
        "id": 12,
        "title": "💔 Расставание",
        "description": "Грустные моменты, слезы, одиночество, дождь, воспоминания о бывшем.",
        "style": "dark",
        "mood": "sad",
        "music": "Juice WRLD - Lucid Dreams",
        "effects": ["Ч/Б", "Замедление", "Размытие"],
        "transitions": ["Плавные", "Растворение"],
        "duration": "20-35 секунд",
        "difficulty": "Средний",
        "likes": 63
    },
    {
        "id": 13,
        "title": "🤸‍♀️ Танцевальный клип",
        "description": "Танцы, движения, эмоции, переходы под бит, крутые ракурсы.",
        "style": "vibe",
        "mood": "energetic",
        "music": "Dua Lipa - Dance The Night",
        "effects": ["Резкие переходы", "Замедление", "Вспышки"],
        "transitions": ["Под бит", "Zoom"],
        "duration": "20-30 секунд",
        "difficulty": "Средний",
        "likes": 81
    },
    {
        "id": 14,
        "title": "🐱 Милые животные",
        "description": "Котики, собачки, смешные моменты, умиление, домашние питомцы.",
        "style": "aesthetic",
        "mood": "happy",
        "music": "Lo-fi beats",
        "effects": ["Свечение", "Теплые тона", "Замедление"],
        "transitions": ["Плавные"],
        "duration": "15-25 секунд",
        "difficulty": "Легкий",
        "likes": 94
    },
    {
        "id": 15,
        "title": "🎄 Новый год",
        "description": "Елка, гирлянды, снег, фейерверки, подарки, праздничное настроение.",
        "style": "aesthetic",
        "mood": "happy",
        "music": "Wham! - Last Christmas",
        "effects": ["Свечение", "Вспышки", "Теплые тона"],
        "transitions": ["Слайд-шоу", "Вспышка"],
        "duration": "25-40 секунд",
        "difficulty": "Легкий",
        "likes": 88
    },
    {
        "id": 16,
        "title": "🏔️ Природа и горы",
        "description": "Горы, лес, озера, рассветы, красивые пейзажи, единение с природой.",
        "style": "aesthetic",
        "mood": "romantic",
        "music": "Hans Zimmer - Interstellar",
        "effects": ["Замедление", "Цветокоррекция", "Параллакс"],
        "transitions": ["Плавные"],
        "duration": "30-50 секунд",
        "difficulty": "Средний",
        "likes": 57
    },
    {
        "id": 17,
        "title": "👰 Свадьба",
        "description": "Свадебная церемония, кольца, поцелуй, слезы счастья, первый танец.",
        "style": "aesthetic",
        "mood": "romantic",
        "music": "Ed Sheeran - Perfect",
        "effects": ["Замедление", "Свечение", "Теплые тона"],
        "transitions": ["Плавные"],
        "duration": "40-60 секунд",
        "difficulty": "Средний",
        "likes": 72
    },
    {
        "id": 18,
        "title": "🎸 Концерт",
        "description": "Выступление любимой группы, толпа, огни, эмоции, море людей.",
        "style": "dark",
        "mood": "energetic",
        "music": "Imagine Dragons - Believer",
        "effects": ["Вспышки", "Screen shake", "Неон"],
        "transitions": ["Резкие", "Под бит"],
        "duration": "25-40 секунд",
        "difficulty": "Средний",
        "likes": 49
    },
    {
        "id": 19,
        "title": "🧘 Медитация и спокойствие",
        "description": "Йога, море, рассвет, спокойствие, гармония, умиротворение.",
        "style": "aesthetic",
        "mood": "romantic",
        "music": "Meditation music",
        "effects": ["Замедление", "Размытие", "Пастельные тона"],
        "transitions": ["Очень плавные"],
        "duration": "20-40 секунд",
        "difficulty": "Легкий",
        "likes": 36
    },
    {
        "id": 20,
        "title": "🏀 Спортивный баскетбол",
        "description": "Бросок мяча, победные моменты, тренировки, эмоции игроков.",
        "style": "gaming",
        "mood": "energetic",
        "music": "Phonk remix",
        "effects": ["Замедление", "Screen shake", "Резкие переходы"],
        "transitions": ["Zoom", "Whip"],
        "duration": "20-35 секунд",
        "difficulty": "Средний",
        "likes": 44
    }
]

# ============================================
# ПРИЛОЖЕНИЯ ДЛЯ МОНТАЖА (РАСПРЕДЕЛЕННЫЕ)
# ============================================

# Приложения для видео
VIDEO_APPS = [
    {
        "name": "🎬 CapCut",
        "desc": "Лучшее для телефона. Авто-субтитры, шаблоны, эффекты, бесплатно",
        "platform": "iOS/Android/Web"
    },
    {
        "name": "🎥 VN Video Editor",
        "desc": "Продвинутый монтаж. Кривые скорости, хромакей, ключевые кадры",
        "platform": "iOS/Android"
    },
    {
        "name": "🎞️ KineMaster",
        "desc": "Профессиональный на телефоне. Много слоев, хромакей, 4K",
        "platform": "iOS/Android"
    },
    {
        "name": "📱 InShot",
        "desc": "Для соцсетей. Обрезка, музыка, стикеры, текст",
        "platform": "iOS/Android"
    },
    {
        "name": "💻 Premiere Pro",
        "desc": "Профессиональный монтаж. Любые форматы, цветокоррекция",
        "platform": "Windows/Mac"
    },
    {
        "name": "🎨 DaVinci Resolve",
        "desc": "Лучшая цветокоррекция. Fusion эффекты, бесплатно",
        "platform": "Windows/Mac/Linux"
    },
    {
        "name": "🍎 Final Cut Pro",
        "desc": "Для Mac. Оптимизирован, магнитная временная шкала",
        "platform": "Mac"
    },
    {
        "name": "✂️ Shotcut",
        "desc": "Бесплатный редактор. Много форматов, фильтры",
        "platform": "Windows/Mac/Linux"
    },
    {
        "name": "🎬 Filmora",
        "desc": "Для начинающих на ПК. Готовые эффекты, интуитивно",
        "platform": "Windows/Mac"
    },
    {
        "name": "📲 PowerDirector",
        "desc": "Мощный редактор. 4K, хромакей, стабилизация",
        "platform": "Android/iOS/Windows"
    }
]

# Приложения для фото
PHOTO_APPS = [
    {
        "name": "📸 Adobe Lightroom",
        "desc": "Профессиональная обработка. RAW, пресеты, маски",
        "platform": "iOS/Android/Windows/Mac"
    },
    {
        "name": "🎨 VSCO",
        "desc": "Эстетичные фильтры. Стильные пресеты, ретушь",
        "platform": "iOS/Android"
    },
    {
        "name": "✨ Snapseed",
        "desc": "Профессиональная на телефоне. Точечная коррекция, HDR",
        "platform": "iOS/Android"
    },
    {
        "name": "🎭 PicsArt",
        "desc": "Креативные коллажи. Наклейки, эффекты, рисование",
        "platform": "iOS/Android"
    },
    {
        "name": "🖌️ Adobe Photoshop",
        "desc": "Профессиональная ретушь. Слои, маски, кисти",
        "platform": "Windows/Mac/iPad"
    },
    {
        "name": "🎨 Canva",
        "desc": "Дизайн и соцсети. Шаблоны, текст, анимация",
        "platform": "Web/iOS/Android"
    },
    {
        "name": "✨ Pixlr",
        "desc": "Бесплатный Photoshop. Слои, фильтры, удаление фона",
        "platform": "Web/iOS/Android"
    },
    {
        "name": "🔮 Remini",
        "desc": "Улучшение качества. Восстановление старых фото",
        "platform": "iOS/Android"
    },
    {
        "name": "🌸 Meitu",
        "desc": "Ретушь лица. Красота, фильтры, макияж",
        "platform": "iOS/Android"
    },
    {
        "name": "🖼️ GIMP",
        "desc": "Бесплатный аналог Photoshop. Слои, маски, плагины",
        "platform": "Windows/Mac/Linux"
    }
]

# Приложения для аудио
AUDIO_APPS = [
    {
        "name": "🎧 FL Studio",
        "desc": "Создание музыки. Синтезаторы, сэмплы, миди",
        "platform": "Windows/Mac"
    },
    {
        "name": "🎵 Audacity",
        "desc": "Редактирование аудио. Обрезка, эффекты, удаление шума",
        "platform": "Windows/Mac/Linux"
    },
    {
        "name": "🎸 BandLab",
        "desc": "Создание на телефоне. Мультитрек, сэмплы",
        "platform": "iOS/Android/Web"
    },
    {
        "name": "⚡ Ableton Live",
        "desc": "Живые выступления. Петли, эффекты, автоматизация",
        "platform": "Windows/Mac"
    },
    {
        "name": "🎹 GarageBand",
        "desc": "Для начинающих музыкантов. Виртуальные инструменты",
        "platform": "Mac/iOS"
    },
    {
        "name": "🌊 WavePad",
        "desc": "Редактирование звука. Обрезка, эффекты, нормализация",
        "platform": "Windows/Mac/iOS/Android"
    },
    {
        "name": "📱 FL Studio Mobile",
        "desc": "Создание музыки на телефоне. Синтезаторы, драм-машина",
        "platform": "iOS/Android"
    },
    {
        "name": "🎙️ Adobe Audition",
        "desc": "Профессиональный звук. Многодорожечная запись",
        "platform": "Windows/Mac"
    },
    {
        "name": "🗣️ VOCO",
        "desc": "Обработка голоса. Изменение голоса, автотюн",
        "platform": "iOS/Android"
    },
    {
        "name": "🎼 Cakewalk",
        "desc": "Бесплатная DAW. Мультитрек, миди, виртуальные инструменты",
        "platform": "Windows"
    }
]

# ============================================
# КЛАСС ДЛЯ РАБОТЫ С ДАННЫМИ
# ============================================

class DataStorage:
    def __init__(self):
        self.ideas = {idea["id"]: idea for idea in IDEAS}
        self.video_apps = VIDEO_APPS
        self.photo_apps = PHOTO_APPS
        self.audio_apps = AUDIO_APPS
        self.user_favorites = {}
        self.load_data()
    
    def load_data(self):
        """Загрузка данных из файла"""
        try:
            if os.path.exists("edit_bot_data.json"):
                with open("edit_bot_data.json", "r", encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_favorites = data.get("favorites", {})
                    
                    # Загружаем лайки
                    saved_likes = data.get("likes", {})
                    for idea_id, likes in saved_likes.items():
                        if int(idea_id) in self.ideas:
                            self.ideas[int(idea_id)]["likes"] = likes
                            
                logger.info(f"Загружены данные для {len(self.user_favorites)} пользователей")
        except Exception as e:
            logger.error(f"Ошибка загрузки: {e}")
            self.user_favorites = {}
    
    def save_data(self):
        """Сохранение данных в файл"""
        try:
            # Собираем лайки
            likes = {}
            for idea_id, idea in self.ideas.items():
                likes[str(idea_id)] = idea["likes"]
            
            data = {
                "favorites": self.user_favorites,
                "likes": likes,
                "last_update": datetime.now().isoformat()
            }
            
            with open("edit_bot_data.json", "w", encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.info("Данные сохранены")
        except Exception as e:
            logger.error(f"Ошибка сохранения: {e}")
    
    def add_favorite(self, user_id: int, idea_id: int):
        """Добавить идею в избранное"""
        user_id = str(user_id)
        if user_id not in self.user_favorites:
            self.user_favorites[user_id] = []
        
        if idea_id not in self.user_favorites[user_id]:
            self.user_favorites[user_id].append(idea_id)
            if idea_id in self.ideas:
                self.ideas[idea_id]["likes"] += 1
            self.save_data()
            return True
        return False
    
    def remove_favorite(self, user_id: int, idea_id: int):
        """Удалить идею из избранного"""
        user_id = str(user_id)
        if user_id in self.user_favorites and idea_id in self.user_favorites[user_id]:
            self.user_favorites[user_id].remove(idea_id)
            if idea_id in self.ideas:
                self.ideas[idea_id]["likes"] = max(0, self.ideas[idea_id]["likes"] - 1)
            self.save_data()
            return True
        return False
    
    def get_favorites(self, user_id: int) -> List[Dict]:
        """Получить избранное пользователя"""
        user_id = str(user_id)
        if user_id not in self.user_favorites:
            return []
        return [self.ideas[i] for i in self.user_favorites[user_id] if i in self.ideas]
    
    def get_ideas_by_style(self, style: str) -> List[Dict]:
        """Получить идеи по стилю"""
        return [i for i in self.ideas.values() if i["style"] == style]
    
    def get_ideas_by_mood(self, mood: str) -> List[Dict]:
        """Получить идеи по настроению"""
        return [i for i in self.ideas.values() if i["mood"] == mood]
    
    def get_popular_ideas(self, limit: int = 5) -> List[Dict]:
        """Получить популярные идеи"""
        return sorted(self.ideas.values(), key=lambda x: x["likes"], reverse=True)[:limit]

# ============================================
# ИНИЦИАЛИЗАЦИЯ БОТА
# ============================================

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())
storage = DataStorage()

# ============================================
# СОСТОЯНИЯ FSM
# ============================================

class EditStates(StatesGroup):
    waiting_for_description = State()

# ============================================
# КЛАВИАТУРЫ
# ============================================

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное нижнее меню"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="💡 Все идеи"),
        KeyboardButton(text="🎨 По стилю"),
        KeyboardButton(text="🎭 По настроению")
    )
    builder.row(
        KeyboardButton(text="🎲 Случайная идея"),
        KeyboardButton(text="❤️ Избранное"),
        KeyboardButton(text="✨ По описанию")
    )
    builder.row(
        KeyboardButton(text="🎬 Видео приложения"),
        KeyboardButton(text="📸 Фото приложения"),
        KeyboardButton(text="🎵 Аудио приложения")
    )
    builder.row(
        KeyboardButton(text="🔥 Популярные идеи"),
        KeyboardButton(text="ℹ️ Помощь")
    )
    return builder.as_markup(resize_keyboard=True)

def get_style_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура стилей"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✨ Эстетика", callback_data="style_aesthetic"),
        InlineKeyboardButton(text="🌃 Киберпанк", callback_data="style_cyberpunk")
    )
    builder.row(
        InlineKeyboardButton(text="🌸 Аниме", callback_data="style_anime"),
        InlineKeyboardButton(text="🎮 Игровой", callback_data="style_gaming")
    )
    builder.row(
        InlineKeyboardButton(text="📼 Ретро", callback_data="style_retro"),
        InlineKeyboardButton(text="🌑 Темный", callback_data="style_dark")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
    )
    return builder.as_markup()

def get_mood_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроений"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="😢 Грустное", callback_data="mood_sad"),
        InlineKeyboardButton(text="😊 Счастливое", callback_data="mood_happy")
    )
    builder.row(
        InlineKeyboardButton(text="⚡ Энергичное", callback_data="mood_energetic"),
        InlineKeyboardButton(text="💕 Романтичное", callback_data="mood_romantic")
    )
    builder.row(
        InlineKeyboardButton(text="👻 Загадочное", callback_data="mood_mysterious"),
        InlineKeyboardButton(text="⚔️ Эпичное", callback_data="mood_epic")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
    )
    return builder.as_markup()

def get_idea_buttons(idea_id: int, user_id: int) -> InlineKeyboardMarkup:
    """Кнопки для идеи (лайк/копировать)"""
    builder = InlineKeyboardBuilder()
    user_id = str(user_id)
    is_favorite = user_id in storage.user_favorites and idea_id in storage.user_favorites.get(user_id, [])
    
    builder.row(
        InlineKeyboardButton(
            text="❤️" if not is_favorite else "💔 Убрать",
            callback_data=f"fav_{idea_id}" if not is_favorite else f"unfav_{idea_id}"
        ),
        InlineKeyboardButton(text="📋 Копировать", callback_data=f"copy_{idea_id}")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")
    )
    return builder.as_markup()

# ============================================
# ФУНКЦИИ ГЕНЕРАЦИИ
# ============================================

def generate_idea_from_description(description: str) -> str:
    """Генерирует идею на основе описания пользователя"""
    desc_lower = description.lower()
    
    # Определяем стиль
    style = "aesthetic"
    if any(word in desc_lower for word in ["игра", "геймплей", "килл", "фонк", "дрифт"]):
        style = "gaming"
    elif any(word in desc_lower for word in ["аниме", "япония", "анимешный"]):
        style = "anime"
    elif any(word in desc_lower for word in ["киберпанк", "неон", "город", "ночь", "огни"]):
        style = "cyberpunk"
    elif any(word in desc_lower for word in ["ретро", "старый", "винтаж", "vhs", "90"]):
        style = "retro"
    elif any(word in desc_lower for word in ["темный", "мрачный", "грустный", "депрессия"]):
        style = "dark"
    
    # Определяем настроение
    mood = "happy"
    if any(word in desc_lower for word in ["груст", "печаль", "депресси", "слезы"]):
        mood = "sad"
    elif any(word in desc_lower for word in ["энерги", "быстр", "динамич", "актив"]):
        mood = "energetic"
    elif any(word in desc_lower for word in ["романт", "любов", "нежн"]):
        mood = "romantic"
    
    # Подбираем эффекты
    effects_map = {
        "aesthetic": "мягкое свечение, пастельные тона, легкое размытие",
        "cyberpunk": "неон, глитч, хром. аберрация, сине-розовые тона",
        "anime": "акварель, яркие цвета, блестки, звездочки",
        "gaming": "screen shake, замедление в моментах, резкие переходы",
        "retro": "VHS шум, зернистость, эффект старой пленки",
        "dark": "черно-белый, контраст, глубокие тени",
    }
    
    # Подбираем музыку
    music_map = {
        "aesthetic": "lo-fi, Frank Ocean, Joji",
        "cyberpunk": "synthwave, The Weeknd, Kavinsky",
        "anime": "anime OST, Kenshi Yonezu, RADWIMPS",
        "gaming": "phonk, drift phonk, METAMORPHOSIS",
        "retro": "city pop, 80s synth, Macintosh Plus",
        "dark": "dark trap, NF, $uicideboy$",
    }
    
    return f"""✨ **ИДЕЯ ПО ТВОЕМУ ОПИСАНИЮ**

📝 **Ты написал:** _{description[:150]}..._

🎨 **Стиль:** {style.upper()}
🎭 **Настроение:** {mood}

✨ **Эффекты:** {effects_map.get(style, effects_map['aesthetic'])}
🎵 **Музыка:** {music_map.get(style, music_map['aesthetic'])}

📋 **ПЛАН ДЕЙСТВИЙ:**
1. Выбери программу для монтажа (смотри раздел приложений)
2. Найди похожую музыку
3. Собери материалы под свою идею
4. Монтируй под бит с указанными эффектами

🔥 **Удачи с эдитом!**"""

def format_idea(idea: Dict) -> str:
    """Форматирует идею для вывода"""
    return f"""🎬 **{idea['title']}**

📝 **Описание:** {idea['description']}

🎨 **Стиль:** {idea['style']}
🎭 **Настроение:** {idea['mood']}

🎵 **Музыка:** {idea['music']}
✨ **Эффекты:** {', '.join(idea['effects'])}
🔄 **Переходы:** {', '.join(idea['transitions'])}
⏱️ **Длительность:** {idea['duration']}
📊 **Сложность:** {idea['difficulty']}

❤️ **Лайков:** {idea['likes']}"""

def format_apps_list(apps: List[Dict], title: str) -> str:
    """Форматирует список приложений для вывода"""
    if not apps:
        return f"❌ {title} не найдены"
    
    text = f"**{title}**\n\n"
    for app in apps:
        text += f"{app['name']}\n"
        text += f"📱 {app['platform']}\n"
        text += f"📌 {app['desc']}\n\n"
    
    return text

# ============================================
# ОБРАБОТЧИКИ КОМАНД
# ============================================

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    try:
        await message.answer(
            f"🎬 **EditBot**\n\n"
            f"Привет, {message.from_user.first_name}!\n\n"
            f"📌 **Что я умею:**\n"
            f"• 💡 {len(storage.ideas)} готовых идей для едитов\n"
            f"• 🎨 Искать идеи по стилям\n"
            f"• 🎭 Искать по настроению\n"
            f"• ✨ Генерировать идеи по твоему описанию\n"
            f"• ❤️ Сохранять понравившиеся идеи\n"
            f"• 📱 30+ приложений для фото, видео и аудио\n\n"
            f"👇 **Используй кнопки внизу**",
            reply_markup=get_main_keyboard()
        )
        logger.info(f"User {message.from_user.id} started bot")
    except Exception as e:
        logger.error(f"Error in start: {e}")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "📖 **Помощь по командам**\n\n"
        "💡 **Все идеи** - список всех идей\n"
        "🎨 **По стилю** - идеи по стилям\n"
        "🎭 **По настроению** - идеи по настроению\n"
        "🎲 **Случайная идея** - случайная идея\n"
        "🔥 **Популярные идеи** - самые лайкаемые\n"
        "❤️ **Избранное** - твои сохраненные идеи\n\n"
        "🎬 **Видео приложения** - программы для монтажа видео\n"
        "📸 **Фото приложения** - редакторы фото\n"
        "🎵 **Аудио приложения** - для работы со звуком\n\n"
        "✨ **По описанию** - сгенерировать идею",
        reply_markup=get_main_keyboard()
    )

# ============================================
# ОБРАБОТЧИКИ ТЕКСТОВЫХ КНОПОК
# ============================================

@dp.message(F.text == "💡 Все идеи")
async def show_all_ideas(message: Message):
    """Показать все идеи"""
    try:
        text = "💡 **Все идеи для едитов:**\n\n"
        for idea in storage.ideas.values():
            text += f"• {idea['title']} - ❤️ {idea['likes']}\n"
        
        await message.answer(text[:1000])
    except Exception as e:
        logger.error(f"Error in show_all_ideas: {e}")
        await message.answer("❌ Ошибка загрузки идей")

@dp.message(F.text == "🎨 По стилю")
async def show_styles(message: Message):
    """Показать выбор стилей"""
    await message.answer(
        "🎨 **Выбери стиль:**",
        reply_markup=get_style_keyboard()
    )

@dp.message(F.text == "🎭 По настроению")
async def show_moods(message: Message):
    """Показать выбор настроений"""
    await message.answer(
        "🎭 **Выбери настроение:**",
        reply_markup=get_mood_keyboard()
    )

@dp.message(F.text == "🎲 Случайная идея")
async def random_idea(message: Message):
    """Показать случайную идею"""
    try:
        idea = random.choice(list(storage.ideas.values()))
        await message.answer(
            format_idea(idea),
            reply_markup=get_idea_buttons(idea["id"], message.from_user.id)
        )
    except Exception as e:
        logger.error(f"Error in random_idea: {e}")
        await message.answer("❌ Ошибка")

@dp.message(F.text == "🔥 Популярные идеи")
async def popular_ideas(message: Message):
    """Показать популярные идеи"""
    try:
        popular = storage.get_popular_ideas(10)
        text = "🔥 **Самые популярные идеи:**\n\n"
        for idea in popular:
            text += f"• {idea['title']} - ❤️ {idea['likes']}\n"
        
        await message.answer(text)
    except Exception as e:
        logger.error(f"Error in popular_ideas: {e}")
        await message.answer("❌ Ошибка")

@dp.message(F.text == "❤️ Избранное")
async def show_favorites(message: Message):
    """Показать избранное пользователя"""
    try:
        favorites = storage.get_favorites(message.from_user.id)
        
        if not favorites:
            await message.answer(
                "❤️ **У тебя пока нет избранных идей**\n\n"
                "Нажимай ❤️ под идеями, чтобы сохранить их сюда"
            )
            return
        
        text = "❤️ **Твои избранные идеи:**\n\n"
        for idea in favorites[:5]:
            text += f"• {idea['title']} - ❤️ {idea['likes']}\n"
        
        await message.answer(text)
    except Exception as e:
        logger.error(f"Error in show_favorites: {e}")
        await message.answer("❌ Ошибка")

@dp.message(F.text == "🎬 Видео приложения")
async def show_video_apps(message: Message):
    """Показать видео приложения"""
    try:
        text = format_apps_list(storage.video_apps, "🎬 **Видео приложения:**")
        await message.answer(text[:4000], disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error in show_video_apps: {e}")
        await message.answer("❌ Ошибка")

@dp.message(F.text == "📸 Фото приложения")
async def show_photo_apps(message: Message):
    """Показать фото приложения"""
    try:
        text = format_apps_list(storage.photo_apps, "📸 **Фото приложения:**")
        await message.answer(text[:4000], disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error in show_photo_apps: {e}")
        await message.answer("❌ Ошибка")

@dp.message(F.text == "🎵 Аудио приложения")
async def show_audio_apps(message: Message):
    """Показать аудио приложения"""
    try:
        text = format_apps_list(storage.audio_apps, "🎵 **Аудио приложения:**")
        await message.answer(text[:4000], disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Error in show_audio_apps: {e}")
        await message.answer("❌ Ошибка")

@dp.message(F.text == "✨ По описанию")
async def create_by_description(message: Message, state: FSMContext):
    """Начать создание по описанию"""
    await message.answer(
        "✨ **Создание идеи по описанию**\n\n"
        "Опиши, что ты хочешь сделать. Например:\n"
        "• `хочу грустный эдит про расставание`\n"
        "• `нужен энергичный монтаж для игры`\n"
        "• `сделать романтичное видео для девушки`\n\n"
        "Или отправь /cancel для отмены"
    )
    await state.set_state(EditStates.waiting_for_description)

@dp.message(EditStates.waiting_for_description)
async def process_description(message: Message, state: FSMContext):
    """Обработка описания"""
    try:
        if message.text == "/cancel":
            await state.clear()
            await message.answer(
                "❌ Создание отменено",
                reply_markup=get_main_keyboard()
            )
            return
        
        if len(message.text) < 10:
            await message.answer("❌ Опиши подробнее (минимум 10 символов)")
            return
        
        result = generate_idea_from_description(message.text)
        await message.answer(result)
        await state.clear()
        
    except Exception as e:
        logger.error(f"Error in process_description: {e}")
        await state.clear()
        await message.answer("❌ Ошибка генерации")

@dp.message(F.text == "ℹ️ Помощь")
async def show_help(message: Message):
    """Показать помощь"""
    await cmd_help(message)

# ============================================
# ОБРАБОТЧИКИ INLINE КНОПОК
# ============================================

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Вернуться в главное меню"""
    await callback.message.delete()
    await callback.message.answer(
        "📌 **Главное меню:**",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("style_"))
async def process_style(callback: CallbackQuery):
    """Обработка выбора стиля"""
    try:
        style = callback.data.replace("style_", "")
        ideas = storage.get_ideas_by_style(style)
        
        if not ideas:
            await callback.answer(f"❌ Нет идей в стиле {style}")
            return
        
        # Показываем первую идею
        idea = ideas[0]
        await callback.message.edit_text(
            format_idea(idea),
            reply_markup=get_idea_buttons(idea["id"], callback.from_user.id)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in process_style: {e}")
        await callback.answer("❌ Ошибка")

@dp.callback_query(F.data.startswith("mood_"))
async def process_mood(callback: CallbackQuery):
    """Обработка выбора настроения"""
    try:
        mood = callback.data.replace("mood_", "")
        ideas = storage.get_ideas_by_mood(mood)
        
        if not ideas:
            await callback.answer(f"❌ Нет идей с настроением {mood}")
            return
        
        # Показываем первую идею
        idea = ideas[0]
        await callback.message.edit_text(
            format_idea(idea),
            reply_markup=get_idea_buttons(idea["id"], callback.from_user.id)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in process_mood: {e}")
        await callback.answer("❌ Ошибка")

@dp.callback_query(F.data.startswith("fav_"))
async def add_to_favorites(callback: CallbackQuery):
    """Добавить в избранное"""
    try:
        idea_id = int(callback.data.split("_")[1])
        
        if storage.add_favorite(callback.from_user.id, idea_id):
            await callback.answer("❤️ Добавлено в избранное!")
        else:
            await callback.answer("❌ Уже в избранном")
        
        # Обновляем кнопки
        await callback.message.edit_reply_markup(
            reply_markup=get_idea_buttons(idea_id, callback.from_user.id)
        )
        
    except Exception as e:
        logger.error(f"Error in add_to_favorites: {e}")
        await callback.answer("❌ Ошибка")

@dp.callback_query(F.data.startswith("unfav_"))
async def remove_from_favorites(callback: CallbackQuery):
    """Удалить из избранного"""
    try:
        idea_id = int(callback.data.split("_")[1])
        
        if storage.remove_favorite(callback.from_user.id, idea_id):
            await callback.answer("💔 Удалено из избранного")
        else:
            await callback.answer("❌ Не найдено")
        
        # Обновляем кнопки
        await callback.message.edit_reply_markup(
            reply_markup=get_idea_buttons(idea_id, callback.from_user.id)
        )
        
    except Exception as e:
        logger.error(f"Error in remove_from_favorites: {e}")
        await callback.answer("❌ Ошибка")

@dp.callback_query(F.data.startswith("copy_"))
async def copy_idea(callback: CallbackQuery):
    """Скопировать идею"""
    try:
        idea_id = int(callback.data.split("_")[1])
        
        if idea_id in storage.ideas:
            idea = storage.ideas[idea_id]
            await callback.message.answer(
                f"📋 **{idea['title']}**\n\n{idea['description']}"
            )
            await callback.answer("✅ Скопировано!")
        else:
            await callback.answer("❌ Идея не найдена")
            
    except Exception as e:
        logger.error(f"Error in copy_idea: {e}")
        await callback.answer("❌ Ошибка")

# ============================================
# ОБРАБОТКА НЕИЗВЕСТНЫХ СООБЩЕНИЙ
# ============================================

@dp.message()
async def handle_unknown(message: Message):
    """Обработка всех остальных сообщений"""
    await message.answer(
        "❓ Я не понимаю эту команду.\n"
        "Используй кнопки внизу 👇",
        reply_markup=get_main_keyboard()
    )

# ============================================
# ЗАПУСК БОТА
# ============================================

async def main():
    """Главная функция запуска"""
    try:
        print("\n" + "="*60)
        print("✅ EditBot v6.2 - 20+ ИДЕЙ")
        print("="*60)
        print("📱 Бот запущен и готов к работе!")
        print("📊 Статистика:")
        print(f"   • Идей: {len(storage.ideas)}")
        print(f"   • Видео приложений: {len(storage.video_apps)}")
        print(f"   • Фото приложений: {len(storage.photo_apps)}")
        print(f"   • Аудио приложений: {len(storage.audio_apps)}")
        print("="*60)
        print("🎯 Функции:")
        print("   • 💡 Все идеи (20+)")
        print("   • 🎨 Поиск по стилям")
        print("   • 🎭 Поиск по настроению")
        print("   • 🎲 Случайная идея")
        print("   • 🔥 Популярные идеи")
        print("   • ❤️ Избранное")
        print("   • 🎬 Видео приложения")
        print("   • 📸 Фото приложения")
        print("   • 🎵 Аудио приложения")
        print("   • ✨ Генерация по описанию")
        print("="*60 + "\n")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
