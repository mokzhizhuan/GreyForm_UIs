from PyQt5.QtWidgets import QWidget, QLabel, QPushButton

class SettingThemeChange(object):
    def __init__(self, config, widget):
        self.config = config
        self.widget = widget
        self.apply_styles()

    def apply_styles(self):
        # Applying main background color
        if self.config['maincolor'] == "Gray":
            self.widget.setStyleSheet("")
        elif self.config['maincolor'] == "Black":
            self.widget.setStyleSheet(f"background-color: {self.config['maincolor']};")
        else:
            main_bg_color = self.config['maincolor'] if self.config['maincolor'] != "Other Color" else self.config['themecolor']
            self.widget.setStyleSheet(f"background-color: {main_bg_color};")
        
        # Applying styles for labels within the widget
        text_color = self.config['maincolortext'] if self.config['maincolortext'] != "Other Color" else self.config['text_labelothercolor']
        self.apply_widget_style(QLabel, f"color: {text_color};")
        
        # Applying styles for buttons within the widget
        button_style = ""
        button_bg_color = self.config['buttoncolor'] if self.config['buttoncolor'] != "Other Color" else self.config['buttonthemeothercolor']
        button_text_color = self.config['buttontextcolor'] if self.config['buttontextcolor'] != "Other Color" else self.config['buttontextothercolor']
        
        if self.config['buttoncolor'] not in ["Gray", ""]:
            button_style += f"background-color: {button_bg_color};"
        if self.config['buttontextcolor'] not in ["Gray", ""]:
            button_style += f"color: {button_text_color};"
        
        self.apply_widget_style(QPushButton, button_style)

    def apply_widget_style(self, widget_type, style):
        for widget in self.widget.findChildren(widget_type):
            widget.setStyleSheet(style)