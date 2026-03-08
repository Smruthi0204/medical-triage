# negation.py
# Detects whether medical entities are present or negated in clinical text

from preprocessing import nlp

# ── Negation trigger words ────────────────────────────────────────────────────
NEGATION_WORDS = {
    'no', 'not', 'without', 'denies', 'denied',
    'absence', 'absent', 'negative', 'never', 'none'
}

# ── Target medical entities organized by category ────────────────────────────
TARGET_ENTITIES_DICT = {
    "symptoms": [
        "pain", "chest pain", "shortness of breath", "dyspnea", "fever",
        "cough", "swelling", "edema", "dizziness", "weakness", "fatigue",
        "nausea", "vomiting", "headache", "palpitations", "syncope",
        "numbness", "tingling", "bleeding"
    ],
    "diseases": [
        "hypertension", "diabetes mellitus", "coronary artery disease",
        "myocardial infarction", "heart failure", "arrhythmia",
        "atrial fibrillation", "pneumonia", "asthma", "copd", "stroke",
        "fracture", "arthritis", "osteoarthritis", "osteoporosis",
        "infection", "sepsis"
    ],
    "anatomy": [
        "heart", "artery", "vein", "valve", "ventricle", "atrium",
        "lung", "pulmonary artery", "aorta", "myocardium",
        "bone", "joint", "knee", "hip", "spine", "shoulder",
        "ankle", "wrist", "ligament", "tendon", "cartilage"
    ],
    "procedures": [
        "surgery", "arthroscopy", "replacement", "repair",
        "incision", "fixation"
    ]
}

# Flatten into one set for fast lookup
TARGET_ENTITIES = set(
    entity
    for category in TARGET_ENTITIES_DICT.values()
    for entity in category
)


def detect_negation(text: str) -> list:
    """
    Detects whether target medical entities are negated or present.
    Returns a list of dicts with entity, category and status.

    Handles both:
    - Single word entities : pain, fever, knee
    - Multi word entities  : chest pain, heart failure
    """
    doc = nlp(text)
    results = []
    text_lower = text.lower()

    # ── Multi-word entities ───────────────────────────────────────────────────
    multi_word_entities = [e for e in TARGET_ENTITIES if ' ' in e]

    for entity in multi_word_entities:
        if entity in text_lower:
            start_idx = text_lower.find(entity)
            preceding_text = text_lower[:start_idx].split()[-3:]
            negated = any(word in NEGATION_WORDS for word in preceding_text)

            results.append({
                'entity': entity,
                'category': next(
                    cat for cat, items in TARGET_ENTITIES_DICT.items()
                    if entity in items
                ),
                'status': 'Negated' if negated else 'Present'
            })

    # ── Single word entities ──────────────────────────────────────────────────
    single_word_entities = [e for e in TARGET_ENTITIES if ' ' not in e]

    for token in doc:
        if token.lemma_.lower() not in single_word_entities and \
           token.text.lower() not in single_word_entities:
            continue

        negated = False

        # Check 1: direct negation child
        for child in token.children:
            if child.dep_ == 'neg' or child.lemma_.lower() in NEGATION_WORDS \
               or child.text.lower() in NEGATION_WORDS:
                negated = True
                break

        # Check 2: governing verb has negation
        if not negated:
            head = token.head
            for child in head.children:
                if child.dep_ == 'neg' or child.lemma_.lower() in NEGATION_WORDS \
                   or child.text.lower() in NEGATION_WORDS:
                    negated = True
                    break
            if head.lemma_.lower() in NEGATION_WORDS or \
               head.text.lower() in NEGATION_WORDS:
                negated = True

        # Check 3: word immediately to the left
        if not negated and token.i > 0:
            prev_token = doc[token.i - 1]
            if prev_token.lemma_.lower() in NEGATION_WORDS or \
               prev_token.text.lower() in NEGATION_WORDS:
                negated = True

        results.append({
            'entity': token.text,
            'category': next(
                (cat for cat, items in TARGET_ENTITIES_DICT.items()
                 if token.lemma_.lower() in items
                 or token.text.lower() in items), 'unknown'
            ),
            'status': 'Negated' if negated else 'Present'
        })

    # Remove duplicates keeping first occurrence
    seen = set()
    unique_results = []
    for r in results:
        key = r['entity'].lower()
        if key not in seen:
            seen.add(key)
            unique_results.append(r)

    return unique_results