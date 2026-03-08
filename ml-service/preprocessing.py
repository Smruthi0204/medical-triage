# preprocessing.py
# This is your Phase 1 code from Colab organized as a proper reusable module
# FastAPI will import and use these functions to clean incoming notes

import re
import spacy

# Load spaCy model once at module level
# Loading it here means it loads ONCE when the service starts
# not every time a request comes in — much faster
nlp = spacy.load("en_core_web_sm")

# ── Negation terms to preserve during lemmatization ──────────────────────────
NEGATION_TERMS = {
    'no', 'not', 'without', 'denies', 'denied', 'negative'
}

# ── Medical abbreviation dictionary ──────────────────────────────────────────
MEDICAL_ABBREVIATIONS = {
    # Imaging / Echo
    r'\b2\s*-?\s*d\b':     'two dimensional',
    r'\bm\s*-?\s*mode\b':  'motion mode',
    r'\bdoppler\b':        'doppler',

    # Chambers / Cardiology
    r'\blv\b':             'left ventricle',
    r'\brv\b':             'right ventricle',
    r'\bef\b':             'ejection fraction',
    r'\bpa\b':             'pulmonary artery',

    # General / H&P
    r'\bpt\b':             'patient',
    r'\bh&p\b':            'history and physical',
    r'\bh\+p\b':           'history and physical',
    r'\bhx\b':             'history',
    r'\bhpi\b':            'history of present illness',
    r'\bpmh\b':            'past medical history',
    r'\bfh\b':             'family history',
    r'\bsh\b':             'social history',
    r'\bcc\b':             'chief complaint',
    r'\bc/o\b':            'complains of',
    r'\bcons\b':           'consultation',
    r'\by/o\b':            'year old',
    r'\byo\b':             'year old',
    r'\bwf\b':             'white female',

    # Vitals
    r'\bvs\b':             'vital signs',
    r'\bbp\b':             'blood pressure',
    r'\bhr\b':             'heart rate',
    r'\brr\b':             'respiratory rate',
    r'\bpr\b':             'pulse rate',
    r'\bo2\s*sat\b':       'oxygen saturation',

    # Diseases
    r'\bmi\b':             'myocardial infarction',
    r'\bhtn\b':            'hypertension',
    r'\bdm\b':             'diabetes mellitus',
    r'\bsob\b':            'shortness of breath',
    r'\bcad\b':            'coronary artery disease',
    r'\bchf\b':            'congestive heart failure',
    r'\bcopd\b':           'chronic obstructive pulmonary disease',

    # Orthopedic
    r'\borif\b':           'open reduction internal fixation',
    r'\boa\b':             'osteoarthritis',
    r'\bacl\b':            'anterior cruciate ligament',
    r'\brom\b':            'range of motion',
    r'\bthr\b':            'total hip replacement',
    r'\btha\b':            'total hip arthroplasty',
    r'\btkr\b':            'total knee replacement',
    r'\btka\b':            'total knee arthroplasty',

    # Gynecologic Surgery
    r'\btah\b':            'total abdominal hysterectomy',
    r'\btahbso\b':         'total abdominal hysterectomy and bilateral salpingo oophorectomy',

    # Labs
    r'\bwbc\b':            'white blood cell',
    r'\brbc\b':            'red blood cell',
    r'\bcva\b':            'cerebrovascular accident',
    r'\buri\b':            'upper respiratory infection',
}


def remove_noise(text: str) -> str:
    """Remove clinical document headers, footers, and formatting artifacts."""

    # Remove metadata header lines
    text = re.sub(
        r'^(sample name|description|medical specialty|keywords|patient id|'
        r'patient name|date of birth|age|gender|referring physician|'
        r'admitting diagnosis|date of admission|date of discharge|'
        r'date of procedure)\s*:.*$',
        '', text, flags=re.IGNORECASE | re.MULTILINE
    )

    # Remove ALL-CAPS section headers
    text = re.sub(r'^[A-Z][A-Z\s]{2,}:\s*$', '', text, flags=re.MULTILINE)

    # Remove dictation artifacts
    text = re.sub(
        r'(dictated by|dictated on|transcribed by|electronically signed by|'
        r'this concludes the dictation|thank you for (allowing|the referral)).*',
        '', text, flags=re.IGNORECASE
    )

    # Remove PHI placeholders
    text = re.sub(r'\[\*\*.*?\*\*\]', '', text)
    text = re.sub(r'[_X]{3,}', '', text)
    text = re.sub(r'\b\d+\.(?=\s)', '', text)

    # Normalize whitespace
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)

    # Keep letters, numbers, spaces, punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,%]', '', text)

    return text.strip()


def expand_abbreviations(text: str) -> str:
    """Replace medical abbreviations with full forms."""
    text = text.lower()
    for abbr, full in MEDICAL_ABBREVIATIONS.items():
        text = re.sub(abbr, full, text, flags=re.IGNORECASE)
    return text


def protect_laterality(text: str) -> str:
    """Protect left/right from being changed during lemmatization."""
    text = re.sub(r'\bleft\b',  'left_side',  text, flags=re.IGNORECASE)
    text = re.sub(r'\bright\b', 'right_side', text, flags=re.IGNORECASE)
    return text


def lemmatize_text(text: str) -> str:
    """Tokenize, remove stopwords, and lemmatize."""
    doc = nlp(text)
    tokens = [
        token.lemma_
        for token in doc
        if (
            (not token.is_stop or token.text.lower() in NEGATION_TERMS)
            and not token.is_punct
            and (
                len(token.text) > 2
                or token.text.lower() in NEGATION_TERMS
                or token.text.isdigit()
                or token.text.lower() in {'ef', 'lv', 'rv'}
            )
        )
    ]
    return ' '.join(tokens)


def restore_laterality(text: str) -> str:
    """Restore left_side/right_side back to left/right."""
    return text.replace('left_side', 'left').replace('right_side', 'right')


def preprocess(text: str) -> str:
    """
    Master preprocessing pipeline.
    Runs all steps in sequence — same pipeline used in Colab training.
    """
    text = remove_noise(text)
    text = expand_abbreviations(text)
    text = protect_laterality(text)
    text = lemmatize_text(text)
    text = restore_laterality(text)
    return text
