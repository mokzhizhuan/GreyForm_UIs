import json


# load json file for window setting
def jsopen(jsonfile):
    try:
        with open(jsonfile, "r") as f:
            data = json.load(f)
            resolution = data["resolution"]
            font = data["font_size"]
            theme = data["theme"]
            themecolor = data["themeothercolor"]
            texttheme = data["text_label"]
            text_labelothercolor = data["text_labelothercolor"]
            buttoncolor = data["buttontheme"]
            buttonthemeothercolor = data["buttonthemeothercolor"]
            buttoncolortext = data["buttontext"]
            buttontextothercolor = data["buttontextothercolor"]
            password = data["password"]
            selected_time_zone = data["timezone"]
            width, height = map(int, resolution.split(" x "))
    except FileNotFoundError:
        font = 30
        theme = "Gray"
        texttheme = "Black"
        buttoncolor = "White"
        buttoncolortext = "Black"
        password = "pass"
        selected_time_zone = "Asia/Singapore"
        width = 800
        height = 600
        pass
    return (
        font,
        theme,
        themecolor,
        texttheme,
        text_labelothercolor,
        buttoncolor,
        buttonthemeothercolor,
        buttoncolortext,
        buttontextothercolor,
        password,
        selected_time_zone,
        width,
        height,
    )
