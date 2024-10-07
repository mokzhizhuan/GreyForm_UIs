import json

#load json file for window setting
def jsopen(jsonfile):
    try:
        with open(jsonfile, "r") as f:
            data = json.load(f)
            resolution = data["resolution"]
            font = data["font_size"]
            theme = data["theme"]
            password = data["password"]
            selected_time_zone = data["timezone"]
            width, height = map(int, resolution.split(" x "))
    except FileNotFoundError:
        font = 30
        theme = "Gray"
        password = "pass"
        selected_time_zone = "Asia/Singapore"
        width = 800
        height = 600
        pass
    return font, theme, password, selected_time_zone, width, height
