import os
import sys

os.environ['KIVY_LOG_LEVEL'] = 'debug'

from kivy.config import Config
Config.set('kivy', 'window', 'sdl2')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder


def resource_path(relative_path):
    """Get absolute path to resource — works for dev and PyInstaller bundles."""
    base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.abspath('.')
    return os.path.join(base_path, relative_path)


Builder.load_file(resource_path('main.kv'))


class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_kv_post(self, base=None):
        from admin.admin import AdminWindow
        from signin.signin import SigninWindow
        from signup.signup import SignupWindow
        from till_operator.till_operator import OperationWindow

        self._signin  = SigninWindow()
        self._signup  = SignupWindow()

        try:
            self._admin    = AdminWindow()
            self._operator = OperationWindow()
        except Exception as e:
            self._show_db_error(str(e))
            return

        self.ids.scrn_si.add_widget(self._signin)
        self.ids.scrn_signup.add_widget(self._signup)
        self.ids.scrn_admin.add_widget(self._admin)
        self.ids.scrn_op.add_widget(self._operator)

    def _show_db_error(self, message):
        from kivy.uix.label import Label
        from kivy.uix.popup import Popup
       
        self.ids.scrn_si.add_widget(self._signin)
        self.ids.scrn_signup.add_widget(self._signup)
        Popup(
            title="Database Connection Error",
            content=Label(
                text=(
                    "[b][color=#FF0000]Could not connect to MongoDB.[/color][/b]\n\n"
                    "Make sure MongoDB is running on this machine.\n\n"
                    f"Detail: {message}"
                ),
                markup=True,
                halign='center',
                text_size=(420, None),
            ),
            size_hint=(None, None),
            size=(500, 320),
            auto_dismiss=True,
        ).open()


class POSApp(App):
    def build(self):
        self.icon = resource_path('guru.ico')
        return MainWindow()


if __name__ == '__main__':
    POSApp().run()