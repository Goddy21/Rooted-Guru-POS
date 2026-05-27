import json
import os
import sys

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock


def resource_path(relative_path):
    base = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath('.')
    return os.path.join(base, relative_path)


CONFIG_FILE = resource_path("printer_config.json")


class PrinterConfigForm(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        Clock.schedule_once(self.load_values, 0)

    def load_values(self, *args):
        if not hasattr(self.ids, 'vendor_id'):
            Clock.schedule_once(self.load_values, 0.1)
            return
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        except:
            config = {}

        self.ids.vendor_id.text = config.get("vendor_id", "")
        self.ids.product_id.text = config.get("product_id", "")
        self.ids.encoding.text = config.get("encoding", "")
        self.ids.timeout.text = str(config.get("timeout", ""))
        self.ids.interface.text = str(config.get("interface", ""))

    def save_config(self):
        config = {
            "type": "usb",
            "vendor_id": self.ids.vendor_id.text.strip(),
            "product_id": self.ids.product_id.text.strip(),
        }
        if self.ids.interface.text.strip().isdigit():
            config["interface"] = int(self.ids.interface.text.strip())
        if self.ids.timeout.text.strip().isdigit():
            config["timeout"] = int(self.ids.timeout.text.strip())
        if self.ids.encoding.text.strip():
            config["encoding"] = self.ids.encoding.text.strip()

        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
            self.show_popup("Success", "Configuration saved.")
        except Exception as e:
            self.show_popup("Error", str(e))

    def show_popup(self, title, message):
        popup = Popup(
            title=title,
            content=Label(text=message, halign='center', valign='middle',
                          text_size=(280, None)),
            size_hint=(None, None), size=(300, 150), auto_dismiss=True
        )
        popup.open()