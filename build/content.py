# Curated content layered on top of the open gita/gita dataset.
# Everything here is hand-written for Sarathi; review before launch.

# Commentary traditions (sampradaya) for the "read through this lens" feature.
TRADITIONS = [
    ("advaita", "Advaita", "Non-dual: the self and the absolute are one."),
    ("vishishtadvaita", "Vishishtadvaita", "Qualified non-dual: souls are real parts of the divine."),
    ("dvaita", "Dvaita", "Dual: the soul and God are eternally distinct."),
    ("shuddhadvaita", "Shuddhadvaita", "Pure non-dual, centred on grace and devotion."),
    ("shaiva", "Kashmir Shaivism", "The Gita read through Trika Shaiva philosophy."),
    ("modern", "Modern teachers", "20th-century teachers writing for today's readers."),
]

COMMENTATORS = {
    "Sri Shankaracharya": "advaita",
    "Sri Anandgiri": "advaita",
    "Sri Madhusudan Saraswati": "advaita",
    "Sri Sridhara Swami": "advaita",
    "Sri Dhanpati": "advaita",
    "Sri Neelkanth": "advaita",
    "Sri Ramanujacharya": "vishishtadvaita",
    "Sri Vedantadeshikacharya Venkatanatha": "vishishtadvaita",
    "Sri Madhavacharya": "dvaita",
    "Sri Jayatritha": "dvaita",
    "Sri Vallabhacharya": "shuddhadvaita",
    "Sri Purushottamji": "shuddhadvaita",
    "Sri Abhinavgupta": "shaiva",
    "Swami Sivananda": "modern",
    "Swami Ramsukhdas": "modern",
    "Swami Chinmayananda": "modern",
}

# Reading translations, in tab order. "follows" ties a translation to the
# classical commentary it renders, which is what powers the lens toggle.
TRANSLATIONS = [
    ("Swami Sivananda", "english", None),
    ("Swami Gambirananda", "english", "Shankara (Advaita)"),
    ("Swami Adidevananda", "english", "Ramanuja (Vishishtadvaita)"),
    ("Dr. S. Sankaranarayan", "english", "Abhinavagupta (Kashmir Shaivism)"),
    ("Shri Purohit Swami", "english", None),
    ("Swami Ramsukhdas", "hindi", None),
    ("Swami Tejomayananda", "hindi", None),
]

# Concepts. match = substrings of the diacritic-free Sanskrit token;
# exact = tokens that must match whole (for roots that collide with grammar).
CONCEPTS = [
    ("dharma", "dharma", "धर्म", "Duty, right order", ["dharm"], []),
    ("karma", "karma", "कर्म", "Action and its consequences", ["karm"], []),
    ("yoga", "yoga", "योग", "Union; disciplined practice", ["yog"], []),
    ("jnana", "jñāna", "ज्ञान", "Knowledge, insight", ["jnan"], []),
    ("bhakti", "bhakti", "भक्ति", "Loving devotion", ["bhakt"], []),
    ("atman", "ātman", "आत्मन्", "The self", ["atma"], []),
    ("brahman", "brahman", "ब्रह्मन्", "The absolute reality", ["brahm"], []),
    ("guna", "guṇa", "गुण", "The three qualities of nature", ["guna", "gunai", "gunat", "guneb"], []),
    ("sattva", "sattva", "सत्त्व", "Clarity, goodness", ["sattv"], []),
    ("rajas", "rajas", "रजस्", "Passion, restless activity", ["rajas", "rajo"], []),
    ("tamas", "tamas", "तमस्", "Inertia, darkness", ["tamas", "tamo"], []),
    ("prakriti", "prakṛti", "प्रकृति", "Nature, matter", ["prakrit"], []),
    ("purusha", "puruṣa", "पुरुष", "Spirit, the person", ["purush"], []),
    ("yajna", "yajña", "यज्ञ", "Sacrifice, offering", ["yajn"], []),
    ("tyaga", "tyāga", "त्याग", "Letting go", ["tyag"], []),
    ("sannyasa", "sannyāsa", "संन्यास", "Renunciation", ["sannyas", "sanyas"], []),
    ("buddhi", "buddhi", "बुद्धि", "Intellect, discernment", ["buddh"], []),
    ("manas", "manas", "मनस्", "The mind", ["manas", "mano"], ["manah", "manam"]),
    ("kama", "kāma", "काम", "Desire", ["kama"], []),
    ("krodha", "krodha", "क्रोध", "Anger", ["krodh"], []),
    ("ahankara", "ahaṅkāra", "अहङ्कार", "Ego, I-making", ["ahankar"], []),
    ("moksha", "mokṣa", "मोक्ष", "Liberation", ["moksh", "mukt"], []),
    ("shraddha", "śraddhā", "श्रद्धा", "Faith, trust", ["shraddh"], []),
    ("shanti", "śānti", "शान्ति", "Peace", ["shant"], []),
]

# "What are you facing?" entry points. Verse picks checked against the text.
SITUATIONS = [
    ("results", "I'm anxious about how things will turn out", ["2.47", "2.48", "2.50", "3.19", "5.12"]),
    ("grief", "I lost someone", ["2.11", "2.13", "2.20", "2.22", "2.27"]),
    ("anger", "I can't control my anger", ["2.62", "2.63", "3.37", "16.21", "5.26"]),
    ("mind", "My mind won't settle", ["6.5", "6.6", "6.26", "6.34", "6.35"]),
    ("doubt", "I feel weak and unsure of myself", ["2.3", "2.7", "4.42", "6.5", "18.73"]),
    ("duty", "I don't know what I should do", ["3.8", "3.35", "18.47", "18.48", "18.63"]),
    ("burnout", "I'm burnt out", ["3.19", "5.10", "6.16", "6.17", "2.50"]),
    ("fear", "I'm afraid", ["4.10", "9.22", "9.31", "18.66", "12.15"]),
    ("praise", "Praise and criticism shake me", ["2.38", "12.18", "12.19", "14.24", "6.7"]),
    ("alone", "I feel alone", ["6.30", "9.22", "9.29", "18.65", "9.18"]),
    ("craving", "I can't stop wanting more", ["2.70", "2.71", "3.39", "16.21", "5.22"]),
    ("death", "I'm afraid of death", ["2.20", "2.22", "2.27", "8.5", "8.6"]),
]
