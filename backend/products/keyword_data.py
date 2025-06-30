# Comprehensive Keyword & Negative Keyword Mappings for All 10 Simulated Products

PRODUCT_KEYWORD_MAPPINGS = {
    "B0BQZ0Y4R5": { # Ergonomic Office Chair
        "product_name": "Ergonomic Office Chair",
        "primary_keywords": [
            "[ergonomic office chair]", "[adjustable desk chair]",
            "[computer chair ergonomic]", "[lumbar support office chair]"
        ],
        "general_search_terms": [
            "office chair", "comfortable chair for desk", "chair for back pain",
            "work from home chair", "gaming chair", "ergonomic seating", "desk accessories"
        ],
        "negative_keywords": [
            "[cheap office chair]", "[used office chair]", "[leather recliner]", "\"office chair parts\""
        ]
    },
    "B0CR00N0M0": { # Portable Bluetooth Speaker
        "product_name": "Portable Bluetooth Speaker",
        "primary_keywords": [
            "[portable bluetooth speaker]", "[waterproof speaker outdoor]",
            "[mini wireless speaker]", "[bluetooth speaker with bass]"
        ],
        "general_search_terms": [
            "bluetooth speaker", "portable speaker", "wireless audio", "outdoor sound system",
            "travel speaker", "party speaker", "small speaker"
        ],
        "negative_keywords": [
            "[smart speaker]", "[home theater speaker]", "[speaker stand]", "\"car audio speaker\""
        ]
    },
    "B0CR1A1B1C": { # Organic Green Tea Bags (100-ct)
        "product_name": "Organic Green Tea Bags (100-ct)",
        "primary_keywords": [
            "[organic green tea bags]", "[100 count green tea]",
            "[loose leaf green tea organic]", "[detox green tea]" # Assuming it is loose leaf based on one keyword
        ],
        "general_search_terms": [
            "green tea", "herbal tea", "tea bags", "healthy drinks",
            "organic tea", "loose leaf tea", "tea variety pack"
        ],
        "negative_keywords": [
            "[iced tea mix]", "[tea pot]", "[tea cup]", "\"tea ceremony kit\"", "\"black tea\""
        ]
    },
    "B0BR2C2D2E": { # Kids' STEM Robot Kit
        "product_name": "Kids' STEM Robot Kit",
        "primary_keywords": [
            "[kids robot kit]", "[stem coding robot]",
            "[educational robot for kids]", "[build your own robot]"
        ],
        "general_search_terms": [
            "robot toy", "stem kit", "coding for kids", "science toys",
            "educational gifts for kids", "christmas toys", "learning games"
        ],
        "negative_keywords": [
            "[robot vacuum]", "[adult robot]", "[robot parts]", "\"robot costume\""
        ]
    },
    "B0CR3E3F3G": { # Winter Wool Scarf
        "product_name": "Winter Wool Scarf",
        "primary_keywords": [
            "[winter wool scarf women]", "[mens wool scarf cashmere]",
            "[warm knitted scarf]", "[oversized blanket scarf]"
        ],
        "general_search_terms": [
            "wool scarf", "winter accessories", "knitted scarf", "fashion scarf",
            "neck warmer", "gifts for her", "mens scarves"
        ],
        "negative_keywords": [
            "[silk scarf]", "[summer scarf]", "[scarf hanger]", "\"scarf knitting pattern\""
        ]
    },
    "B0CR4H4I4J": { # Stainless Steel Water Bottle (32oz)
        "product_name": "Stainless Steel Water Bottle (32oz)",
        "primary_keywords": [
            "[stainless steel water bottle 32oz]", "[insulated water bottle large]",
            "[bpa free water bottle for hiking]", "[hydroflask alternative]"
        ],
        "general_search_terms": [
            "water bottle", "reusable bottle", "sports bottle", "hydration bottle",
            "camping gear", "gym bottle", "thermos bottle"
        ],
        "negative_keywords": [
            "[plastic water bottle]", "[glass water bottle]", "[water bottle holder]", "\"water bottle pump\""
        ]
    },
    "B0CR5K5L5M": { # Pet Grooming Glove
        "product_name": "Pet Grooming Glove",
        "primary_keywords": [
            "[pet grooming glove]", "[dog shedding glove]",
            "[cat deshedding tool glove]", "[massage pet brush]"
        ],
        "general_search_terms": [
            "grooming glove", "pet brush", "dog grooming supplies", "cat hair removal",
            "shedding tool", "pet bath accessories", "animal deshedder"
        ],
        "negative_keywords": [
            "[human grooming glove]", "[garden glove]", "[oven mitt]", "\"leather glove\""
        ]
    },
    "B0CR6N6O6P": { # Advanced Drone with HD Camera
        "product_name": "Advanced Drone with HD Camera",
        "primary_keywords": [
            "[drone with hd camera]", "[professional fpv drone]",
            "[4k camera drone gps]", "[long range drone for adults]"
        ],
        "general_search_terms": [
            "drone", "rc drone", "quadcopter", "camera drone",
            "flying camera", "aerial photography", "drone for beginners"
        ],
        "negative_keywords": [
            "[toy drone]", "[drone parts]", "[drone repair]", "\"drone racing kit\""
        ]
    },
    "B0CR7Q7R7S": { # Eco-Friendly Reusable Shopping Bags (5-pack)
        "product_name": "Eco-Friendly Reusable Shopping Bags (5-pack)",
        "primary_keywords": [
            "[eco friendly reusable shopping bags]", "[collapsible grocery bags 5 pack]",
            "[washable produce bags]", "[heavy duty reusable tote bags]"
        ],
        "general_search_terms": [
            "reusable bags", "shopping bags", "grocery tote", "eco friendly products",
            "produce bags", "canvas bags", "foldable bags"
        ],
        "negative_keywords": [
            "[paper bags]", "[plastic bags]", "[gift bags]", "\"trash bags\""
        ]
    },
    "B0CR8T8U8V": { # Gourmet Coffee Beans (Dark Roast)
        "product_name": "Gourmet Coffee Beans (Dark Roast)",
        "primary_keywords": [
            "[gourmet coffee beans dark roast]", "[whole bean coffee organic]",
            "[artisanal coffee beans]", "[espresso blend beans]"
        ],
        "general_search_terms": [
            "coffee beans", "dark roast coffee", "whole bean coffee", "specialty coffee",
            "breakfast blend", "coffee gift set", "ground coffee"
        ],
        "negative_keywords": [
            "[instant coffee]", "[coffee maker]", "[coffee grinder]",
            "\"coffee machine parts\"", "\"coffee pods\""
        ]
    }
}

def get_keyword_suggestions_for_asins(asins: list) -> dict:
    """
    Returns keyword suggestions based on a list of ASINs.
    For MVP, it aggregates primary and general terms.
    """
    suggestions = {
        "primary_keywords": set(),
        "general_search_terms": set()
    }
    for asin in asins:
        data = PRODUCT_KEYWORD_MAPPINGS.get(asin)
        if data:
            suggestions["primary_keywords"].update(data.get("primary_keywords", []))
            suggestions["general_search_terms"].update(data.get("general_search_terms", []))

    # Convert sets to lists for JSON serialization if needed by API
    suggestions["primary_keywords"] = list(suggestions["primary_keywords"])
    suggestions["general_search_terms"] = list(suggestions["general_search_terms"])
    return suggestions

def get_negative_keywords_for_asins(asins: list) -> list:
    """
    Returns a combined list of negative keywords for given ASINs.
    """
    negatives = set()
    for asin in asins:
        data = PRODUCT_KEYWORD_MAPPINGS.get(asin)
        if data:
            negatives.update(data.get("negative_keywords", []))
    return list(negatives)

def get_all_product_keyword_data_for_asin(asin: str) -> dict:
    """
    Returns all keyword data (primary, general, negative) for a single ASIN.
    """
    return PRODUCT_KEYWORD_MAPPINGS.get(asin, {})

# Example usage:
if __name__ == '__main__':
    sample_asins = ["B0BQZ0Y4R5", "B0CR00N0M0"]
    suggestions = get_keyword_suggestions_for_asins(sample_asins)
    print(f"Suggestions for {sample_asins}: {suggestions}")

    negatives = get_negative_keywords_for_asins(sample_asins)
    print(f"Negative keywords for {sample_asins}: {negatives}")

    chair_data = get_all_product_keyword_data_for_asin("B0BQZ0Y4R5")
    print(f"Data for Ergonomic Office Chair: {chair_data}")
