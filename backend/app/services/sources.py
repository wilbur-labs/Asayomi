"""RSS / Web ニュースソース定義"""

RSS_SOURCES = [
    # --- 日本語ソース ---
    {
        "name": "NHK News Web",
        "url": "https://www.nhk.or.jp/rss/news/cat0.xml",
        "category": "総合",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "Yahoo!ニュース",
        "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml",
        "category": "総合",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "ITmedia",
        "url": "https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml",
        "category": "テクノロジー",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "Gigazine",
        "url": "https://gigazine.net/news/rss_2.0/",
        "category": "テクノロジー",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "東洋経済オンライン",
        "url": "https://toyokeizai.net/list/feed/rss",
        "category": "経済・ビジネス",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "BBC News Japan",
        "url": "https://feeds.bbci.co.uk/japanese/rss.xml",
        "category": "国際",
        "language": "ja",
        "enabled": True,
    },
    {
        "name": "Reuters Japan",
        "url": "https://assets.wor.jp/rss/rdf/reuters/top.rdf",
        "category": "国際",
        "language": "ja",
        "enabled": False,  # RSS 廃止済み
    },
    # --- 英語ソース（AI で日本語に翻訳） ---
    {
        "name": "The Japan Times",
        "url": "https://www.japantimes.co.jp/feed/",
        "category": "国際",
        "language": "en",
        "enabled": True,
    },
    {
        "name": "Yomiuri English",
        "url": "https://japannews.yomiuri.co.jp/feed/",
        "category": "国際",
        "language": "en",
        "enabled": True,
    },
]
