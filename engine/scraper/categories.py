"""
Twenty blog topic categories for pre-2012 corpus collection.

Each category uses a Wayback CDX URL pattern (Blogspot was common pre-2012).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    slug: str
    name: str
    cdx_url_pattern: str
    description: str = ""


# Top 20 categories × 25 posts each = 500 target documents
CATEGORIES: tuple[Category, ...] = (
    Category("technology", "Technology", "*.blogspot.com/*tech*", "Software, gadgets, IT"),
    Category("travel", "Travel", "*.blogspot.com/*travel*", "Trips, destinations"),
    Category("food", "Food & Cooking", "*.blogspot.com/*recipe*", "Recipes, restaurants"),
    Category("parenting", "Parenting", "*.blogspot.com/*mom*", "Family, kids"),
    Category("politics", "Politics", "*.blogspot.com/*politic*", "News, opinions"),
    Category("sports", "Sports", "*.blogspot.com/*sport*", "Games, teams"),
    Category("music", "Music", "*.blogspot.com/*music*", "Bands, concerts"),
    Category("photography", "Photography", "*.blogspot.com/*photo*", "Cameras, images"),
    Category("personal", "Personal", "*.blogspot.com/*diary*", "Life, journals"),
    Category("finance", "Finance", "*.blogspot.com/*money*", "Investing, budgeting"),
    Category("health", "Health", "*.blogspot.com/*health*", "Wellness, fitness"),
    Category("fashion", "Fashion", "*.blogspot.com/*fashion*", "Style, clothing"),
    Category("gaming", "Gaming", "*.blogspot.com/*game*", "Video games"),
    Category("education", "Education", "*.blogspot.com/*school*", "Teaching, learning"),
    Category("science", "Science", "*.blogspot.com/*science*", "Research, nature"),
    Category("books", "Books", "*.blogspot.com/*book*", "Reading, reviews"),
    Category("movies", "Movies", "*.blogspot.com/*movie*", "Film, TV"),
    Category("pets", "Pets", "*.blogspot.com/*pet*", "Dogs, cats"),
    Category("diy", "DIY & Crafts", "*.blogspot.com/*craft*", "Handmade, projects"),
    Category("religion", "Faith", "*.blogspot.com/*church*", "Spirituality"),
)


def categories_slice(max_categories: int | None = None) -> list[Category]:
    if max_categories is None or max_categories >= len(CATEGORIES):
        return list(CATEGORIES)
    return list(CATEGORIES[:max_categories])
