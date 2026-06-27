WORDLIST_FILE = "temp_wordlist.txt"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import hashlib
import itertools
import string

app = FastAPI()


# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------
# MODELS
# -----------------------------------------------------------

class HashRequest(BaseModel):
    text: str
    algorithm: str

class CrackRequest(BaseModel):
    hash_value: str
    algorithm: str
    wordlist: list

class WordlistRequest(BaseModel):
    charset: str
    min_len: int
    max_len: int

class MutationRequest(BaseModel):
    words: list


# -----------------------------------------------------------
# HASH FUNCTION
# -----------------------------------------------------------

def hash_text(text, algorithm):
    raw = text.encode()
    if algorithm == "md5":
        return hashlib.md5(raw).hexdigest()
    if algorithm == "sha1":
        return hashlib.sha1(raw).hexdigest()
    if algorithm == "sha256":
        return hashlib.sha256(raw).hexdigest()


# -----------------------------------------------------------
# WORDLIST GENERATOR
# -----------------------------------------------------------

def generate_wordlist(charset, min_len, max_len):
    for length in range(min_len, max_len + 1):
        for combo in itertools.product(charset, repeat=length):
            yield "".join(combo)


# -----------------------------------------------------------
# MUTATION ENGINE
# -----------------------------------------------------------

def apply_mutations(words):
    mutated = set()

    for w in words:
        w = w.strip()
        mutated.add(w.lower())
        mutated.add(w.upper())
        mutated.add(w[::-1])
        mutated.add(w + "123")
        mutated.add(w + "!")
    
    return list(mutated)


# -----------------------------------------------------------
# SMART CRACK ENGINE (auto + dictionary)
# -----------------------------------------------------------

def smart_crack(hash_value, algorithm):
    chars = string.ascii_lowercase

    # Brute force prefixes (1–3 letters)
    for length in range(1, 4):
        for combo in itertools.product(chars, repeat=length):
            prefix = "".join(combo)

            guesses = [
                prefix,
                prefix + "er",
                prefix + "wer",
                prefix + "ar",
                prefix + "a",
                prefix + "aa",
                prefix + "aaa",
                prefix + "123",
                prefix + "2024"
            ]

            for word in guesses:
                if hash_text(word, algorithm) == hash_value:
                    return word

    return None


# -----------------------------------------------------------
# API ROUTES
# -----------------------------------------------------------

@app.post("/store_wordlist")
def store_wordlist(data: CrackRequest):
    with open(WORDLIST_FILE, "w", encoding="utf-8") as f:
        for word in data.wordlist:
            f.write(word.strip() + "\n")

    return {"saved": True, "count": len(data.wordlist)}


@app.post("/hash")
def create_hash(data: HashRequest):
    return {"hash": hash_text(data.text, data.algorithm.lower())}


@app.post("/crack")
def crack(data: CrackRequest):

    # Load wordlist from file
    try:
        with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
            words = [w.strip() for w in f.readlines()]
    except:
        return {"found": False, "error": "Wordlist not loaded"}

    # Auto brute force mode
    if len(words) == 1 and words[0].lower() == "auto":
        chars = string.ascii_lowercase
        for length in range(1, 4):
            for combo in itertools.product(chars, repeat=length):
                word = "".join(combo)
                if hash_text(word, data.algorithm) == data.hash_value.lower():
                    return {"found": True, "password": word}
        return {"found": False}

    # Standard dictionary mode
    for word in words:
        if hash_text(word, data.algorithm.lower()) == data.hash_value.lower():
            return {"found": True, "password": word}

    return {"found": False}


@app.post("/wordlist")
def wordlist_api(data: WordlistRequest):

    if data.charset == "lower":
        charset = string.ascii_lowercase
    elif data.charset == "lowerdigit":
        charset = string.ascii_lowercase + string.digits
    else:
        charset = string.ascii_letters + string.digits + "!@#$%"

    words = generate_wordlist(charset, data.min_len, data.max_len)
    preview = list(next(words) for _ in range(20))

    return {"preview": preview}


@app.post("/mutate")
def mutation_api(data: MutationRequest):
    return {"mutations": apply_mutations(data.words)[:50]}

# ==========================
# HASHCAT SPEED COMPARISON
# ==========================

HASHCAT_SPEED = {
    "md5": "70+ Billion H/s",
    "sha1": "30+ Billion H/s",
    "sha256": "9+ Billion H/s"
}

@app.post("/compare")
def compare_speed(data: HashRequest):

    python_speed = "10,000 – 20,000 H/s"
    algo = data.algorithm.lower()

    return {
        "python_speed": python_speed,
        "hashcat_speed": HASHCAT_SPEED.get(algo, "N/A"),
        "difference": "Hashcat is millions of times faster"
    }

@app.get("/")
def home():
    return {"message": "Password Cracker API Running Correctly!"}