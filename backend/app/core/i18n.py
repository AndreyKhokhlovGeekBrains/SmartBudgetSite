from __future__ import annotations

from typing import Final
from fastapi import Request
from starlette.responses import Response

SUPPORTED_LANGS: Final[set[str]] = {"en", "ru"}
DEFAULT_LANG: Final[str] = "en"
COOKIE_NAME: Final[str] = "sb_lang"


TRANSLATIONS: Final[dict[str, dict[str, str]]] = {
    "en": {
        "brand_name": "Andrey Khokhlov",
        "nav_about": "About",
        "nav_products": "Products",
        "about_h1": "About me",
        "products_h1": "Products",
        "products_subtitle": "Thoughtfully designed products to plan, control, and improve your personal finances.",
        "about_p": (
            "I help turn data and technology into clear, practical solutions "
            "for both life and business. My goal is not just to build reports "
            "or write code, but to simplify processes, eliminate manual work, "
            "and give people a sense of control over their systems and numbers."
        ),

        "about_p2": (
            "I started my career in finance (ex-EY, ACCA/FCCA), and over time "
            "moved deeper into analytics, automation, and development. Today "
            "I work as a BI developer, combining SQL, Power BI, Tableau, Python, "
            "and Excel/VBA with a strong focus on performance and real-world value."
        ),

        "about_p3": (
            "I am also passionate about automating everyday life — smart home "
            "systems, sensors, scenarios, and Home Assistant. I like systems "
            "that work quietly, logically, and without constant manual control. "
            "The same principles guide my professional work."
        ),

        "about_b1": "BI developer with strong finance background (ex-EY, ACCA/FCCA).",
        "about_b2": "SQL Server, Power BI, Tableau — performance-focused approach.",
        "about_b3": "Building SmartBudget: Excel + VBA product with a companion web app.",

        "footer_copy": "Andrey Khokhlov",
        "link_tg_url": "https://t.me/NebulaMaverick?start=site",
        "link_wa_url": "https://wa.me/79268272465",
        "link_fb_url": "https://facebook.com/andrey.khokhlov.2025",
        "link_vk_url": "https://vk.com/id7384755",
        "link_email_url": "mailto:khokhlov.a.a@gmail.com",
        "link_li_url": "https://www.linkedin.com/in/andrey-khokhlov-acca-25315816a",

        "features_h2": "What I do",
        "feature_1_h": "Analytics & BI",
        "feature_1_p": "Designing efficient data models, dashboards, and reports that answer real business questions.",
        "feature_2_h": "Automation",
        "feature_2_p": "Automating finance and data workflows using Python, SQL, and Excel/VBA.",
        "feature_3_h": "Products",
        "feature_3_p": "Building practical tools like SmartBudget that people actually use.",

        "product_smartbudget_title": "SmartBudget",
        "product_smartbudget_subtitle": "An Excel-based personal budget: plan the year, track actuals, and spot cash gaps before they happen.",

        "product_smartbudget_h1": "Guided, step-by-step budget planning with built-in tips",
        "product_smartbudget_h2": "Plan vs Actual control to catch overspending early",
        "product_smartbudget_h3": "Utilities micro-budget: plan + actual + payment checklist",
        "product_smartbudget_h4": "Credit card cash-gap handling with a clear payoff plan",
        "product_smartbudget_h5": "Personal projects as sub-budgets (trips, goals, big plans)",
        "product_smartbudget_h6": "Built-in analytics: charts and detailed variance view",

        "product_cta_buy": "Learn more",

        "sb_lp_subtitle": "Plan the year, track actuals, and spot cash gaps before they happen.",

        "sb_lp_cta_primary": "Learn more",
        "sb_lp_cta_secondary": "See screenshots",

        "sb_lp_b1": "Detect cash gaps months in advance",
        "sb_lp_b2": "Plan vs Actual with variance tracking",
        "sb_lp_b3": "Microbudgets for utilities and personal projects",

        "sb_lp_buy_h2": "Get SmartBudget",
        "sb_lp_buy_p": "Purchase and download the latest version.",

        "sb_shot_1": "Plan & cashflow overview",
        "sb_shot_2": "Plan vs Actual (variance)",
        "sb_shot_3": "Utilities micro-budget",

# --- SmartBudget landing (EN) ---
        "sb_landing_title": "Plan, track, and understand your money — in one Excel file",
        "sb_landing_lead": "SmartBudget is a practical budgeting system with clear structure, plan vs fact control, and simple analytics.",
        "sb_landing_cta_primary": "View product",
        "sb_landing_cta_consult": "Paid консультация в Telegram",
        "sb_landing_note": "Works locally in Excel. No data leaves your computer.",

        "sb_nav_title": "Everything important — one click away",
        "sb_nav_p1": "When a budget grows, searching for the right sheet steals focus and time.",
        "sb_nav_p2": "A single navigation panel gives instant access to Plan, Fact, Comparison, Utilities, and more — without extra clicks.",
        "sb_nav_alt": "SmartBudget navigation panel",

        "sb_inputs_title": "All key settings in one place",
        "sb_inputs_p1": "Budget setup is often scattered: limits, accounts, cards, currencies — easy to miss something.",
        "sb_inputs_p2": "The Inputs sheet keeps core parameters together, so the budget starts from a clean and consistent base.",
        "sb_inputs_alt": "SmartBudget inputs sheet",

        "sb_plan_title": "A budget model, not a random list of expenses",
        "sb_plan_p1": "Simple spreadsheets mix everything together, and monthly results become a surprise.",
        "sb_plan_p2": "The Plan sheet structures cash flows so you can see the outcome of each month and adjust early.",
        "sb_plan_alt": "SmartBudget plan sheet",

        "sb_savings_viz_title": "See progress, not just numbers",
        "sb_savings_viz_p1": "Tables are hard to read at a glance — growth gets lost in rows and columns.",
        "sb_savings_viz_p2": "Clear charts show end-of-month balances and savings structure across the year.",
        "sb_savings_viz_alt": "Savings charts",

        "sb_fact_title": "Spot cash gaps before they hurt",
        "sb_fact_p1": "Real life differs from the plan — unexpected expenses show up and create stress.",
        "sb_fact_p2": "Fact mirrors Plan, so deviations are immediately visible and you can act in advance.",
        "sb_fact_alt": "SmartBudget fact sheet",

        "sb_utilities_title": "Never forget an important bill",
        "sb_utilities_p1": "Utilities come from different providers and at different times — it’s easy to miss one.",
        "sb_utilities_p2": "Track planned vs paid bills by month and always know what is already covered.",
        "sb_utilities_alt": "Utilities payments table",

        "sb_compare_title": "Know exactly where the budget deviates",
        "sb_compare_p1": "A monthly total may look fine, while the real reasons stay hidden.",
        "sb_compare_p2": "Comparison provides line-by-line plan vs fact with absolute and percent variance for each month.",
        "sb_compare_alt": "Plan vs fact comparison table",

        "sb_consult_title": "Need help setting it up for your life?",
        "sb_consult_p": "I offer paid 1:1 консультации: setup, workflow, and interpreting results — via Telegram.",
        "sb_consult_cta": "Message me on Telegram",

        "sb_landing_cta_buy": "Buy SmartBudget",
        "sb_final_cta_title": "Ready to take control of your budget?",

    },
    "ru": {
        "brand_name": "Андрей Хохлов",
        "nav_about": "Обо мне",
        "nav_products": "Продукты",
        "about_h1": "Обо мне",
        "products_h1": "Продукты",
        "products_subtitle": "Продуманные продукты для планирования, контроля и улучшения личных финансов.",

        "about_p": (
            "Я помогаю превращать данные и технологии в понятные и практичные решения "
            "для жизни и бизнеса. Для меня важно не просто сделать отчёт или написать код, "
            "а упростить процессы, убрать ручной труд и дать человеку ощущение контроля "
            "над цифрами и системами."
        ),

        "about_p2": (
            "По образованию и опыту я финансист (ex-EY, ACCA/FCCA), но со временем "
            "ушёл глубже в аналитику, автоматизацию и разработку. Сейчас я работаю "
            "как BI-разработчик, сочетая SQL, Power BI, Tableau, Python и Excel/VBA "
            "с фокусом на производительность и практическую пользу."
        ),

        "about_p3": (
            "Отдельная часть моих интересов — автоматизация повседневной жизни: "
            "умный дом, датчики, сценарии и Home Assistant. Мне нравятся системы, "
            "которые работают тихо, логично и без постоянного ручного вмешательства. "
            "Тот же принцип я применяю и в профессиональной работе."
        ),
        "about_b1": "BI-разработчик с сильной финансовой базой (ex-EY, ACCA/FCCA).",
        "about_b2": "SQL Server, Power BI, Tableau — фокус на производительности.",
        "about_b3": "Делаю SmartBudget: продукт на Excel + VBA и сайт-компаньон.",

        "footer_copy": "Andrey Khokhlov",
        "link_tg_url": "https://t.me/NebulaMaverick?start=site",
        "link_wa_url": "https://wa.me/79268272465",
        "link_fb_url": "https://facebook.com/andrey.khokhlov.2025",
        "link_vk_url": "https://vk.com/id7384755",
        "link_email_url": "mailto:khokhlov.a.a@gmail.com",
        "link_li_url": "https://www.linkedin.com/in/andrey-khokhlov-acca-25315816a",

        "features_h2": "Чем я занимаюсь",
        "feature_1_h": "Аналитика и BI",
        "feature_1_p": "Проектирование моделей данных, дашбордов и отчетов для реальных бизнес-задач.",
        "feature_2_h": "Автоматизация",
        "feature_2_p": "Автоматизация финансовых и аналитических процессов на Python, SQL и Excel/VBA.",
        "feature_3_h": "Продукты",
        "feature_3_p": "Создание практичных продуктов, таких как SmartBudget.",

        "product_smartbudget_title": "SmartBudget",
        "product_smartbudget_subtitle": "Личный бюджет в Excel: планируй на год вперёд, контролируй факт, предотвращай кассовые разрывы.",

        "product_smartbudget_h1": "Пошаговое планирование бюджета (walkthrough с подсказками)",
        "product_smartbudget_h2": "План vs Факт: быстро видно перерасход и отклонения",
        "product_smartbudget_h3": "Коммуналка как микробюджет: план + факт + контроль оплат",
        "product_smartbudget_h4": "Кредитные карты: закрывай разрывы и планируй погашение",
        "product_smartbudget_h5": "Личные проекты: подбюджеты для поездок/ремонта/целей",
        "product_smartbudget_h6": "Встроенная аналитика: графики и детальный план-факт",

        "product_cta_buy": "Подробнее",

        "sb_lp_subtitle": "Планирование года, контроль факта и раннее выявление кассовых разрывов.",

        "sb_lp_cta_primary": "Подробнее",
        "sb_lp_cta_secondary": "Скриншоты",

        "sb_lp_b1": "Видно кассовые разрывы за месяцы вперёд",
        "sb_lp_b2": "План vs Факт с отклонениями и контролем перерасхода",
        "sb_lp_b3": "Микробюджеты: коммуналка и личные проекты",

        "sb_lp_buy_h2": "Получить SmartBudget",
        "sb_lp_buy_p": "Оплата и скачивание последней версии.",

        "sb_shot_1": "План и денежные потоки",
        "sb_shot_2": "План vs Факт (отклонения)",
        "sb_shot_3": "Микробюджет: коммуналка",

# --- SmartBudget landing (RU) ---
        "sb_landing_title": "Планируйте и контролируйте личный бюджет — в одном Excel-файле",
        "sb_landing_lead": "SmartBudget — практичная система бюджета: понятная структура, план-факт контроль и базовая аналитика.",
        "sb_landing_cta_primary": "Смотреть продукт",
        "sb_landing_cta_consult": "Платная консультация в Telegram",
        "sb_landing_note": "Работает локально в Excel. Данные никуда не отправляются.",

        "sb_nav_title": "Всё важное — в один клик",
        "sb_nav_p1": "Когда бюджет разрастается, поиск нужного раздела начинает мешать думать.",
        "sb_nav_p2": "Единая панель навигации даёт быстрый доступ к Плану, Факту, Сравнению, Коммуналке и другим разделам.",
        "sb_nav_alt": "Панель навигации SmartBudget",

        "sb_inputs_title": "Все настройки бюджета — в одном месте",
        "sb_inputs_p1": "Обычно параметры раскиданы по файлу: лимиты, счета, карты, валюты — легко что-то забыть.",
        "sb_inputs_p2": "Лист «Вводные данные» собирает базовые параметры в одной форме — бюджет начинается с чистой и понятной основы.",
        "sb_inputs_alt": "Лист «Вводные данные»",

        "sb_plan_title": "Система денежных потоков вместо хаотичной таблицы",
        "sb_plan_p1": "В обычных таблицах всё смешивается, и итог месяца становится сюрпризом.",
        "sb_plan_p2": "Лист «План» структурирует бюджет так, чтобы видеть результат каждого месяца и корректировать заранее.",
        "sb_plan_alt": "Лист «План»",

        "sb_savings_viz_title": "Видно прогресс, а не только цифры",
        "sb_savings_viz_p1": "Табличные итоги по месяцам трудно воспринимать: динамика теряется.",
        "sb_savings_viz_p2": "Графики показывают остатки на конец месяца и структуру сбережений в динамике года.",
        "sb_savings_viz_alt": "Графики сбережений",

        "sb_fact_title": "Кассовые разрывы видны заранее",
        "sb_fact_p1": "Факт почти всегда отличается от плана — внезапные траты создают стресс.",
        "sb_fact_p2": "Лист «Факт» повторяет структуру плана, поэтому отклонения сразу заметны и можно действовать заранее.",
        "sb_fact_alt": "Лист «Факт»",

        "sb_utilities_title": "Не забывайте оплачивать важные счета",
        "sb_utilities_p1": "Коммунальные счета приходят от разных поставщиков и в разное время — легко пропустить платёж.",
        "sb_utilities_p2": "Планируйте и отмечайте оплату по месяцам и всегда видите, что уже закрыто, а что требует внимания.",
        "sb_utilities_alt": "Коммунальные платежи",

        "sb_compare_title": "Постатейный план-факт контроль",
        "sb_compare_p1": "Общий итог месяца может выглядеть нормально, но причины отклонений остаются неочевидными.",
        "sb_compare_p2": "Лист «Сравнение» показывает суммы, отклонения и проценты по каждой статье в разрезе месяцев.",
        "sb_compare_alt": "Таблица сравнения План vs Факт",

        "sb_consult_title": "Нужна помощь с настройкой под вашу жизнь?",
        "sb_consult_p": "Делаю платные 1:1 консультации: настройка, процесс ведения бюджета и разбор результатов — в Telegram.",
        "sb_consult_cta": "Написать в Telegram",

        "sb_landing_cta_buy": "Купить SmartBudget",
        "sb_final_cta_title": "Готовы навести порядок в бюджете?",

    },
}


def get_lang(request: Request) -> str:
    # 1) explicit query param
    q = (request.query_params.get("lang") or "").lower()
    if q in SUPPORTED_LANGS:
        return q

    # 2) cookie
    c = (request.cookies.get(COOKIE_NAME) or "").lower()
    if c in SUPPORTED_LANGS:
        return c

    return DEFAULT_LANG


def set_lang_cookie(response: Response, lang: str) -> None:
    if lang in SUPPORTED_LANGS:
        response.set_cookie(
            key=COOKIE_NAME,
            value=lang,
            max_age=60 * 60 * 24 * 365,
            samesite="lax",
            httponly=False,
        )


def t(lang: str, key: str) -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS[DEFAULT_LANG]).get(key, key)
