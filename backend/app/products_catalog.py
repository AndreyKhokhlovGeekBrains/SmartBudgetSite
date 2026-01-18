# backend/app/products_catalog.py
from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class Product:
    slug: str
    title_key: str
    subtitle_key: str
    highlights_keys: List[str]
    cta_key: str


PRODUCTS: List[Product] = [
    Product(
        slug="smartbudget",
        title_key="product_smartbudget_title",
        subtitle_key="product_smartbudget_subtitle",
        highlights_keys=[
            "product_smartbudget_h1",  # Step-by-step planning (walkthrough)
            "product_smartbudget_h2",  # Plan vs Fact control
            "product_smartbudget_h3",  # Utilities micro-budget + payment control
            "product_smartbudget_h4",  # Credit card / cash-gap handling
            "product_smartbudget_h5",  # Personal projects sub-budgets
            "product_smartbudget_h6",  # Built-in analytics
        ],
        cta_key="product_cta_buy",
    ),
]


def products_index() -> List[Dict]:
    # return [p.__dict__ for p in PRODUCTS]
    return [
        {
            "slug": p.slug,
            "title_key": p.title_key,
            "subtitle_key": p.subtitle_key,
            "highlights_keys": p.highlights_keys,
            "cta_key": p.cta_key,
        }
        for p in PRODUCTS
    ]


def product_by_slug(slug: str) -> Product | None:
    return next((p for p in PRODUCTS if p.slug == slug), None)
