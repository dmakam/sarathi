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
    ("habits", "I want better habits", ["6.5", "3.8", "17.16", "13.8", "6.17"]),
]

# Core curriculum: the 20 themes and verse selection of Heartfulness's
# Gitopadesh Vidyarthi course (learning.heartfulness.org/courses/GPDVY-EN).
# Order within a theme follows the course. Theme 12 lists one unnumbered
# shloka that is left out until confirmed.
THEMES_SOURCE = ("Heartfulness Gitopadesh Vidyarthi course", "https://learning.heartfulness.org/courses/GPDVY-EN")
THEMES = [
    ("inner-potential", "Exploring inner potential", ["3.42", "3.43", "7.4", "7.5", "13.5", "13.6"]),
    ("faculties", "Mastering your faculties", ["13.5", "13.6", "18.13", "18.14", "18.15", "3.42"]),
    ("habits", "Habit formation", ["6.5", "17.16", "3.7", "3.8", "13.8", "4.39"]),
    ("gunas", "The three gunas", ["14.6", "14.7", "14.8", "14.11", "14.12", "14.13"]),
    ("demoniac-to-divine", "From demoniac to divine", ["16.6", "16.4", "16.5", "16.1", "16.2", "16.3"]),
    ("self-mastery", "Self mastery", ["15.1", "15.2", "15.4", "15.5", "15.6", "15.10", "15.11"]),
    ("mind", "Regulation of mind", ["2.60", "2.61", "2.64", "6.18", "6.25", "6.26"]),
    ("joyful-action", "Joyful actions", ["3.20", "3.21", "3.25", "4.18", "4.19", "18.56"]),
    ("altruistic-action", "Altruistic actions", ["2.47", "2.48", "3.26", "3.30", "4.21", "4.23"]),
    ("moderation", "Moderation", ["2.62", "2.63", "2.66", "5.7", "5.8", "5.9"]),
    ("conduct", "Conduct", ["17.15", "5.18", "4.34", "13.7", "2.54", "2.56"]),
    ("food", "Attitude towards food", ["6.17", "17.8", "17.9", "17.10", "15.14"]),
    ("life-force", "The seed of all life force", ["10.32", "10.33", "10.34", "10.35", "10.37", "10.39"]),
    ("happiness", "Source of happiness", ["5.21", "5.22", "5.24", "18.39", "18.38", "18.37"]),
    ("wisdom", "Source of wisdom", ["10.10", "10.11", "10.20", "13.17", "13.24", "9.13"]),
    ("true-friend", "The true friend", ["7.24", "7.25", "7.3", "7.17", "7.18", "7.19"]),
    ("guide", "Role of a guide", ["4.35", "4.34", "11.41", "11.42", "11.43", "11.44"]),
    ("devotion", "Devotion in action", ["12.13", "12.14", "12.15", "12.16", "9.27", "12.18"]),
    ("love", "Power of love", ["6.30", "9.26", "8.8", "8.9", "8.14", "9.22"]),
    ("equanimity", "Equanimity", ["12.17", "2.53", "4.22", "6.8", "6.9", "2.50"]),
]

# A Sanskrit keyword for each theme card: (devanagari, romanised).
THEME_WORDS = {
    "inner-potential": ("\u0936\u0915\u094d\u0924\u093f", "\u015bakti"),
    "faculties": ("\u0907\u0928\u094d\u0926\u094d\u0930\u093f\u092f", "indriya"),
    "habits": ("\u0905\u092d\u094d\u092f\u093e\u0938", "abhy\u0101sa"),
    "gunas": ("\u0917\u0941\u0923", "gu\u1e47a"),
    "demoniac-to-divine": ("\u0926\u0948\u0935\u0940 \u0938\u092e\u094d\u092a\u0926\u094d", "daiv\u012b sampad"),
    "self-mastery": ("\u0906\u0924\u094d\u092e\u0938\u0902\u092f\u092e", "\u0101tma-sa\u1e43yama"),
    "mind": ("\u092e\u0928\u0938\u094d", "manas"),
    "joyful-action": ("\u0932\u094b\u0915\u0938\u0919\u094d\u0917\u094d\u0930\u0939", "loka-sa\u1e45graha"),
    "altruistic-action": ("\u0928\u093f\u0937\u094d\u0915\u093e\u092e \u0915\u0930\u094d\u092e", "ni\u1e63k\u0101ma karma"),
    "moderation": ("\u092f\u0941\u0915\u094d\u0924", "yukta"),
    "conduct": ("\u0906\u091a\u093e\u0930", "\u0101c\u0101ra"),
    "food": ("\u0906\u0939\u093e\u0930", "\u0101h\u0101ra"),
    "life-force": ("\u0935\u093f\u092d\u0942\u0924\u093f", "vibh\u016bti"),
    "happiness": ("\u0938\u0941\u0916", "sukha"),
    "wisdom": ("\u091c\u094d\u091e\u093e\u0928", "j\u00f1\u0101na"),
    "true-friend": ("\u0938\u0941\u0939\u0943\u0926\u094d", "suh\u1e5bd"),
    "guide": ("\u0917\u0941\u0930\u0941", "guru"),
    "devotion": ("\u092d\u0915\u094d\u0924\u093f", "bhakti"),
    "love": ("\u092a\u094d\u0930\u0940\u0924\u093f", "pr\u012bti"),
    "equanimity": ("\u0938\u092e\u0924\u094d\u0935", "samatva"),
}
