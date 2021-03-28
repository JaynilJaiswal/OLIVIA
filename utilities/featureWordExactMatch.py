feature_db = {
        "time":["time"],

        "date":["date","day"],

        "location":["location"],

        "weather":["weather","climate","sunny","rain","wind"],

        "alarm reminder":["alarm","remember","reminder"],

        "schedule" :["schedule","plan","timetable"],

        "music":["music","play","lay"],

        "find information": ["info","find"],

        "message":["message","chat","whatsapp","ping"],
        
        "email":["email","mail","gmail"],

        "call":["call","phone call"],
        
        "features":["feature list","utilities"],

        "translation":["translat"]
}


def exactMatchingWords(text):
    feature_selected = []
    global feature_db
    
    for k in text.split(" "):
        for item in feature_db.items():
            if any(it == k for it in item[1]):
                feature_selected.append(item[0])

    if len(feature_selected)==0:
        return ["no feature tag found",[]]
    elif len(feature_selected)>1:
        return ["multiple features selected",feature_selected]
    return ["single feature selected", feature_selected]