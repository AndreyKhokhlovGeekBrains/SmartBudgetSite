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

    },
    "ru": {
        "brand_name": "Андрей Хохлов",
        "nav_about": "Обо мне",
        "nav_products": "Продукты",
        "about_h1": "Обо мне",
        "products_h1": "Продукты",

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
