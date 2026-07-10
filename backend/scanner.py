import re
import math
import os
import requests
from typing import List, Dict, Tuple

# Regex šabloni za česte tipove tajni i osetljivih podataka
PATTERNS = {
    "AWS Access Key ID": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Access Key": r"(?i)aws(.{0,20})?[0-9a-zA-Z\/+]{40}",
    "GitHub Token": r"ghp_[0-9a-zA-Z]{36}",
    "Slack Token": r"xox[baprs]-[0-9a-zA-Z\-]{10,}",
    "Generic API Key (looks like)": r"(?i)(api[_-]?key|apikey|secret|token|password)\s*[:=]\s*['\"]?([a-zA-Z0-9\-_]{20,})",
    "Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "IPv4 Address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "JWT Token": r"eyJ[a-zA-Z0-9\-_]{10,}\.[a-zA-Z0-9\-_]{10,}\.[a-zA-Z0-9\-_]{10,}",
    "Credit Card (Visa/MasterCard)": r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b",
    "Private SSH Key Header": r"-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----",
}

def shannon_entropy(data: str) -> float:
    """Računa entropiju stringa – veća entropija znači nasumičniji string."""
    if not data:
        return 0.0
    entropy = 0
    for x in range(256):
        p_x = data.count(chr(x)) / len(data)
        if p_x > 0:
            entropy += - p_x * math.log2(p_x)
    return entropy

def find_high_entropy(text: str, threshold: float = 4.5, min_length: int = 10) -> List[Dict]:
    """
    Traži segmente teksta sa visokom entropijom (potencijalne tajne).
    Vraća listu rečnika sa 'type', 'value', 'start', 'end'.
    """
    results = []
    tokens = re.finditer(r'[a-zA-Z0-9\-_/+]{10,}', text)
    for match in tokens:
        token = match.group()
        if len(token) >= min_length:
            ent = shannon_entropy(token)
            if ent > threshold:
                results.append({
                    "type": "High Entropy String",
                    "value": token,
                    "start": match.start(),
                    "end": match.end(),
                    "entropy": round(ent, 2)
                })
    return results

def scan_with_ai(text: str) -> List[Dict]:
    """
    Koristi Hugging Face NER model za prepoznavanje ličnih podataka (PII):
    imena (PER), organizacije (ORG), lokacije (LOC).
    Vraća listu nalaza u istom formatu kao regex skener.
    """
    HF_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
    # DEBUG: ispiši početak tokena
    print("DEBUG: HF_TOKEN =", HF_TOKEN[:10] + "..." if HF_TOKEN else "None")
    
    if not HF_TOKEN:
        print("Upozorenje: HUGGINGFACE_API_TOKEN nije podešen. Preskačem AI analizu.")
        return []

    API_URL = "https://api-inference.huggingface.co/models/dslim/bert-base-NER"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": text})
        response.raise_for_status()
        entities = response.json()
        # DEBUG: ispiši status i entitete
        print("DEBUG: API response status:", response.status_code)
        print("DEBUG: Entities received:", entities)
    except Exception as e:
        print(f"Greška pri pozivanju Hugging Face API-ja: {e}")
        return []

    findings = []
    if isinstance(entities, list):
        for ent in entities:
            if ent["score"] < 0.85:
                continue
            entity_type = ent["entity_group"]
            label_map = {
                "PER": "PII: Person Name",
                "ORG": "PII: Organization",
                "LOC": "PII: Location"
            }
            type_name = label_map.get(entity_type, f"PII: {entity_type}")
            findings.append({
                "type": type_name,
                "value": ent["word"],
                "start": ent["start"],
                "end": ent["end"],
                "entropy": None,
                "score": round(ent["score"], 2)
            })
    return findings

def scan_text(text: str) -> List[Dict]:
    """
    Glavna funkcija: skenira tekst koristeći regex šablone i entropijsku analizu.
    Vraća listu pronađenih incidenata, sortiranu po poziciji.
    """
    findings = []
    
    for name, pattern in PATTERNS.items():
        for match in re.finditer(pattern, text):
            findings.append({
                "type": name,
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            })
    
    high_entropy_findings = find_high_entropy(text)
    findings.extend(high_entropy_findings)
    
    findings.sort(key=lambda x: x["start"])
    return findings