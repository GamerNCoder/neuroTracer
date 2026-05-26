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

# Extra patterns for larger corpora (e.g. 1000+ posts)
EXTRA_CATEGORIES: tuple[Category, ...] = (
    Category("tech-alt", "Technology (alt)", "*.blogspot.com/*software*", "Dev, apps"),
    Category("travel-alt", "Travel (alt)", "*.blogspot.com/*trip*", "Travel diaries"),
    Category("food-alt", "Food (alt)", "*.blogspot.com/*cooking*", "Cooking blogs"),
    Category("parenting-alt", "Parenting (alt)", "*.blogspot.com/*baby*", "Parenting"),
    Category("politics-alt", "Politics (alt)", "*.blogspot.com/*election*", "Elections"),
    Category("sports-alt", "Sports (alt)", "*.blogspot.com/*football*", "Sports"),
    Category("music-alt", "Music (alt)", "*.blogspot.com/*band*", "Music"),
    Category("photo-alt", "Photography (alt)", "*.blogspot.com/*camera*", "Photo"),
    Category("journal", "Journal", "*.blogspot.com/*journal*", "Journals"),
    Category("finance-alt", "Finance (alt)", "*.blogspot.com/*invest*", "Investing"),
    Category("health-alt", "Health (alt)", "*.blogspot.com/*fitness*", "Fitness"),
    Category("fashion-alt", "Fashion (alt)", "*.blogspot.com/*style*", "Style"),
    Category("gaming-alt", "Gaming (alt)", "*.blogspot.com/*gaming*", "Gaming"),
    Category("edu-alt", "Education (alt)", "*.blogspot.com/*student*", "Students"),
    Category("science-alt", "Science (alt)", "*.blogspot.com/*research*", "Research"),
    Category("lit", "Literature", "*.blogspot.com/*novel*", "Books/fiction"),
    Category("film-alt", "Film (alt)", "*.blogspot.com/*film*", "Film"),
    Category("pets-alt", "Pets (alt)", "*.blogspot.com/*dog*", "Dogs/cats"),
    Category("diy-alt", "DIY (alt)", "*.blogspot.com/*handmade*", "Crafts"),
    Category("faith-alt", "Faith (alt)", "*.blogspot.com/*faith*", "Faith"),
    Category("lj-general", "LiveJournal", "*.livejournal.com/*", "LiveJournal posts"),
)

ALL_CATEGORIES: tuple[Category, ...] = CATEGORIES + EXTRA_CATEGORIES


def categories_slice(max_categories: int | None = None, *, extended: bool = False) -> list[Category]:
    pool = ALL_CATEGORIES if extended else CATEGORIES
    if max_categories is None or max_categories >= len(pool):
        return list(pool)
    return list(pool[:max_categories])
