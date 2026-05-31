from __future__ import annotations

from typing import Any

LANG_RU = "ru"
LANG_EN = "en"

TRANSLATIONS: dict[str, dict[str, str]] = {
    LANG_RU: {
        # --- Start / Welcome ---
        "welcome": (
            "Привет, {name}! 👋\n\n"
            "Я продвинутый AI-помощник для решения задач. Я могу помочь с:\n"
            "• Математика и олимпиадные задачи\n"
            "• Физика, Химия, Программирование\n"
            "• Анализ изображений с OCR\n"
            "• Пошаговые объяснения\n\n"
            "Выбери опцию ниже, чтобы начать:"
        ),
        "help": (
            "🤖 **AI Solver Bot — Помощь**\n\n"
            "**Команды:**\n"
            "/start — Запустить бота\n"
            "/solve — Решить задачу\n"
            "/image — Отправить изображение\n"
            "/help — Показать помощь\n"
            "/profile — Профиль и статистика\n\n"
            "**Как использовать:**\n"
            "1. Напиши или вставь текст задачи\n"
            "2. Загрузи изображение задачи\n"
            "3. Выбери предмет для точности\n\n"
            "**Поддерживается:** Математика, Физика, Химия, Программирование и другое!"
        ),
        "main_menu": "Главное меню — выбери опцию:",
        "action_cancelled": "Действие отменено. Возврат в меню.",

        # --- Solve ---
        "solve_prompt": "Отправь мне задачу, которую нужно решить. Можно написать текст или загрузить изображение.",
        "select_subject": "Выбери предмет для более точного результата:",
        "analyzing": "🧠 Анализирую задачу...\nЭто может занять немного времени.",
        "ai_error": "❌ {error}\n\nУбедись, что API-ключи AI-провайдера указаны в .env",
        "validation_note": "\n\n⚠️ *Уверенность проверки: {confidence:.0%}*",
        "processing_error": "❌ Произошла ошибка: {error}",
        "something_wrong": "Что-то пошло не так. Начни заново.",
        "wait_processing": "Подожди, я ещё обрабатываю предыдущий запрос...",
        "too_long": "Задача слишком длинная. Максимум {max} символов.",
        "send_text_or_image": "Отправь текст или изображение.",

        # --- Image ---
        "image_prompt": "Отправь изображение задачи. Поддерживаемые форматы: PNG, JPG, JPEG, BMP, TIFF, WebP",
        "processing_image": "📸 Обрабатываю изображение через OCR...",
        "no_text_found": "❌ Не удалось извлечь текст из изображения. Попробуй более чёткое изображение.",
        "extracted_text": "📝 **Извлечённый текст:**\n{text}\n\nУверенность: {confidence:.0%}\n{review}\n\n🧠 Теперь решаю...",
        "low_confidence": "⚠️ Низкая уверенность — результат может требовать проверки.",
        "unsupported_format": "Неподдерживаемый формат: {ext}. Поддерживаются: {formats}",
        "file_too_large": "Файл слишком большой. Максимум: {max_size}MB",
        "error_ocr": "❌ Ошибка: {error}",

        # --- Profile ---
        "profile_title": "👤 **Твой профиль**\n\n"
        "ID: `{id}`\n"
        "Username: @{username}\n"
        "Статус: 🆓 Активен\n"
        "Язык: {language}\n\n"
        "📊 **Статистика:**\n"
        "Всего запросов: {total_requests}\n"
        "Сегодня: {daily_requests}\n"
        "Всего токенов: {total_tokens}\n\n"
        "📅 Регистрация: {created_at}",
        "stats_title": "📊 **Детальная статистика**\n\n"
        "• Всего запросов: {total_requests}\n"
        "• Запросов сегодня: {daily_requests}\n"
        "• Месячных токенов: {monthly_tokens}\n"
        "• Всего токенов: {total_tokens}\n"
        "• Диалогов: {conversations_count}\n"
        "• Рефералов: {referral_count}\n\n"
        "⚡ Дневной лимит: {daily_limit}\n"
        "📅 Месячный лимит: {monthly_limit}",
        "settings_title": "⚙️ **Настройки**\n\nНастрой свой опыт:",
        "daily_reset": "✅ Дневное использование сброшено.",

        # --- Languages ---
        "lang_ru": "Русский",
        "lang_en": "English",
        "status_active": "🆓 Активен",

        # --- Subject names ---
        "subject_mathematics": "Математика",
        "subject_physics": "Физика",
        "subject_chemistry": "Химия",
        "subject_programming": "Программирование",
        "subject_general": "Общее",

        # --- Keyboard buttons ---
        "btn_solve": "🧮 Решить задачу",
        "btn_image": "📸 Загрузить фото",
        "btn_history": "💬 История",
        "btn_profile": "👤 Профиль",
        "btn_help": "❓ Помощь",
        "btn_back": "↩ Назад",
        "btn_cancel": "Отмена",
        "btn_confirm": "✅ Подтвердить",
        "btn_stats": "📊 Статистика",
        "btn_reset": "🔄 Сброс",
        "btn_settings": "⚙️ Настройки",
        "btn_menu": "↩ Меню",
        "btn_language": "🌐 Язык",
        "btn_level": "📚 Уровень объяснений",
        "btn_provider": "🤖 AI-провайдер",
        "btn_usage": "📝 Как использовать",
        "btn_subjects": "📚 Предметы",
        "btn_tips": "💡 Советы",
        "btn_prev": "◀ Назад",
        "btn_next": "Вперёд ▶",

        # --- Common ---
        "n_a": "N/A",
        "or": "или",

        # --- History ---
        "history_empty": "**История диалогов**\n\nДиалогов пока нет. Начни с решения задачи!",
        "history_title": "💬 **Недавние диалоги**",
        "history_you": "👤 Ты",
        "history_bot": "🤖 Бот",
        "history_footer": "Используй /solve, чтобы начать новый диалог.",
    },
    LANG_EN: {
        # --- Start / Welcome ---
        "welcome": (
            "Hello, {name}! 👋\n\n"
            "I am an advanced AI solver bot. I can help you with:\n"
            "• Mathematics & Olympiad problems\n"
            "• Physics, Chemistry, Programming\n"
            "• Image analysis with OCR\n"
            "• Step-by-step explanations\n\n"
            "Select an option below to get started:"
        ),
        "help": (
            "🤖 **AI Solver Bot Help**\n\n"
            "**Commands:**\n"
            "/start — Start the bot\n"
            "/solve — Solve a problem\n"
            "/image — Upload an image\n"
            "/help — Show this help\n"
            "/profile — Your profile & stats\n\n"
            "**How to use:**\n"
            "1. Type or paste your problem\n"
            "2. Upload an image of the problem\n"
            "3. Select a subject for better results\n\n"
            "**Supported:** Math, Physics, Chemistry, Programming, and more!"
        ),
        "main_menu": "Main Menu — Select an option:",
        "action_cancelled": "Action cancelled. Returning to menu.",

        # --- Solve ---
        "solve_prompt": "Please send me the problem you want me to solve. You can type it or upload an image.",
        "select_subject": "Select the subject area for better results:",
        "analyzing": "🧠 Analyzing your problem...\nThis may take a moment.",
        "ai_error": "❌ {error}\n\nMake sure AI provider API keys are set in .env",
        "validation_note": "\n\n⚠️ *Validation confidence: {confidence:.0%}*",
        "processing_error": "❌ Sorry, I encountered an error: {error}",
        "something_wrong": "Something went wrong. Please start again.",
        "wait_processing": "Please wait, I'm still processing your previous request...",
        "too_long": "Problem too long. Max {max} characters.",
        "send_text_or_image": "Please send text or an image.",

        # --- Image ---
        "image_prompt": "Please send me an image of the problem. Supported formats: PNG, JPG, JPEG, BMP, TIFF, WebP",
        "processing_image": "📸 Processing image with OCR...",
        "no_text_found": "❌ Could not extract text from the image. Please try with a clearer image.",
        "extracted_text": "📝 **Extracted Text:**\n{text}\n\nConfidence: {confidence:.0%}\n{review}\n\n🧠 Now solving...",
        "low_confidence": "⚠️ Low confidence — results may need review.",
        "unsupported_format": "Unsupported format: {ext}. Supported: {formats}",
        "file_too_large": "File too large. Max size: {max_size}MB",
        "error_ocr": "❌ Error: {error}",

        # --- Profile ---
        "profile_title": "👤 **Your Profile**\n\n"
        "ID: `{id}`\n"
        "Username: @{username}\n"
        "Status: 🆓 Active\n"
        "Language: {language}\n\n"
        "📊 **Statistics:**\n"
        "Total requests: {total_requests}\n"
        "Today: {daily_requests}\n"
        "Tokens used: {total_tokens}\n\n"
        "📅 Joined: {created_at}",
        "stats_title": "📊 **Detailed Stats**\n\n"
        "• Total Requests: {total_requests}\n"
        "• Daily Requests: {daily_requests}\n"
        "• Monthly Tokens: {monthly_tokens}\n"
        "• Total Tokens: {total_tokens}\n"
        "• Conversations: {conversations_count}\n"
        "• Referrals: {referral_count}\n\n"
        "⚡ Daily limit: {daily_limit}\n"
        "📅 Monthly limit: {monthly_limit}",
        "settings_title": "⚙️ **Settings**\n\nCustomize your experience:",
        "daily_reset": "✅ Daily usage has been reset.",

        # --- Languages ---
        "lang_ru": "Русский",
        "lang_en": "English",
        "status_active": "🆓 Active",

        # --- Subject names ---
        "subject_mathematics": "Mathematics",
        "subject_physics": "Physics",
        "subject_chemistry": "Chemistry",
        "subject_programming": "Programming",
        "subject_general": "General",

        # --- Keyboard buttons ---
        "btn_solve": "🧮 Solve Problem",
        "btn_image": "📸 Upload Image",
        "btn_history": "💬 History",
        "btn_profile": "👤 Profile",
        "btn_help": "❓ Help",
        "btn_back": "↩ Back",
        "btn_cancel": "Cancel",
        "btn_confirm": "✅ Confirm",
        "btn_stats": "📊 Stats",
        "btn_reset": "🔄 Reset Daily",
        "btn_settings": "⚙️ Settings",
        "btn_menu": "↩ Menu",
        "btn_language": "🌐 Language",
        "btn_level": "📚 Explanation Level",
        "btn_provider": "🤖 AI Provider",
        "btn_usage": "📝 How to Use",
        "btn_subjects": "📚 Supported Subjects",
        "btn_tips": "💡 Tips",
        "btn_prev": "◀ Prev",
        "btn_next": "Next ▶",

        # --- Common ---
        "n_a": "N/A",
        "or": "or",

        # --- History ---
        "history_empty": "**Conversation History**\n\nNo conversations yet. Start by solving a problem!",
        "history_title": "💬 **Recent Conversations**",
        "history_you": "👤 You",
        "history_bot": "🤖 Bot",
        "history_footer": "Use /solve to start a new conversation.",
    },
}

_ALIASES: dict[str, str] = {
    "ru": LANG_RU,
    "uk": LANG_RU,
    "be": LANG_RU,
    "en": LANG_EN,
}


def resolve_lang(code: str | None) -> str:
    if code and code in _ALIASES:
        return _ALIASES[code]
    return LANG_EN


def _(key: str, lang: str = LANG_EN, **kwargs: Any) -> str:
    translations = TRANSLATIONS.get(lang, TRANSLATIONS[LANG_EN])
    template = translations.get(key, key)
    if kwargs:
        return template.format(**kwargs)
    return template
