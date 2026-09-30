"""
Multilingual message templates for parent notifications.
All 10 languages supported for every notification type.
"""

TRANSLATIONS = {
    # ==========================================
    # LOW ATTENDANCE
    # ==========================================
    "low_attendance": {
        "en": {
            "subject": "Low Attendance Alert for {student_name}",
            "message": (
                "Dear {parent_name},\n\n"
                "This is to inform you that {student_name} "
                "(Reg. No: {register_number}) currently has an attendance "
                "of {percentage}% in {department}.\n\n"
                "The required minimum attendance is {required}%.\n\n"
                "{student_name} is {gap}% below the required attendance. "
                "Please ensure regular attendance to avoid any academic issues.\n\n"
                "Department: {department}\n"
                "College: {college}\n\n"
                "Regards,\n"
                "Attendance Management System"
            ),
        },
        "hi": {
            "subject": "{student_name} के लिए कम उपस्थिति चेतावनी",
            "message": (
                "प्रिय {parent_name},\n\n"
                "हम आपको सूचित करना चाहते हैं कि {student_name} "
                "(रजिस्टर संख्या: {register_number}) की वर्तमान उपस्थिति "
                "{department} में {percentage}% है।\n\n"
                "आवश्यक न्यूनतम उपस्थिति {required}% है।\n\n"
                "{student_name} आवश्यक उपस्थिति से {gap}% कम है। "
                "कृपया नियमित उपस्थिति सुनिश्चित करें।\n\n"
                "विभाग: {department}\n"
                "कॉलेज: {college}\n\n"
                "सादर,\n"
                "उपस्थिति प्रबंधन प्रणाली"
            ),
        },
        "ta": {
            "subject": "{student_name} க்கான குறைந்த வருகை எச்சரிக்கை",
            "message": (
                "அன்புள்ள {parent_name},\n\n"
                "{student_name} (பதிவு எண்: {register_number}) "
                "தற்போது {department} இல் {percentage}% வருகை "
                "வைத்துள்ளார் என்பதை தெரிவிக்கிறோம்.\n\n"
                "தேவையான குறைந்தபட்ச வருகை {required}% ஆகும்.\n\n"
                "{student_name} தேவையான வருகையை விட {gap}% குறைவாக உள்ளார். "
                "தயவுசெய்து வழக்கமான வருகையை உறுதிப்படுத்தவும்.\n\n"
                "துறை: {department}\n"
                "கல்லூரி: {college}\n\n"
                "அன்புடன்,\n"
                "வருகை மேலாண்மை அமைப்பு"
            ),
        },
        "te": {
            "subject": "{student_name} కోసం తక్కువ హాజరు హెచ్చరిక",
            "message": (
                "ప్రియమైన {parent_name},\n\n"
                "{student_name} (నమోదు సంఖ్య: {register_number}) "
                "{department} లో ప్రస్తుతం {percentage}% హాజరు "
                "కలిగి ఉన్నారని తెలియజేయడానికి ఈ లేఖ.\n\n"
                "అవసరమైన కనీస హాజరు {required}%.\n\n"
                "{student_name} అవసరమైన హాజరు కంటే {gap}% తక్కువగా ఉన్నారు. "
                "దయచేసి క్రమమైన హాజరును నిర్ధారించండి.\n\n"
                "విభాగం: {department}\n"
                "కళాశాల: {college}\n\n"
                "భవదీయులు,\n"
                "హాజరు నిర్వహణ వ్యవస్థ"
            ),
        },
        "ml": {
            "subject": "{student_name} ന് കുറഞ്ഞ ഹാജർ മുന്നറിയിപ്പ്",
            "message": (
                "പ്രിയ {parent_name},\n\n"
                "{student_name} (രജിസ്റ്റർ നമ്പർ: {register_number}) "
                "{department} ൽ നിലവിൽ {percentage}% ഹാജർ "
                "ഉണ്ടെന്ന് അറിയിക്കുന്നു.\n\n"
                "ആവശ്യമായ കുറഞ്ഞ ഹാജർ {required}% ആണ്.\n\n"
                "{student_name} ആവശ്യമായ ഹാജറിനേക്കാൾ {gap}% കുറവാണ്. "
                "ദയവായി സ്ഥിരമായ ഹാജർ ഉറപ്പാക്കുക.\n\n"
                "വിഭാഗം: {department}\n"
                "കോളേജ്: {college}\n\n"
                "ആദരവോടെ,\n"
                "ഹാജർ മാനേജ്മെന്റ് സിസ്റ്റം"
            ),
        },
        "kn": {
            "subject": "{student_name} ಗಾಗಿ ಕಡಿಮೆ ಹಾಜರಿ ಎಚ್ಚರಿಕೆ",
            "message": (
                "ಆತ್ಮೀಯ {parent_name},\n\n"
                "{student_name} (ನೋಂದಣಿ ಸಂಖ್ಯೆ: {register_number}) "
                "{department} ನಲ್ಲಿ ಪ್ರಸ್ತುತ {percentage}% ಹಾಜರಿ "
                "ಹೊಂದಿದ್ದಾರೆ ಎಂದು ತಿಳಿಸಲು ಬಯಸುತ್ತೇವೆ.\n\n"
                "ಅಗತ್ಯವಿರುವ ಕನಿಷ್ಠ ಹಾಜರಿ {required}%.\n\n"
                "{student_name} ಅಗತ್ಯಕ್ಕಿಂತ {gap}% ಕಡಿಮೆ ಇದ್ದಾರೆ. "
                "ದಯವಿಟ್ಟು ನಿಯಮಿತ ಹಾಜರಿಯನ್ನು ಖಚಿತಪಡಿಸಿ.\n\n"
                "ವಿಭಾಗ: {department}\n"
                "ಕಾಲೇಜು: {college}\n\n"
                "ವಂದನೆಗಳೊಂದಿಗೆ,\n"
                "ಹಾಜರಿ ನಿರ್ವಹಣಾ ವ್ಯವಸ್ಥೆ"
            ),
        },
        "mr": {
            "subject": "{student_name} साठी कमी उपस्थितीची सूचना",
            "message": (
                "प्रिय {parent_name},\n\n"
                "आम्ही तुम्हाला कळवू इच्छितो की {student_name} "
                "(नोंदणी क्रमांक: {register_number}) ची "
                "{department} मध्ये सध्याची उपस्थिती {percentage}% आहे.\n\n"
                "आवश्यक किमान उपस्थिती {required}% आहे.\n\n"
                "{student_name} आवश्यक उपस्थितीपेक्षा {gap}% कमी आहे. "
                "कृपया नियमित उपस्थिती सुनिश्चित करा.\n\n"
                "विभाग: {department}\n"
                "महाविद्यालय: {college}\n\n"
                "सस्नेह,\n"
                "उपस्थिती व्यवस्थापन प्रणाली"
            ),
        },
        "bn": {
            "subject": "{student_name} এর জন্য কম উপস্থিতি সতর্কতা",
            "message": (
                "প্রিয় {parent_name},\n\n"
                "আমরা আপনাকে জানাতে চাই যে {student_name} "
                "(নিবন্ধন নম্বর: {register_number}) এর "
                "{department} এ বর্তমান উপস্থিতি {percentage}%।\n\n"
                "প্রয়োজনীয় ন্যূনতম উপস্থিতি {required}%।\n\n"
                "{student_name} প্রয়োজনীয় উপস্থিতির চেয়ে {gap}% কম। "
                "অনুগ্রহ করে নিয়মিত উপস্থিতি নিশ্চিত করুন।\n\n"
                "বিভাগ: {department}\n"
                "কলেজ: {college}\n\n"
                "শুভেচ্ছান্তে,\n"
                "উপস্থিতি ব্যবস্থাপনা সিস্টেম"
            ),
        },
        "gu": {
            "subject": "{student_name} માટે ઓછી હાજરીની ચેતવણી",
            "message": (
                "પ્રિય {parent_name},\n\n"
                "અમે તમને જાણ કરવા માંગીએ છીએ કે {student_name} "
                "(નોંધણી નંબર: {register_number}) ની "
                "{department} માં હાલની હાજરી {percentage}% છે.\n\n"
                "જરૂરી લઘુત્તમ હાજરી {required}% છે.\n\n"
                "{student_name} જરૂરી હાજરી કરતાં {gap}% ઓછા છે. "
                "કૃપા કરીને નિયમિત હાજરી સુનિશ્ચિત કરો.\n\n"
                "વિભાગ: {department}\n"
                "કૉલેજ: {college}\n\n"
                "સાદર,\n"
                "હાજરી વ્યવસ્થાપન સિસ્ટમ"
            ),
        },
        "pa": {
            "subject": "{student_name} ਲਈ ਘੱਟ ਹਾਜ਼ਰੀ ਦੀ ਚੇਤਾਵਨੀ",
            "message": (
                "ਪਿਆਰੇ {parent_name},\n\n"
                "ਅਸੀਂ ਤੁਹਾਨੂੰ ਦੱਸਣਾ ਚਾਹੁੰਦੇ ਹਾਂ ਕਿ {student_name} "
                "(ਰਜਿਸਟਰ ਨੰਬਰ: {register_number}) ਦੀ "
                "{department} ਵਿੱਚ ਮੌਜੂਦਾ ਹਾਜ਼ਰੀ {percentage}% ਹੈ।\n\n"
                "ਲੋੜੀਂਦੀ ਘੱਟੋ-ਘੱਟ ਹਾਜ਼ਰੀ {required}% ਹੈ।\n\n"
                "{student_name} ਲੋੜੀਂਦੀ ਹਾਜ਼ਰੀ ਤੋਂ {gap}% ਘੱਟ ਹੈ। "
                "ਕਿਰਪਾ ਕਰਕੇ ਨਿਯਮਿਤ ਹਾਜ਼ਰੀ ਨੂੰ ਯਕੀਨੀ ਬਣਾਓ।\n\n"
                "ਵਿਭਾਗ: {department}\n"
                "ਕਾਲਜ: {college}\n\n"
                "ਸਤਿਕਾਰ ਸਹਿਤ,\n"
                "ਹਾਜ਼ਰੀ ਪ੍ਰਬੰਧਨ ਸਿਸਟਮ"
            ),
        },
    },

    # ==========================================
    # CRITICAL ATTENDANCE
    # ==========================================
    "critical_attendance": {
        "en": {
            "subject": "⚠ Critical Attendance Warning for {student_name}",
            "message": (
                "Dear {parent_name},\n\n"
                "URGENT: {student_name} (Reg: {register_number}) "
                "has CRITICALLY LOW attendance of {percentage}% "
                "in {department}.\n\n"
                "Required: {required}%\n"
                "Current: {percentage}%\n"
                "Gap: {gap}%\n\n"
                "Immediate action is required. Please contact the "
                "department immediately to discuss this matter.\n\n"
                "Regards,\n"
                "Attendance Management System"
            ),
        },
        "hi": {
            "subject": "⚠ {student_name} के लिए गंभीर उपस्थिति चेतावनी",
            "message": (
                "प्रिय {parent_name},\n\n"
                "अत्यावश्यक: {student_name} (रजि: {register_number}) की "
                "{department} में अत्यंत कम उपस्थिति {percentage}% है।\n\n"
                "आवश्यक: {required}%\n"
                "वर्तमान: {percentage}%\n"
                "कमी: {gap}%\n\n"
                "तत्काल कार्रवाई की आवश्यकता है। कृपया विभाग से संपर्क करें।\n\n"
                "सादर,\n"
                "उपस्थिति प्रबंधन प्रणाली"
            ),
        },
        "ta": {
            "subject": "⚠ {student_name} க்கான தீவிர வருகை எச்சரிக்கை",
            "message": (
                "அன்புள்ள {parent_name},\n\n"
                "அவசரம்: {student_name} (பதிவு: {register_number}) "
                "{department} இல் {percentage}% மிகக் குறைந்த "
                "வருகையைக் கொண்டுள்ளார்.\n\n"
                "தேவை: {required}%\n"
                "தற்போதைய: {percentage}%\n"
                "இடைவெளி: {gap}%\n\n"
                "உடனடி நடவடிக்கை தேவை. தயவுசெய்து துறையைத் தொடர்பு கொள்ளவும்.\n\n"
                "அன்புடன்,\n"
                "வருகை மேலாண்மை அமைப்பு"
            ),
        },
        "te": {
            "subject": "⚠ {student_name} కోసం తీవ్రమైన హాజరు హెచ్చరిక",
            "message": (
                "ప్రియమైన {parent_name},\n\n"
                "అత్యవసరం: {student_name} (నమోదు: {register_number}) "
                "{department} లో {percentage}% అత్యంత తక్కువ "
                "హాజరు కలిగి ఉన్నారు.\n\n"
                "అవసరం: {required}%\n"
                "ప్రస్తుతం: {percentage}%\n"
                "తేడా: {gap}%\n\n"
                "తక్షణ చర్య అవసరం. దయచేసి విభాగాన్ని సంప్రదించండి.\n\n"
                "భవదీయులు,\n"
                "హాజరు నిర్వహణ వ్యవస్థ"
            ),
        },
        "ml": {
            "subject": "⚠ {student_name} ന് ഗുരുതരമായ ഹാജർ മുന്നറിയിപ്പ്",
            "message": (
                "പ്രിയ {parent_name},\n\n"
                "അടിയന്തിരം: {student_name} (രജിസ്റ്റർ: {register_number}) "
                "{department} ൽ {percentage}% അതീവ കുറഞ്ഞ "
                "ഹാജർ ഉണ്ട്.\n\n"
                "ആവശ്യം: {required}%\n"
                "നിലവിൽ: {percentage}%\n"
                "വ്യത്യാസം: {gap}%\n\n"
                "ഉടനടി നടപടി ആവശ്യമാണ്. ദയവായി വിഭാഗവുമായി ബന്ധപ്പെടുക.\n\n"
                "ആദരവോടെ,\n"
                "ഹാജർ മാനേജ്മെന്റ് സിസ്റ്റം"
            ),
        },
        "kn": {
            "subject": "⚠ {student_name} ಗಾಗಿ ಗಂಭೀರ ಹಾಜರಿ ಎಚ್ಚರಿಕೆ",
            "message": (
                "ಆತ್ಮೀಯ {parent_name},\n\n"
                "ತುರ್ತು: {student_name} (ನೋಂದಣಿ: {register_number}) "
                "{department} ನಲ್ಲಿ {percentage}% ಅತಿ ಕಡಿಮೆ "
                "ಹಾಜರಿ ಹೊಂದಿದ್ದಾರೆ.\n\n"
                "ಅಗತ್ಯ: {required}%\n"
                "ಪ್ರಸ್ತುತ: {percentage}%\n"
                "ವ್ಯತ್ಯಾಸ: {gap}%\n\n"
                "ತಕ್ಷಣ ಕ್ರಮ ಅಗತ್ಯ. ದಯವಿಟ್ಟು ವಿಭಾಗವನ್ನು ಸಂಪರ್ಕಿಸಿ.\n\n"
                "ವಂದನೆಗಳೊಂದಿಗೆ,\n"
                "ಹಾಜರಿ ನಿರ್ವಹಣಾ ವ್ಯವಸ್ಥೆ"
            ),
        },
        "mr": {
            "subject": "⚠ {student_name} साठी गंभीर उपस्थिती चेतावणी",
            "message": (
                "प्रिय {parent_name},\n\n"
                "तातडीचे: {student_name} (नोंदणी: {register_number}) ची "
                "{department} मध्ये {percentage}% अत्यंत कमी "
                "उपस्थिती आहे.\n\n"
                "आवश्यक: {required}%\n"
                "सध्याची: {percentage}%\n"
                "तफावत: {gap}%\n\n"
                "तात्काळ कारवाई आवश्यक. कृपया विभागाशी संपर्क साधा.\n\n"
                "सस्नेह,\n"
                "उपस्थिती व्यवस्थापन प्रणाली"
            ),
        },
        "bn": {
            "subject": "⚠ {student_name} এর জন্য গুরুতর উপস্থিতি সতর্কতা",
            "message": (
                "প্রিয় {parent_name},\n\n"
                "জরুরি: {student_name} (নিবন্ধন: {register_number}) এর "
                "{department} এ {percentage}% অত্যন্ত কম "
                "উপস্থিতি আছে।\n\n"
                "প্রয়োজন: {required}%\n"
                "বর্তমান: {percentage}%\n"
                "ব্যবধান: {gap}%\n\n"
                "অবিলম্বে পদক্ষেপ প্রয়োজন। অনুগ্রহ করে বিভাগের সাথে যোগাযোগ করুন।\n\n"
                "শুভেচ্ছান্তে,\n"
                "উপস্থিতি ব্যবস্থাপনা সিস্টেম"
            ),
        },
        "gu": {
            "subject": "⚠ {student_name} માટે ગંભીર હાજરી ચેતવણી",
            "message": (
                "પ્રિય {parent_name},\n\n"
                "તાત્કાલિક: {student_name} (નોંધણી: {register_number}) ની "
                "{department} માં {percentage}% અત્યંત ઓછી "
                "હાજરી છે.\n\n"
                "જરૂરી: {required}%\n"
                "વર્તમાન: {percentage}%\n"
                "તફાવત: {gap}%\n\n"
                "તાત્કાલિક પગલાં જરૂરી. કૃપા કરીને વિભાગનો સંપર્ક કરો.\n\n"
                "સાદર,\n"
                "હાજરી વ્યવસ્થાપન સિસ્ટમ"
            ),
        },
        "pa": {
            "subject": "⚠ {student_name} ਲਈ ਗੰਭੀਰ ਹਾਜ਼ਰੀ ਚੇਤਾਵਨੀ",
            "message": (
                "ਪਿਆਰੇ {parent_name},\n\n"
                "ਫੌਰੀ: {student_name} (ਰਜਿਸਟਰ: {register_number}) ਦੀ "
                "{department} ਵਿੱਚ {percentage}% ਬਹੁਤ ਘੱਟ "
                "ਹਾਜ਼ਰੀ ਹੈ।\n\n"
                "ਲੋੜ: {required}%\n"
                "ਮੌਜੂਦਾ: {percentage}%\n"
                "ਅੰਤਰ: {gap}%\n\n"
                "ਤੁਰੰਤ ਕਾਰਵਾਈ ਦੀ ਲੋੜ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਵਿਭਾਗ ਨਾਲ ਸੰਪਰਕ ਕਰੋ।\n\n"
                "ਸਤਿਕਾਰ ਸਹਿਤ,\n"
                "ਹਾਜ਼ਰੀ ਪ੍ਰਬੰਧਨ ਸਿਸਟਮ"
            ),
        },
    },

    # ==========================================
    # WEEKLY SUMMARY
    # ==========================================
    "weekly_summary": {
        "en": {
            "subject": "Weekly Attendance Summary for {student_name}",
            "message": (
                "Dear {parent_name},\n\n"
                "Here is the weekly attendance summary for "
                "{student_name} (Reg: {register_number}):\n\n"
                "📅 Week: {week_start} to {week_end}\n"
                "✅ Present: {present} classes\n"
                "❌ Absent: {absent} classes\n"
                "📊 Weekly Attendance: {percentage}%\n\n"
                "📈 Overall attendance: {overall_percentage}%\n"
                "🎯 Required: {required}%\n\n"
                "Keep encouraging regular attendance!\n\n"
                "Regards,\n"
                "Attendance Management System"
            ),
        },
        "hi": {
            "subject": "{student_name} के लिए साप्ताहिक उपस्थिति सारांश",
            "message": (
                "प्रिय {parent_name},\n\n"
                "{student_name} (रजि: {register_number}) का "
                "साप्ताहिक उपस्थिति सारांश:\n\n"
                "📅 सप्ताह: {week_start} से {week_end}\n"
                "✅ उपस्थित: {present} कक्षाएँ\n"
                "❌ अनुपस्थित: {absent} कक्षाएँ\n"
                "📊 साप्ताहिक उपस्थिति: {percentage}%\n\n"
                "📈 कुल उपस्थिति: {overall_percentage}%\n"
                "🎯 आवश्यक: {required}%\n\n"
                "नियमित उपस्थिति के लिए प्रोत्साहित करें!\n\n"
                "सादर,\n"
                "उपस्थिति प्रबंधन प्रणाली"
            ),
        },
        "ta": {
            "subject": "{student_name} க்கான வாராந்திர வருகை சுருக்கம்",
            "message": (
                "அன்புள்ள {parent_name},\n\n"
                "{student_name} (பதிவு: {register_number}) இன் "
                "வாராந்திர வருகை சுருக்கம்:\n\n"
                "📅 வாரம்: {week_start} முதல் {week_end} வரை\n"
                "✅ வந்தது: {present} வகுப்புகள்\n"
                "❌ வரவில்லை: {absent} வகுப்புகள்\n"
                "📊 வாராந்திர வருகை: {percentage}%\n\n"
                "📈 ஒட்டுமொத்த வருகை: {overall_percentage}%\n"
                "🎯 தேவை: {required}%\n\n"
                "வழக்கமான வருகையை ஊக்குவிக்கவும்!\n\n"
                "அன்புடன்,\n"
                "வருகை மேலாண்மை அமைப்பு"
            ),
        },
        "te": {
            "subject": "{student_name} కోసం వారపు హాజరు సారాంశం",
            "message": (
                "ప్రియమైన {parent_name},\n\n"
                "{student_name} (నమోదు: {register_number}) యొక్క "
                "వారపు హాజరు సారాంశం:\n\n"
                "📅 వారం: {week_start} నుండి {week_end} వరకు\n"
                "✅ హాజరు: {present} తరగతులు\n"
                "❌ గైర్హాజరు: {absent} తరగతులు\n"
                "📊 వారపు హాజరు: {percentage}%\n\n"
                "📈 మొత్తం హాజరు: {overall_percentage}%\n"
                "🎯 అవసరం: {required}%\n\n"
                "క్రమమైన హాజరును ప్రోత్సహించండి!\n\n"
                "భవదీయులు,\n"
                "హాజరు నిర్వహణ వ్యవస్థ"
            ),
        },
        "ml": {
            "subject": "{student_name} നുള്ള പ്രതിവാര ഹാജർ സംഗ്രഹം",
            "message": (
                "പ്രിയ {parent_name},\n\n"
                "{student_name} (രജിസ്റ്റർ: {register_number}) ന്റെ "
                "പ്രതിവാര ഹാജർ സംഗ്രഹം:\n\n"
                "📅 ആഴ്ച: {week_start} മുതൽ {week_end} വരെ\n"
                "✅ ഹാജർ: {present} ക്ലാസുകൾ\n"
                "❌ ഹാജരില്ലാത്തത്: {absent} ക്ലാസുകൾ\n"
                "📊 പ്രതിവാര ഹാജർ: {percentage}%\n\n"
                "📈 മൊത്തം ഹാജർ: {overall_percentage}%\n"
                "🎯 ആവശ്യം: {required}%\n\n"
                "സ്ഥിരമായ ഹാജർ പ്രോത്സാഹിപ്പിക്കുക!\n\n"
                "ആദരവോടെ,\n"
                "ഹാജർ മാനേജ്മെന്റ് സിസ്റ്റം"
            ),
        },
        "kn": {
            "subject": "{student_name} ಗಾಗಿ ಸಾಪ್ತಾಹಿಕ ಹಾಜರಿ ಸಾರಾಂಶ",
            "message": (
                "ಆತ್ಮೀಯ {parent_name},\n\n"
                "{student_name} (ನೋಂದಣಿ: {register_number}) ರ "
                "ಸಾಪ್ತಾಹಿಕ ಹಾಜರಿ ಸಾರಾಂಶ:\n\n"
                "📅 ವಾರ: {week_start} ರಿಂದ {week_end} ವರೆಗೆ\n"
                "✅ ಹಾಜರು: {present} ತರಗತಿಗಳು\n"
                "❌ ಗೈರುಹಾಜರು: {absent} ತರಗತಿಗಳು\n"
                "📊 ಸಾಪ್ತಾಹಿಕ ಹಾಜರಿ: {percentage}%\n\n"
                "📈 ಒಟ್ಟು ಹಾಜರಿ: {overall_percentage}%\n"
                "🎯 ಅಗತ್ಯ: {required}%\n\n"
                "ನಿಯಮಿತ ಹಾಜರಿಯನ್ನು ಪ್ರೋತ್ಸಾಹಿಸಿ!\n\n"
                "ವಂದನೆಗಳೊಂದಿಗೆ,\n"
                "ಹಾಜರಿ ನಿರ್ವಹಣಾ ವ್ಯವಸ್ಥೆ"
            ),
        },
        "mr": {
            "subject": "{student_name} साठी साप्ताहिक उपस्थिती सारांश",
            "message": (
                "प्रिय {parent_name},\n\n"
                "{student_name} (नोंदणी: {register_number}) चा "
                "साप्ताहिक उपस्थिती सारांश:\n\n"
                "📅 आठवडा: {week_start} ते {week_end}\n"
                "✅ उपस्थित: {present} वर्ग\n"
                "❌ अनुपस्थित: {absent} वर्ग\n"
                "📊 साप्ताहिक उपस्थिती: {percentage}%\n\n"
                "📈 एकूण उपस्थिती: {overall_percentage}%\n"
                "🎯 आवश्यक: {required}%\n\n"
                "नियमित उपस्थितीसाठी प्रोत्साहित करा!\n\n"
                "सस्नेह,\n"
                "उपस्थिती व्यवस्थापन प्रणाली"
            ),
        },
        "bn": {
            "subject": "{student_name} এর জন্য সাপ্তাহিক উপস্থিতি সারসংক্ষেপ",
            "message": (
                "প্রিয় {parent_name},\n\n"
                "{student_name} (নিবন্ধন: {register_number}) এর "
                "সাপ্তাহিক উপস্থিতি সারসংক্ষেপ:\n\n"
                "📅 সপ্তাহ: {week_start} থেকে {week_end}\n"
                "✅ উপস্থিত: {present} ক্লাস\n"
                "❌ অনুপস্থিত: {absent} ক্লাস\n"
                "📊 সাপ্তাহিক উপস্থিতি: {percentage}%\n\n"
                "📈 মোট উপস্থিতি: {overall_percentage}%\n"
                "🎯 প্রয়োজন: {required}%\n\n"
                "নিয়মিত উপস্থিতি উৎসাহিত করুন!\n\n"
                "শুভেচ্ছান্তে,\n"
                "উপস্থিতি ব্যবস্থাপনা সিস্টেম"
            ),
        },
        "gu": {
            "subject": "{student_name} માટે સાપ્તાહિક હાજરી સારાંશ",
            "message": (
                "પ્રિય {parent_name},\n\n"
                "{student_name} (નોંધણી: {register_number}) નો "
                "સાપ્તાહિક હાજરી સારાંશ:\n\n"
                "📅 અઠવાડિયું: {week_start} થી {week_end}\n"
                "✅ હાજર: {present} વર્ગો\n"
                "❌ ગેરહાજર: {absent} વર્ગો\n"
                "📊 સાપ્તાહિક હાજરી: {percentage}%\n\n"
                "📈 એકંદર હાજરી: {overall_percentage}%\n"
                "🎯 જરૂરી: {required}%\n\n"
                "નિયમિત હાજરીને પ્રોત્સાહિત કરો!\n\n"
                "સાદર,\n"
                "હાજરી વ્યવસ્થાપન સિસ્ટમ"
            ),
        },
        "pa": {
            "subject": "{student_name} ਲਈ ਹਫ਼ਤਾਵਾਰੀ ਹਾਜ਼ਰੀ ਸਾਰ",
            "message": (
                "ਪਿਆਰੇ {parent_name},\n\n"
                "{student_name} (ਰਜਿਸਟਰ: {register_number}) ਦਾ "
                "ਹਫ਼ਤਾਵਾਰੀ ਹਾਜ਼ਰੀ ਸਾਰ:\n\n"
                "📅 ਹਫ਼ਤਾ: {week_start} ਤੋਂ {week_end}\n"
                "✅ ਹਾਜ਼ਰ: {present} ਕਲਾਸਾਂ\n"
                "❌ ਗੈਰਹਾਜ਼ਰ: {absent} ਕਲਾਸਾਂ\n"
                "📊 ਹਫ਼ਤਾਵਾਰੀ ਹਾਜ਼ਰੀ: {percentage}%\n\n"
                "📈 ਕੁੱਲ ਹਾਜ਼ਰੀ: {overall_percentage}%\n"
                "🎯 ਲੋੜੀਂਦੀ: {required}%\n\n"
                "ਨਿਯਮਿਤ ਹਾਜ਼ਰੀ ਲਈ ਉਤਸ਼ਾਹਿਤ ਕਰੋ!\n\n"
                "ਸਤਿਕਾਰ ਸਹਿਤ,\n"
                "ਹਾਜ਼ਰੀ ਪ੍ਰਬੰਧਨ ਸਿਸਟਮ"
            ),
        },
    },
}


def get_translation(key, language):
    """
    Get translated subject/message for a given key and language.
    Falls back to English if translation is missing.
    """
    messages = TRANSLATIONS.get(key, {})
    return messages.get(language) or messages.get("en") or {
        "subject": "Notification",
        "message": "You have a new notification.",
    }