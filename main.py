import os
import sys

os.environ['KIVY_LOG_LEVEL'] = 'debug'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from admin.admin import AdminWindow
from signin.signin import SigninWindow
from signup.signup import SignupWindow
from till_operator.till_operator import OperationWindow
from kivy.config import Config
from kivy.lang import Builder


def resource_path(relative_path):
    """Get absolute path to resource — works for dev and PyInstaller bundles."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller extracts to a temp folder (_MEIPASS)
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)

Config.set('kivy', 'window', 'sdl2')
#Builder.load_file("main.kv")
Builder.load_file(resource_path('main.kv')) 


class MainWindow(BoxLayout):
    admin_widget = AdminWindow()
    signin_widget = SigninWindow()
    signup_widget = SignupWindow()
    operator_widget = OperationWindow()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_kv_post(self, base=None):
        self.ids.scrn_si.add_widget(self.signin_widget)
        self.ids.scrn_signup.add_widget(self.signup_widget)
        self.ids.scrn_admin.add_widget(self.admin_widget)
        self.ids.scrn_op.add_widget(self.operator_widget)

class POSApp(App):
    def build(self):
        self.icon = resource_path('guru.jpg')
        return MainWindow()

if __name__ == '__main__':
    POSApp().run()
