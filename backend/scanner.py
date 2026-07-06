import re
import math
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
    # Jednostavna tokenizacija: odvoji reči koje nisu standardni tekst.
    tokens = re.finditer(r'[a-zA-Z0-9\-_/+]{10,}', text)  # samo alfanumerički + neki simboli
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

def scan_text(text: str) -> List[Dict]:
    """
    Glavna funkcija: skenira tekst koristeći regex šablone i entropijsku analizu.
    Vraća listu pronađenih incidenata, sortiranu po poziciji.
    """
    findings = []
    
    # Regex skeniranje
    for name, pattern in PATTERNS.items():
        for match in re.finditer(pattern, text):
            findings.append({
                "type": name,
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            })
    
    # Entropijska analiza
    high_entropy_findings = find_high_entropy(text)
    # Da ne bismo duplirali već pronađene (ako se poklapaju sa regexom), jednostavno ih dodamo
    # Možemo kasnije implementirati pametnije dedupliciranje.
    findings.extend(high_entropy_findings)
    
    # Sortiraj po poziciji
    findings.sort(key=lambda x: x["start"])
    return findings