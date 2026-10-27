"""Server-side translations. To add a language: add its code to LANGS and a column to every entry.
Missing keys fall back to English. Numbers/units are passed as parameters and never translated.
NOTE: Telugu/Hindi strings should be reviewed by native speakers before production use."""

LANGS = {"en": "English", "te": "తెలుగు", "hi": "हिन्दी"}
M: dict[str, dict[str, str]] = {}


def m(key: str, en: str, te: str, hi: str) -> None:
    M[key] = {"en": en, "te": te, "hi": hi}


def t(key: str, lang: str = "en", **kw) -> str:
    entry = M.get(key)
    if not entry:
        return key
    text = entry.get(lang) or entry["en"]
    try:
        return text.format(**kw)
    except (KeyError, IndexError):
        return text


# ---- weather conditions ----
m("cond.clear", "Clear sky", "నిర్మలమైన ఆకాశం", "साफ आसमान")
m("cond.mostly_clear", "Mainly clear", "దాదాపు నిర్మలం", "लगभग साफ")
m("cond.partly_cloudy", "Partly cloudy", "పాక్షికంగా మేఘావృతం", "आंशिक रूप से बादल")
m("cond.overcast", "Overcast", "మేఘావృతం", "घने बादल")
m("cond.fog", "Fog", "పొగమంచు", "कोहरा")
m("cond.drizzle", "Drizzle", "తుంపర వర్షం", "बूंदाबांदी")
m("cond.light_rain", "Light rain", "తేలికపాటి వర్షం", "हल्की बारिश")
m("cond.rain", "Moderate rain", "మోస్తరు వర్షం", "मध्यम बारिश")
m("cond.heavy_rain", "Heavy rain", "భారీ వర్షం", "भारी बारिश")
m("cond.freezing_rain", "Freezing rain", "గడ్డకట్టే వర్షం", "जमने वाली बारिश")
m("cond.snow", "Snow", "మంచు", "बर्फबारी")
m("cond.showers", "Rain showers", "వర్షపు జల్లులు", "बारिश की बौछारें")
m("cond.heavy_showers", "Heavy showers", "భారీ జల్లులు", "तेज़ बौछारें")
m("cond.thunderstorm", "Thunderstorm", "ఉరుములతో కూడిన వర్షం", "गरज के साथ बारिश")
m("cond.thunderstorm_hail", "Thunderstorm with hail", "వడగండ్లతో ఉరుముల వర్షం", "ओलों के साथ गरज-तूफ़ान")
m("cond.unknown", "Unknown", "తెలియదు", "अज्ञात")

# ---- levels / statuses / misc words ----
m("level.information", "Information", "సమాచారం", "सूचना")
m("level.advisory", "Advisory", "సలహా", "परामर्श")
m("level.warning", "Warning", "హెచ్చరిక", "चेतावनी")
m("level.severe_warning", "Severe Warning", "తీవ్ర హెచ్చరిక", "गंभीर चेतावनी")
m("status.good", "Good", "అనుకూలం", "अनुकूल")
m("status.caution", "Caution", "జాగ్రత్త", "सावधानी")
m("status.avoid", "Avoid", "నివారించండి", "टालें")
m("status.info", "Info", "సమాచారం", "जानकारी")
m("status.na", "N/A", "లేదు", "उपलब्ध नहीं")
m("day.today", "Today", "ఈ రోజు", "आज")
m("day.tomorrow", "Tomorrow", "రేపు", "कल")
m("day.day_after", "Day after tomorrow", "ఎల్లుండి", "परसों")
m("val.none", "None expected", "ఏమీ లేదు", "कोई नहीं")
m("val.possible", "Possible", "అవకాశం ఉంది", "संभव")
m("val.na", "Not available", "అందుబాటులో లేదు", "उपलब्ध नहीं")
m("param.rainfall", "Rainfall", "వర్షపాతం", "वर्षा")
m("param.temperature", "Temperature", "ఉష్ణోగ్రత", "तापमान")
m("param.humidity", "Humidity", "తేమ", "आर्द्रता")

# ---- alerts ----
m("alert.rain.title", "Heavy Rain Alert", "భారీ వర్ష హెచ్చరిక", "भारी बारिश की चेतावनी")
m("alert.rain.summary", "About {mm} mm of rain is forecast for {place} on {date} ({prob}% chance).",
  "{date} నాడు {place}లో సుమారు {mm} మి.మీ వర్షం పడే అవకాశం ఉంది ({prob}% సంభావ్యత).",
  "{date} को {place} में लगभग {mm} मिमी बारिश का पूर्वानुमान है ({prob}% संभावना)।")
m("alert.rain.a1", "Avoid low-lying areas, underpasses and flooded roads.",
  "లోతట్టు ప్రాంతాలు, అండర్‌పాస్‌లు, నీరు నిలిచిన రోడ్లను నివారించండి.",
  "निचले इलाकों, अंडरपास और जलभराव वाली सड़कों से बचें।")
m("alert.rain.a2", "Postpone non-essential travel and keep mobile phones charged.",
  "అవసరం లేని ప్రయాణాలను వాయిదా వేయండి, మొబైల్ ఫోన్లను ఛార్జ్‌లో ఉంచండి.",
  "गैर-ज़रूरी यात्रा टालें और मोबाइल चार्ज रखें।")
m("alert.heat.title", "Heatwave Alert", "వడగాల్పుల హెచ్చరిక", "लू की चेतावनी")
m("alert.heat.summary", "A maximum temperature of {temp}°C is forecast for {place} on {date}.",
  "{date} నాడు {place}లో గరిష్ఠ ఉష్ణోగ్రత {temp}°C ఉండవచ్చని అంచనా.",
  "{date} को {place} में अधिकतम तापमान {temp}°C रहने का पूर्वानुमान है।")
m("alert.heat.a1", "Drink plenty of water and avoid going out between 12 and 4 pm.",
  "ఎక్కువగా నీళ్లు తాగండి, మధ్యాహ్నం 12 నుండి 4 గంటల మధ్య బయటకు వెళ్లకండి.",
  "खूब पानी पिएं और दोपहर 12 से 4 बजे के बीच बाहर निकलने से बचें।")
m("alert.heat.a2", "Wear light, loose clothing and look after children, the elderly and outdoor workers.",
  "తేలికైన, వదులైన దుస్తులు ధరించండి; పిల్లలు, వృద్ధులు, బయట పనిచేసేవారి పట్ల జాగ్రత్త వహించండి.",
  "हल्के, ढीले कपड़े पहनें और बच्चों, बुज़ुर्गों व बाहर काम करने वालों का ध्यान रखें।")
m("alert.heat.a3", "Never leave children or pets in parked vehicles; seek medical help for dizziness, confusion or very high body temperature.",
  "పార్క్ చేసిన వాహనాల్లో పిల్లలను, పెంపుడు జంతువులను ఎప్పుడూ వదిలివేయకండి; తల తిరగడం, గందరగోళం లేదా అధిక శరీర ఉష్ణోగ్రత ఉంటే వైద్య సహాయం తీసుకోండి.",
  "खड़ी गाड़ियों में बच्चों या पालतू जानवरों को कभी न छोड़ें; चक्कर, भ्रम या बहुत तेज़ बुखार हो तो चिकित्सा सहायता लें।")
m("alert.thunderstorm.title", "Thunderstorm Warning", "ఉరుములతో కూడిన తుఫాను హెచ్చరిక", "आंधी-तूफ़ान की चेतावनी")
m("alert.thunderstorm.summary", "Thunderstorm conditions are forecast for {place} on {date}.",
  "{date} నాడు {place}లో ఉరుములతో కూడిన తుఫాను పరిస్థితులు ఉండవచ్చని అంచనా.",
  "{date} को {place} में गरज-तूफ़ान की स्थिति का पूर्वानुमान है।")
m("alert.thunderstorm.summary_hail", "Thunderstorm with hail is forecast for {place} on {date}.",
  "{date} నాడు {place}లో వడగండ్లతో కూడిన ఉరుముల తుఫాను ఉండవచ్చని అంచనా.",
  "{date} को {place} में ओलों के साथ गरज-तूफ़ान का पूर्वानुमान है।")
m("alert.thunderstorm.a1", "Stay indoors during lightning; avoid open fields, tall trees and water bodies.",
  "మెరుపుల సమయంలో ఇంట్లోనే ఉండండి; ఖాళీ మైదానాలు, ఎత్తైన చెట్లు, నీటి వనరుల దగ్గరకు వెళ్లకండి.",
  "बिजली चमकते समय घर के अंदर रहें; खुले मैदान, ऊँचे पेड़ों और जलाशयों से दूर रहें।")
m("alert.thunderstorm.a2", "Unplug sensitive electrical appliances and secure loose outdoor objects.",
  "సున్నితమైన విద్యుత్ పరికరాల ప్లగ్‌లను తీసివేయండి, బయట ఉన్న వస్తువులను భద్రపరచండి.",
  "संवेदनशील बिजली उपकरणों के प्लग निकाल दें और बाहर रखी चीज़ों को सुरक्षित करें।")
m("alert.wind.title", "Strong Wind Advisory", "బలమైన గాలుల సూచన", "तेज़ हवा का परामर्श")
m("alert.wind.summary", "Wind gusts up to {gust} km/h are forecast for {place} on {date}.",
  "{date} నాడు {place}లో గాలి ఝంఝలు {gust} కి.మీ/గం వరకు ఉండవచ్చని అంచనా.",
  "{date} को {place} में हवा के झोंके {gust} किमी/घंटा तक रहने का पूर्वानुमान है।")
m("alert.wind.a1", "Secure loose objects and avoid standing under trees, hoardings or weak structures.",
  "వదులుగా ఉన్న వస్తువులను భద్రపరచండి; చెట్లు, హోర్డింగులు, బలహీన నిర్మాణాల కింద నిలబడకండి.",
  "ढीली चीज़ें सुरक्षित करें और पेड़ों, होर्डिंग व कमज़ोर ढांचों के नीचे न खड़े हों।")
m("alert.wind.a2", "Two-wheeler riders and boat operators should take extra care.",
  "ద్విచక్ర వాహనదారులు, పడవ నడిపేవారు అదనపు జాగ్రత్త వహించండి.",
  "दोपहिया चालक और नाव चलाने वाले विशेष सावधानी बरतें।")
m("alert.flood.title", "Flood Risk Advisory", "వరద ప్రమాద సూచన", "बाढ़ जोखिम परामर्श")
m("alert.flood.summary", "About {mm} mm of rain is forecast over 3 days from {date} in {place}, which may cause waterlogging or flooding.",
  "{date} నుండి 3 రోజుల్లో {place}లో సుమారు {mm} మి.మీ వర్షం పడవచ్చు; నీటి నిల్వ లేదా వరదలు సంభవించవచ్చు.",
  "{date} से 3 दिनों में {place} में लगभग {mm} मिमी बारिश का पूर्वानुमान है, जिससे जलभराव या बाढ़ हो सकती है।")
m("alert.flood.a1", "Move valuables to higher floors and avoid crossing flooded roads or streams.",
  "విలువైన వస్తువులను పై అంతస్తులకు తరలించండి; నీరు ప్రవహిస్తున్న రోడ్లు, వాగులు దాటకండి.",
  "कीमती सामान ऊपरी मंज़िल पर रखें और पानी भरी सड़कें या नाले पार न करें।")
m("alert.flood.a2", "Keep emergency contacts handy and follow local authority instructions.",
  "అత్యవసర నంబర్లు సిద్ధంగా ఉంచుకోండి, స్థానిక అధికారుల సూచనలను పాటించండి.",
  "आपातकालीन नंबर पास रखें और स्थानीय प्रशासन के निर्देशों का पालन करें।")
m("alert.fog.title", "Low Visibility Advisory", "తక్కువ దృశ్యమానత సూచన", "कम दृश्यता परामर्श")
m("alert.fog.summary", "Visibility may drop to {vis} km in {place} on {date}.",
  "{date} నాడు {place}లో దృశ్యమానత {vis} కి.మీ వరకు తగ్గవచ్చు.",
  "{date} को {place} में दृश्यता घटकर {vis} किमी तक हो सकती है।")
m("alert.fog.a1", "Drive slowly with low-beam lights and keep a safe distance.",
  "తక్కువ బీమ్ లైట్లతో నెమ్మదిగా నడపండి, సురక్షిత దూరం పాటించండి.",
  "लो-बीम लाइट के साथ धीरे चलाएं और सुरक्षित दूरी रखें।")
m("alert.fog.a2", "Check flight and train status before travelling.",
  "ప్రయాణానికి ముందు విమాన, రైలు స్థితిని తనిఖీ చేయండి.",
  "यात्रा से पहले उड़ान और ट्रेन की स्थिति जाँच लें।")
m("alert.period", "Expected mainly between {start} and {end}.", "ప్రధానంగా {start} నుండి {end} మధ్య ఉండవచ్చు.",
  "मुख्य रूप से {start} से {end} के बीच संभावित।")
m("alert.disclaimer",
  "Forecast-based advisory generated by Varsha AI from {provider} model data. It is not an official government warning; follow IMD and local disaster authorities for official alerts.",
  "ఇది {provider} మోడల్ డేటా ఆధారంగా Varsha AI రూపొందించిన సూచన మాత్రమే. ఇది అధికారిక ప్రభుత్వ హెచ్చరిక కాదు; అధికారిక హెచ్చరికల కోసం IMD, స్థానిక విపత్తు నిర్వహణ అధికారుల సూచనలను పాటించండి.",
  "यह {provider} मॉडल डेटा पर आधारित Varsha AI का पूर्वानुमान-आधारित परामर्श है। यह आधिकारिक सरकारी चेतावनी नहीं है; आधिकारिक अलर्ट के लिए IMD और स्थानीय आपदा प्राधिकरणों का पालन करें।")
m("alert.limits", "Cyclone tracks and official IMD warnings are not part of this data source.",
  "తుఫాను మార్గాలు, అధికారిక IMD హెచ్చరికలు ఈ డేటా మూలంలో లేవు.",
  "चक्रवात मार्ग और आधिकारिक IMD चेतावनियाँ इस डेटा स्रोत में शामिल नहीं हैं।")
m("alerts.none", "No significant weather alerts for {place} in the next 7 days based on the configured thresholds.",
  "కాన్ఫిగర్ చేసిన పరిమితుల ఆధారంగా రాబోయే 7 రోజుల్లో {place}కు ముఖ్యమైన వాతావరణ హెచ్చరికలు ఏవీ లేవు.",
  "निर्धारित सीमाओं के आधार पर अगले 7 दिनों में {place} के लिए कोई महत्वपूर्ण मौसम अलर्ट नहीं है।")

# ---- chat replies ----
m("reply.now", "Right now in {place}: {condition}, {temp}°C (feels like {feels}°C), humidity {hum}%, wind {wind} km/h.",
  "ప్రస్తుతం {place}లో: {condition}, {temp}°C (అనుభూతి {feels}°C), తేమ {hum}%, గాలి వేగం {wind} కి.మీ/గం.",
  "अभी {place} में: {condition}, {temp}°C (महसूस हो रहा है {feels}°C), नमी {hum}%, हवा {wind} किमी/घंटा।")
m("reply.day", "{day} in {place}: {condition}. Temperature {tmin}–{tmax}°C, chance of rain {prob}% ({mm} mm), wind up to {wind} km/h.",
  "{day} {place}లో: {condition}. ఉష్ణోగ్రత {tmin}–{tmax}°C, వర్షం పడే అవకాశం {prob}% ({mm} మి.మీ), గాలి గరిష్ఠంగా {wind} కి.మీ/గం.",
  "{day} {place} में: {condition}। तापमान {tmin}–{tmax}°C, बारिश की संभावना {prob}% ({mm} मिमी), हवा अधिकतम {wind} किमी/घंटा।")
m("reply.rain.likely", "{day} in {place}: rain is likely — {prob}% chance, about {mm} mm expected.",
  "{day} {place}లో వర్షం పడే అవకాశం ఎక్కువగా ఉంది — {prob}% సంభావ్యత, సుమారు {mm} మి.మీ.",
  "{day} {place} में बारिश की संभावना ज़्यादा है — {prob}% संभावना, लगभग {mm} मिमी।")
m("reply.rain.possible", "{day} in {place}: there is some chance of rain — {prob}% chance, about {mm} mm.",
  "{day} {place}లో వర్షం పడే అవకాశం కొంత ఉంది — {prob}% సంభావ్యత, సుమారు {mm} మి.మీ.",
  "{day} {place} में बारिश की कुछ संभावना है — {prob}% संभावना, लगभग {mm} मिमी।")
m("reply.rain.unlikely", "{day} in {place}: rain is unlikely ({prob}% chance, about {mm} mm).",
  "{day} {place}లో వర్షం పడే అవకాశం తక్కువ ({prob}% సంభావ్యత, సుమారు {mm} మి.మీ).",
  "{day} {place} में बारिश की संभावना कम है ({prob}% संभावना, लगभग {mm} मिमी)।")
m("reply.rain.timing", "Most likely around {start}–{end}.", "ఎక్కువగా {start}–{end} మధ్య పడే అవకాశం.", "ज़्यादा संभावना {start}–{end} के आसपास।")
m("reply.umbrella.yes", "Carry an umbrella or raincoat.", "గొడుగు లేదా రెయిన్‌కోట్ తీసుకెళ్లండి.", "छाता या रेनकोट साथ रखें।")
m("reply.umbrella.maybe", "An umbrella is a good idea, just in case.", "ముందు జాగ్రత్తగా గొడుగు తీసుకెళ్లడం మంచిది.", "एहतियात के तौर पर छाता रखना अच्छा रहेगा।")
m("reply.umbrella.no", "You probably won't need an umbrella.", "గొడుగు అవసరం ఉండకపోవచ్చు.", "शायद छाते की ज़रूरत नहीं पड़ेगी।")
m("reply.temp.now", "Right now in {place} it is {temp}°C (feels like {feels}°C). Today's range: {tmin}–{tmax}°C.",
  "ప్రస్తుతం {place}లో {temp}°C (అనుభూతి {feels}°C). ఈ రోజు పరిధి: {tmin}–{tmax}°C.",
  "अभी {place} में {temp}°C है (महसूस हो रहा है {feels}°C)। आज का दायरा: {tmin}–{tmax}°C।")
m("reply.temp.day", "{day} in {place}: between {tmin}°C and {tmax}°C.", "{day} {place}లో: {tmin}°C నుండి {tmax}°C వరకు.", "{day} {place} में: {tmin}°C से {tmax}°C के बीच।")
m("reply.wind", "{day} in {place}: wind up to {wind} km/h, gusts up to {gust} km/h.",
  "{day} {place}లో: గాలి వేగం {wind} కి.మీ/గం వరకు, ఝంఝలు {gust} కి.మీ/గం వరకు.",
  "{day} {place} में: हवा {wind} किमी/घंटा तक, झोंके {gust} किमी/घंटा तक।")
m("reply.humidity", "{day} in {place}: relative humidity around {hum}%.", "{day} {place}లో: సాపేక్ష తేమ సుమారు {hum}%.", "{day} {place} में: सापेक्ष आर्द्रता लगभग {hum}%।")
m("reply.travel.ok", "{day} in {place}: conditions look fine for travel — no major weather concerns in the data.",
  "{day} {place}లో: ప్రయాణానికి పరిస్థితులు బాగానే ఉన్నాయి — డేటాలో పెద్ద వాతావరణ సమస్యలు కనిపించలేదు.",
  "{day} {place} में: यात्रा के लिए स्थिति ठीक लगती है — डेटा में कोई बड़ी मौसमी चिंता नहीं दिखती।")
m("reply.travel.caution", "{day} in {place}: travel is possible but take care — {reasons}.",
  "{day} {place}లో: ప్రయాణం చేయవచ్చు కానీ జాగ్రత్తగా ఉండండి — {reasons}.",
  "{day} {place} में: यात्रा संभव है लेकिन सावधानी रखें — {reasons}।")
m("reply.travel.avoid", "{day} in {place}: avoid non-essential travel if you can — {reasons}.",
  "{day} {place}లో: వీలైతే అవసరం లేని ప్రయాణాలను నివారించండి — {reasons}.",
  "{day} {place} में: हो सके तो गैर-ज़रूरी यात्रा से बचें — {reasons}।")
m("reason.rain", "{prob}% chance of rain ({mm} mm)", "వర్షం పడే అవకాశం {prob}% ({mm} మి.మీ)", "बारिश की {prob}% संभावना ({mm} मिमी)")
m("reason.wind", "gusts up to {gust} km/h", "ఝంఝలు {gust} కి.మీ/గం వరకు", "झोंके {gust} किमी/घंटा तक")
m("reason.heat", "temperature up to {temp}°C", "ఉష్ణోగ్రత {temp}°C వరకు", "तापमान {temp}°C तक")
m("reason.thunder", "thunderstorm possible", "ఉరుములతో కూడిన తుఫాను అవకాశం", "गरज-तूफ़ान की संभावना")
m("reason.fog", "low visibility ({vis} km)", "తక్కువ దృశ్యమానత ({vis} కి.మీ)", "कम दृश्यता ({vis} किमी)")
m("reason.alert", "active advisory: {title}", "సక్రియ సూచన: {title}", "सक्रिय परामर्श: {title}")
m("line.day", "{date}: {condition}, {tmin}–{tmax}°C, rain {prob}%", "{date}: {condition}, {tmin}–{tmax}°C, వర్షం {prob}%", "{date}: {condition}, {tmin}–{tmax}°C, बारिश {prob}%")
m("reply.week.intro", "Forecast for {place}:", "{place} కోసం సూచన:", "{place} के लिए पूर्वानुमान:")
m("reply.alerts.intro", "Weather alerts for {place}:", "{place} కోసం వాతావరణ హెచ్చరికలు:", "{place} के लिए मौसम अलर्ट:")
m("reply.no_place", "Which place do you mean? Please tell me a city or town name.", "మీరు ఏ ప్రాంతం గురించి అడుగుతున్నారు? దయచేసి నగరం లేదా పట్టణం పేరు చెప్పండి.", "आप किस स्थान के बारे में पूछ रहे हैं? कृपया शहर या कस्बे का नाम बताएं।")
m("reply.not_found", "I couldn't find “{query}”. Please check the spelling or try a nearby city.", "“{query}” కనుగొనలేకపోయాను. స్పెల్లింగ్ తనిఖీ చేయండి లేదా సమీప నగరాన్ని ప్రయత్నించండి.", "“{query}” नहीं मिला। कृपया वर्तनी जाँचें या पास का कोई शहर आज़माएं।")
m("reply.error", "I couldn't get the data right now. Please try again in a moment.", "ప్రస్తుతం డేటా పొందలేకపోయాను. దయచేసి కొద్దిసేపటి తర్వాత మళ్లీ ప్రయత్నించండి.", "अभी डेटा नहीं मिल सका। कृपया थोड़ी देर बाद फिर कोशिश करें।")
m("reply.ai_note", "ℹ️ The AI explanation is unavailable right now, so this answer is based directly on the weather data.", "ℹ️ AI వివరణ ప్రస్తుతం అందుబాటులో లేదు, కాబట్టి ఈ సమాధానం నేరుగా వాతావరణ డేటా ఆధారంగా ఇవ్వబడింది.", "ℹ️ AI व्याख्या अभी उपलब्ध नहीं है, इसलिए यह उत्तर सीधे मौसम डेटा पर आधारित है।")
m("reply.mock_note", "⚠️ Live weather data is unavailable; these values are sample data and NOT real-time.", "⚠️ ప్రత్యక్ష వాతావరణ డేటా అందుబాటులో లేదు; ఈ విలువలు నమూనా డేటా మాత్రమే, నిజ-సమయ డేటా కాదు.", "⚠️ लाइव मौसम डेटा उपलब्ध नहीं है; ये मान नमूना डेटा हैं, रीयल-टाइम नहीं।")
m("reply.safety.intro", "Safety advice ({topic}) for {place}:", "{place} కోసం భద్రతా సూచనలు ({topic}):", "{place} के लिए सुरक्षा सुझाव ({topic}):")
m("reply.safety.active", "Currently forecast: {title}.", "ప్రస్తుత అంచనా: {title}.", "वर्तमान पूर्वानुमान: {title}।")
m("topic.heat", "heat", "వేడి", "गर्मी")
m("topic.rain", "heavy rain / flooding", "భారీ వర్షం / వరదలు", "भारी बारिश / बाढ़")
m("topic.thunderstorm", "thunderstorm", "ఉరుములు", "गरज-तूफ़ान")
m("topic.wind", "strong wind", "బలమైన గాలులు", "तेज़ हवा")
m("reply.climate.intro", "Climate analysis for {place} — {param}, {y1}–{y2}:", "{place} కోసం వాతావరణ విశ్లేషణ — {param}, {y1}–{y2}:", "{place} के लिए जलवायु विश्लेषण — {param}, {y1}–{y2}:")
m("disclaimer.general", "Varsha AI is informational. For critical decisions follow official IMD and local authority advisories.", "Varsha AI సమాచారం కోసం మాత్రమే. కీలక నిర్ణయాల కోసం అధికారిక IMD, స్థానిక అధికారుల సూచనలను పాటించండి.", "Varsha AI केवल जानकारी के लिए है। महत्वपूर्ण निर्णयों के लिए आधिकारिक IMD और स्थानीय प्राधिकरणों की सलाह मानें।")

# ---- climate ----
m("climate.observed", "Observed: yearly {param} ({agg}) averaged {mean} {unit}; highest in {maxyear} ({maxval} {unit}), lowest in {minyear} ({minval} {unit}).",
  "గమనించినవి: వార్షిక {param} ({agg}) సగటు {mean} {unit}; అత్యధికం {maxyear}లో ({maxval} {unit}), అత్యల్పం {minyear}లో ({minval} {unit}).",
  "प्रेक्षित: वार्षिक {param} ({agg}) का औसत {mean} {unit}; सबसे अधिक {maxyear} में ({maxval} {unit}), सबसे कम {minyear} में ({minval} {unit})।")
m("agg.total", "total", "మొత్తం", "कुल")
m("agg.mean", "mean", "సగటు", "औसत")
m("climate.trend.up", "Statistical trend: increasing by about {slope} {unit} per decade (R²={r2}, {n} years){sig}.",
  "గణాంక ధోరణి: దశాబ్దానికి సుమారు {slope} {unit} పెరుగుదల (R²={r2}, {n} సంవత్సరాలు){sig}.",
  "सांख्यिकीय रुझान: प्रति दशक लगभग {slope} {unit} की वृद्धि (R²={r2}, {n} वर्ष){sig}।")
m("climate.trend.down", "Statistical trend: decreasing by about {slope} {unit} per decade (R²={r2}, {n} years){sig}.",
  "గణాంక ధోరణి: దశాబ్దానికి సుమారు {slope} {unit} తగ్గుదల (R²={r2}, {n} సంవత్సరాలు){sig}.",
  "सांख्यिकीय रुझान: प्रति दशक लगभग {slope} {unit} की कमी (R²={r2}, {n} वर्ष){sig}।")
m("climate.trend.none", "Statistical trend: no clear linear trend (slope {slope} {unit} per decade, R²={r2}, {n} years).",
  "గణాంక ధోరణి: స్పష్టమైన రేఖీయ ధోరణి లేదు (దశాబ్దానికి {slope} {unit}, R²={r2}, {n} సంవత్సరాలు).",
  "सांख्यिकीय रुझान: कोई स्पष्ट रैखिक रुझान नहीं (प्रति दशक {slope} {unit}, R²={r2}, {n} वर्ष)।")
m("climate.sig.yes", ", statistically significant at the 95% level", ", 95% స్థాయిలో గణాంకపరంగా ముఖ్యమైనది", ", 95% स्तर पर सांख्यिकीय रूप से महत्वपूर्ण")
m("climate.sig.no", ", not statistically significant at the 95% level", ", 95% స్థాయిలో గణాంకపరంగా ముఖ్యమైనది కాదు", ", 95% स्तर पर सांख्यिकीय रूप से महत्वपूर्ण नहीं")
m("climate.interp.up", "Interpretation: values were generally higher in later years of this record. A short record from one location cannot by itself prove long-term climate change; year-to-year variability is large.",
  "వివరణ: ఈ రికార్డులో తరువాతి సంవత్సరాల్లో విలువలు సాధారణంగా ఎక్కువగా ఉన్నాయి. ఒక ప్రాంతానికి సంబంధించిన చిన్న రికార్డు మాత్రమే దీర్ఘకాలిక వాతావరణ మార్పును నిరూపించలేదు; సంవత్సరం నుండి సంవత్సరానికి వ్యత్యాసం ఎక్కువగా ఉంటుంది.",
  "व्याख्या: इस रिकॉर्ड में बाद के वर्षों में मान आम तौर पर अधिक रहे। एक स्थान का छोटा रिकॉर्ड अकेले दीर्घकालिक जलवायु परिवर्तन साबित नहीं कर सकता; वर्ष-दर-वर्ष उतार-चढ़ाव बड़ा होता है।")
m("climate.interp.down", "Interpretation: values were generally lower in later years of this record. A short record from one location cannot by itself prove long-term climate change; year-to-year variability is large.",
  "వివరణ: ఈ రికార్డులో తరువాతి సంవత్సరాల్లో విలువలు సాధారణంగా తక్కువగా ఉన్నాయి. ఒక ప్రాంతానికి సంబంధించిన చిన్న రికార్డు మాత్రమే దీర్ఘకాలిక వాతావరణ మార్పును నిరూపించలేదు; సంవత్సరం నుండి సంవత్సరానికి వ్యత్యాసం ఎక్కువగా ఉంటుంది.",
  "व्याख्या: इस रिकॉर्ड में बाद के वर्षों में मान आम तौर पर कम रहे। एक स्थान का छोटा रिकॉर्ड अकेले दीर्घकालिक जलवायु परिवर्तन साबित नहीं कर सकता; वर्ष-दर-वर्ष उतार-चढ़ाव बड़ा होता है।")
m("climate.interp.none", "Interpretation: year-to-year variation dominates and no consistent direction is visible in this record.",
  "వివరణ: సంవత్సరం నుండి సంవత్సరానికి వ్యత్యాసమే ఎక్కువగా ఉంది; ఈ రికార్డులో స్థిరమైన దిశ కనిపించడం లేదు.",
  "व्याख्या: इस रिकॉर्ड में वर्ष-दर-वर्ष बदलाव हावी है और कोई स्थिर दिशा नहीं दिखती।")
m("climate.caveat.era5", "Data are ERA5 reanalysis (model-based, roughly 9–25 km grid), not station or rain-gauge observations; local values can differ, especially for rainfall.",
  "డేటా ERA5 రీఅనాలిసిస్ (మోడల్ ఆధారిత, సుమారు 9–25 కి.మీ గ్రిడ్); స్టేషన్ లేదా వర్షమాపక కొలతలు కావు; ముఖ్యంగా వర్షపాతంలో స్థానిక విలువలు భిన్నంగా ఉండవచ్చు.",
  "डेटा ERA5 पुनर्विश्लेषण (मॉडल-आधारित, लगभग 9–25 किमी ग्रिड) है, स्टेशन या वर्षामापी के प्रेक्षण नहीं; स्थानीय मान, खासकर वर्षा में, भिन्न हो सकते हैं।")
m("climate.caveat.region", "This place is a state/region; the analysis uses its central point, not an area average.",
  "ఇది రాష్ట్రం/ప్రాంతం; విశ్లేషణ ఆ ప్రాంతపు కేంద్ర బిందువును ఉపయోగిస్తుంది, ప్రాంత సగటును కాదు.",
  "यह एक राज्य/क्षेत्र है; विश्लेषण उसके केंद्रीय बिंदु पर आधारित है, क्षेत्र के औसत पर नहीं।")
m("climate.caveat.mock", "SAMPLE DATA: synthetic values for demonstration only — not observations.",
  "నమూనా డేటా: ప్రదర్శన కోసం కృత్రిమ విలువలు మాత్రమే — కొలతలు కావు.",
  "नमूना डेटा: केवल प्रदर्शन के लिए कृत्रिम मान — प्रेक्षण नहीं।")

# ---- decision support ----
m("verdict.agri.good", "Conditions look suitable for spraying.", "పిచికారీకి పరిస్థితులు అనుకూలంగా కనిపిస్తున్నాయి.", "छिड़काव के लिए परिस्थितियाँ अनुकूल लगती हैं।")
m("verdict.agri.caution", "Spraying is possible but conditions are not ideal.", "పిచికారీ చేయవచ్చు కానీ పరిస్థితులు అంత అనుకూలంగా లేవు.", "छिड़काव संभव है, लेकिन परिस्थितियाँ आदर्श नहीं हैं।")
m("verdict.agri.avoid", "Spraying is not recommended in these conditions.", "ఈ పరిస్థితుల్లో పిచికారీ చేయడం మంచిది కాదు.", "इन परिस्थितियों में छिड़काव की सलाह नहीं दी जाती।")
m("verdict.good", "No major weather concerns in the forecast data.", "అంచనా డేటాలో పెద్ద వాతావరణ సమస్యలు కనిపించలేదు.", "पूर्वानुमान डेटा में कोई बड़ी मौसमी चिंता नहीं दिखती।")
m("verdict.caution", "Some weather concerns — review the indicators below.", "కొన్ని వాతావరణ సమస్యలు ఉన్నాయి — కింది సూచికలను పరిశీలించండి.", "कुछ मौसमी चिंताएँ हैं — नीचे दिए संकेतकों को देखें।")
m("verdict.avoid", "Significant weather concerns — plan carefully and consider postponing exposed operations.", "గణనీయమైన వాతావరణ సమస్యలు ఉన్నాయి — జాగ్రత్తగా ప్రణాళిక చేయండి, బయటి కార్యకలాపాలను వాయిదా వేయడం పరిగణించండి.", "महत्वपूर्ण मौसमी चिंताएँ हैं — सावधानी से योजना बनाएं और खुले में होने वाले कार्य टालने पर विचार करें।")
m("verdict.info", "Informational summary.", "సమాచార సారాంశం.", "सूचनात्मक सारांश।")
m("check.rain", "Rain chance (daytime)", "వర్షం అవకాశం (పగటి సమయం)", "बारिश की संभावना (दिन)")
m("check.rain_mm", "Rainfall expected", "అంచనా వర్షపాతం", "अनुमानित वर्षा")
m("check.wind", "Wind speed (max)", "గాలి వేగం (గరిష్ఠం)", "हवा की गति (अधिकतम)")
m("check.gust", "Wind gusts (max)", "గాలి ఝంఝలు (గరిష్ఠం)", "हवा के झोंके (अधिकतम)")
m("check.temp", "Max temperature", "గరిష్ఠ ఉష్ణోగ్రత", "अधिकतम तापमान")
m("check.humidity", "Relative humidity", "సాపేక్ష తేమ", "सापेक्ष आर्द्रता")
m("check.vis", "Visibility (min)", "దృశ్యమానత (కనిష్ఠం)", "दृश्यता (न्यूनतम)")
m("check.thunder", "Thunderstorm", "ఉరుములతో కూడిన తుఫాను", "गरज-तूफ़ान")
m("check.waves", "Wave height (max)", "అలల ఎత్తు (గరిష్ఠం)", "लहरों की ऊँचाई (अधिकतम)")
m("check.rain24", "Rain, next 24 hours", "రాబోయే 24 గంటల్లో వర్షం", "अगले 24 घंटे में वर्षा")
m("check.rain72", "Rain, next 3 days", "రాబోయే 3 రోజుల్లో వర్షం", "अगले 3 दिन में वर्षा")
m("check.alerts", "Active advisories", "సక్రియ సూచనలు", "सक्रिय परामर्श")
m("check.rain_trend", "Rainfall trend (10 yr)", "వర్షపాత ధోరణి (10 సం.)", "वर्षा रुझान (10 वर्ष)")
m("check.heat_trend", "Temperature trend (10 yr)", "ఉష్ణోగ్రత ధోరణి (10 సం.)", "तापमान रुझान (10 वर्ष)")
m("check.cloud", "Cloud cover (mean)", "మేఘ ఆవరణ (సగటు)", "बादल (औसत)")
m("rec.agri.good", "Early morning (6–9 am) or evening is usually best. Follow the product label and your local agriculture officer's advice.", "ఉదయం (6–9) లేదా సాయంత్రం సాధారణంగా ఉత్తమం. ఉత్పత్తి లేబుల్, స్థానిక వ్యవసాయ అధికారి సలహాను పాటించండి.", "सुबह (6–9) या शाम का समय आम तौर पर सबसे अच्छा होता है। उत्पाद के लेबल और स्थानीय कृषि अधिकारी की सलाह मानें।")
m("rec.agri.rain", "Rain is possible — wait for a dry spell of at least 24 hours so the spray is not washed off.", "వర్షం పడే అవకాశం ఉంది — పిచికారీ కొట్టుకుపోకుండా కనీసం 24 గంటలు పొడి వాతావరణం కోసం వేచి ఉండండి.", "बारिश संभव है — कम से कम 24 घंटे सूखा मौसम रहने तक रुकें ताकि छिड़काव धुल न जाए।")
m("rec.agri.wind", "Wind can cause spray drift — spray in calmer early-morning or evening hours.", "గాలి వల్ల పిచికారీ మందు ఎగిరిపోవచ్చు — గాలి తక్కువగా ఉండే ఉదయం లేదా సాయంత్రం వేళల్లో చేయండి.", "हवा से छिड़काव बहक सकता है — शांत सुबह या शाम के समय छिड़कें।")
m("rec.agri.temp", "High heat increases evaporation and crop stress — spray in the early morning or late evening.", "అధిక వేడి వల్ల ఆవిరి, పంట ఒత్తిడి పెరుగుతాయి — ఉదయం లేదా సాయంత్రం ఆలస్యంగా చేయండి.", "अधिक गर्मी से वाष्पीकरण और फसल पर तनाव बढ़ता है — सुबह जल्दी या देर शाम छिड़कें।")
m("rec.agri.humidity", "Very low or very high humidity can reduce spray effectiveness — check the product label.", "చాలా తక్కువ లేదా ఎక్కువ తేమ పిచికారీ ప్రభావాన్ని తగ్గించవచ్చు — ఉత్పత్తి లేబుల్ చూడండి.", "बहुत कम या बहुत अधिक नमी से छिड़काव का असर घट सकता है — उत्पाद का लेबल देखें।")
m("rec.agri.irrigation", "Forecast rain may meet crop water needs — consider delaying irrigation.", "అంచనా వర్షం పంట నీటి అవసరాలు తీర్చవచ్చు — నీటి పారుదల వాయిదా వేయడం పరిగణించండి.", "अनुमानित बारिश फसल की पानी की ज़रूरत पूरी कर सकती है — सिंचाई टालने पर विचार करें।")
m("rec.aviation.good", "No major weather flags in the forecast data. Always use official aviation weather products (METAR/TAF/SIGMET).", "అంచనా డేటాలో పెద్ద వాతావరణ సంకేతాలు లేవు. ఎల్లప్పుడూ అధికారిక విమానయాన వాతావరణ సమాచారం (METAR/TAF/SIGMET) ఉపయోగించండి.", "पूर्वानुमान डेटा में कोई बड़ा मौसमी संकेत नहीं है। हमेशा आधिकारिक विमानन मौसम उत्पाद (METAR/TAF/SIGMET) उपयोग करें।")
m("rec.aviation.thunder", "Thunderstorm activity is indicated — expect possible delays or diversions.", "ఉరుములతో కూడిన తుఫాను సూచన ఉంది — ఆలస్యాలు లేదా మళ్లింపులు ఉండవచ్చు.", "गरज-तूफ़ान का संकेत है — देरी या मार्ग-परिवर्तन संभव है।")
m("rec.aviation.vis", "Reduced visibility may affect operations.", "తగ్గిన దృశ్యమానత కార్యకలాపాలను ప్రభావితం చేయవచ్చు.", "कम दृश्यता से संचालन प्रभावित हो सकता है।")
m("rec.aviation.wind", "Strong winds or gusts may affect take-off and landing.", "బలమైన గాలులు లేదా ఝంఝలు టేకాఫ్, ల్యాండింగ్‌ను ప్రభావితం చేయవచ్చు.", "तेज़ हवा या झोंके उड़ान भरने और उतरने को प्रभावित कर सकते हैं।")
m("rec.marine.good", "No major flags in the data. Always check official fishermen/marine warnings (INCOIS, IMD) before going to sea.", "డేటాలో పెద్ద సంకేతాలు లేవు. సముద్రంలోకి వెళ్లే ముందు అధికారిక మత్స్యకార/సముద్ర హెచ్చరికలు (INCOIS, IMD) తప్పక చూడండి.", "डेटा में कोई बड़ा संकेत नहीं है। समुद्र में जाने से पहले आधिकारिक मछुआरा/समुद्री चेतावनियाँ (INCOIS, IMD) ज़रूर देखें।")
m("rec.marine.wind", "Strong winds — small boats should avoid going out.", "బలమైన గాలులు — చిన్న పడవలు సముద్రంలోకి వెళ్లకపోవడం మంచిది.", "तेज़ हवा — छोटी नावों को समुद्र में नहीं जाना चाहिए।")
m("rec.marine.waves", "High waves — fishing in small boats is risky.", "ఎత్తైన అలలు — చిన్న పడవలతో చేపల వేట ప్రమాదకరం.", "ऊँची लहरें — छोटी नावों से मछली पकड़ना जोखिम भरा है।")
m("rec.marine.thunder", "Thunderstorm risk at sea — avoid going out or return to harbour.", "సముద్రంలో ఉరుముల తుఫాను ప్రమాదం — వెళ్లకండి లేదా ఓడరేవుకు తిరిగి రండి.", "समुद्र में गरज-तूफ़ान का जोखिम — न जाएं या बंदरगाह लौट आएं।")
m("rec.marine.rain", "Heavy rain can reduce visibility at sea.", "భారీ వర్షం సముద్రంలో దృశ్యమానతను తగ్గించవచ్చు.", "भारी बारिश से समुद्र में दृश्यता घट सकती है।")
m("rec.disaster.none", "No alert-level hazards in the forecast. Stay informed through official channels.", "అంచనాలో హెచ్చరిక స్థాయి ప్రమాదాలు లేవు. అధికారిక మార్గాల ద్వారా సమాచారం తెలుసుకోండి.", "पूर्वानुमान में अलर्ट-स्तर का कोई खतरा नहीं है। आधिकारिक माध्यमों से जानकारी लेते रहें।")
m("rec.disaster.general", "Keep an emergency kit (water, torch, first aid, documents), charge phones and know your nearest shelter.", "అత్యవసర కిట్ (నీరు, టార్చ్, ప్రథమ చికిత్స, పత్రాలు) సిద్ధంగా ఉంచండి, ఫోన్లు ఛార్జ్ చేయండి, సమీప ఆశ్రయం తెలుసుకోండి.", "आपातकालीन किट (पानी, टॉर्च, प्राथमिक उपचार, दस्तावेज़) तैयार रखें, फ़ोन चार्ज रखें और नज़दीकी आश्रय जानें।")
m("rec.urban.rain_up", "Rainfall has been trending upward — review drainage capacity and flood-prone zones.", "వర్షపాతం పెరిగే ధోరణిలో ఉంది — డ్రైనేజీ సామర్థ్యం, వరద ప్రమాద ప్రాంతాలను సమీక్షించండి.", "वर्षा का रुझान बढ़ रहा है — जल-निकासी क्षमता और बाढ़-प्रवण क्षेत्रों की समीक्षा करें।")
m("rec.urban.heat_up", "Temperatures have been trending upward — consider shade, green cover and cool roofs.", "ఉష్ణోగ్రతలు పెరిగే ధోరణిలో ఉన్నాయి — నీడ, పచ్చదనం, కూల్ రూఫ్‌లను పరిగణించండి.", "तापमान का रुझान बढ़ रहा है — छाया, हरित आवरण और कूल रूफ़ पर विचार करें।")
m("rec.urban.near_rain", "Heavy rain is forecast in the next 3 days — inspect drains and low-lying areas now.", "రాబోయే 3 రోజుల్లో భారీ వర్షం అంచనా — ఇప్పుడే డ్రైన్లు, లోతట్టు ప్రాంతాలను తనిఖీ చేయండి.", "अगले 3 दिनों में भारी बारिश का अनुमान — अभी नालियों और निचले इलाकों की जाँच करें।")
m("rec.urban.none", "No major flags; keep using long-term climate data for infrastructure planning.", "పెద్ద సంకేతాలు లేవు; మౌలిక సదుపాయాల ప్రణాళికకు దీర్ఘకాలిక వాతావరణ డేటాను ఉపయోగించండి.", "कोई बड़ा संकेत नहीं; बुनियादी ढांचे की योजना के लिए दीर्घकालिक जलवायु डेटा का उपयोग करते रहें।")
m("disclaimer.agri", "General guidance only — not a substitute for advice from agricultural experts or the product label.", "ఇది సాధారణ మార్గదర్శకం మాత్రమే — వ్యవసాయ నిపుణుల సలహా లేదా ఉత్పత్తి లేబుల్‌కు ప్రత్యామ్నాయం కాదు.", "यह केवल सामान्य मार्गदर्शन है — कृषि विशेषज्ञों की सलाह या उत्पाद के लेबल का विकल्प नहीं।")
m("disclaimer.aviation", "Informational only. Not an aviation-certified decision system; use official aviation weather services for flight planning.", "సమాచారం కోసం మాత్రమే. ఇది విమానయాన-ధృవీకృత నిర్ణయ వ్యవస్థ కాదు; విమాన ప్రణాళికకు అధికారిక విమానయాన వాతావరణ సేవలను ఉపయోగించండి.", "केवल जानकारी के लिए। यह विमानन-प्रमाणित निर्णय प्रणाली नहीं है; उड़ान योजना के लिए आधिकारिक विमानन मौसम सेवाओं का उपयोग करें।")
m("disclaimer.marine", "Informational only. Follow official marine and fishermen warnings (INCOIS/IMD) and port authority instructions.", "సమాచారం కోసం మాత్రమే. అధికారిక సముద్ర/మత్స్యకార హెచ్చరికలు (INCOIS/IMD), ఓడరేవు అధికారుల సూచనలను పాటించండి.", "केवल जानकारी के लिए। आधिकारिक समुद्री/मछुआरा चेतावनियों (INCOIS/IMD) और बंदरगाह प्राधिकरण के निर्देशों का पालन करें।")
m("disclaimer.disaster", "Forecast-based indicators, not official warnings. Coordinate with NDMA/SDMA/IMD and district authorities.", "అంచనా ఆధారిత సూచికలు మాత్రమే, అధికారిక హెచ్చరికలు కావు. NDMA/SDMA/IMD, జిల్లా అధికారులతో సమన్వయం చేసుకోండి.", "ये पूर्वानुमान-आधारित संकेतक हैं, आधिकारिक चेतावनी नहीं। NDMA/SDMA/IMD और ज़िला प्रशासन से समन्वय करें।")
m("disclaimer.urban", "Planning aid only; combine with local hydrological studies and official climate datasets.", "ప్రణాళిక సహాయం మాత్రమే; స్థానిక జలశాస్త్ర అధ్యయనాలు, అధికారిక వాతావరణ డేటాసెట్‌లతో కలిపి ఉపయోగించండి.", "केवल योजना सहायता; स्थानीय जल-विज्ञान अध्ययनों और आधिकारिक जलवायु डेटासेट के साथ उपयोग करें।")
