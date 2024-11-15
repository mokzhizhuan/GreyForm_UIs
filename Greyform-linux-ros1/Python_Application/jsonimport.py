import json


# load json file for window setting
def jsopen(jsonfile):
    try:
        with open(jsonfile, "r") as f:
            data = json.load(f)
            resolution = data["resolution"]
            font = data["font_size"]
            theme = data["theme"]
            texttheme = data["text_label"]
            buttoncolor = data["buttontheme"]
            buttoncolortext = data["buttontext"]
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
        texttheme,
        buttoncolor,
        buttoncolortext,
        password,
        selected_time_zone,
        width,
        height,
    )
