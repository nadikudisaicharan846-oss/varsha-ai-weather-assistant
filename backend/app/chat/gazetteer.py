"""Place names (English / Telugu / Hindi) -> canonical English name used for geocoding.
Anything not listed here is still found by the English pattern matcher or by the LLM parser."""

PLACES: dict[str, list[str]] = {
    "Hyderabad": ["hyderabad", "హైదరాబాద్", "हैदराबाद"],
    "Secunderabad": ["secunderabad", "సికింద్రాబాద్", "सिकंदराबाद"],
    "Nalgonda": ["nalgonda", "నల్గొండ", "नलगोंडा"],
    "Warangal": ["warangal", "వరంగల్", "वारंगल"],
    "Karimnagar": ["karimnagar", "కరీంనగర్", "करीमनगर"],
    "Khammam": ["khammam", "ఖమ్మం", "खम्मम"],
    "Nizamabad": ["nizamabad", "నిజామాబాద్", "निज़ामाबाद"],
    "Vijayawada": ["vijayawada", "విజయవాడ", "विजयवाड़ा"],
    "Visakhapatnam": ["visakhapatnam", "vizag", "విశాఖపట్నం", "విశాఖ", "विशाखापत्तनम"],
    "Tirupati": ["tirupati", "తిరుపతి", "तिरुपति"],
    "Guntur": ["guntur", "గుంటూరు", "गुंटूर"],
    "Mumbai": ["mumbai", "bombay", "ముంబై", "मुंबई"],
    "Pune": ["pune", "పుణె", "పూణే", "पुणे"],
    "Delhi": ["new delhi", "delhi", "ఢిల్లీ", "दिल्ली"],
    "Bengaluru": ["bengaluru", "bangalore", "బెంగళూరు", "बेंगलुरु", "बेंगलुरू"],
    "Chennai": ["chennai", "madras", "చెన్నై", "चेन्नई"],
    "Kolkata": ["kolkata", "calcutta", "కోల్‌కతా", "कोलकाता"],
    "Ahmedabad": ["ahmedabad", "అహ్మదాబాద్", "अहमदाबाद"],
    "Jaipur": ["jaipur", "జైపూర్", "जयपुर"],
    "Lucknow": ["lucknow", "లక్నో", "लखनऊ"],
    "Bhopal": ["bhopal", "భోపాల్", "भोपाल"],
    "Patna": ["patna", "పాట్నా", "पटना"],
    "Kochi": ["kochi", "cochin", "కొచ్చి", "कोच्चि"],
    "Thiruvananthapuram": ["thiruvananthapuram", "trivandrum", "తిరువనంతపురం", "तिरुवनंतपुरम"],
    "Bhubaneswar": ["bhubaneswar", "భువనేశ్వర్", "भुवनेश्वर"],
    "Nagpur": ["nagpur", "నాగ్‌పూర్", "नागपुर"],
    "Chandigarh": ["chandigarh", "చండీగఢ్", "चंडीगढ़"],
    "Goa": ["goa", "గోవా", "गोवा"],
    # states / regions (resolved to their central point; flagged as regions in climate output)
    "Telangana": ["telangana", "తెలంగాణ", "तेलंगाना"],
    "Andhra Pradesh": ["andhra pradesh", "ఆంధ్రప్రదేశ్", "ఆంధ్ర ప్రదేశ్", "आंध्र प्रदेश"],
    "Karnataka": ["karnataka", "కర్ణాటక", "कर्नाटक"],
    "Tamil Nadu": ["tamil nadu", "తమిళనాడు", "तमिलनाडु"],
    "Kerala": ["kerala", "కేరళ", "केरल"],
    "Maharashtra": ["maharashtra", "మహారాష్ట్ర", "महाराष्ट्र"],
    "Odisha": ["odisha", "orissa", "ఒడిశా", "ओडिशा"],
}

# longest alias first so "new delhi" beats "delhi"
ALIASES = sorted(((a, canon) for canon, al in PLACES.items() for a in al), key=lambda x: -len(x[0]))
