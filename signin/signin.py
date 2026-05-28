import hashlib
import os

from kivy.config import Config
Config.set('kivy', 'window', 'sdl2')

from kivy.lang import Builder

os.environ['KIVY_LOG_LEVEL'] = 'debug'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from pymongo import MongoClient
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.utils import get_color_from_hex
from utils.paths import GURU_JPG
from config import MONGO_URI, MONGO_DB


#Builder.load_file('signin/signin.kv')
kv_path = os.path.join(os.path.dirname(__file__), 'signin.kv')
Builder.load_file(kv_path)

class SigninWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        self.ids.nav_logo.source = GURU_JPG
        self.ids.card_logo.source = GURU_JPG

    def validate_user(self):
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        users = db.users

        user = self.ids.username_field
        pwd = self.ids.pwd_field
        info = self.ids.info

        uname = user.text
        passw = pwd.text

        user.text = ''
        pwd.text = ''

        if uname == '' or passw == '':
            info.text = "[color=#FF0000]Username and/or password required[/color]"
        else:
            user = users.find_one({'user_name': uname})
            if user is None:
                info.text = '[color=#FF0000]Invalid Username and/or password[/color]'
            else:
                passw = hashlib.sha256(passw.encode()).hexdigest()
                if passw == user['password']:
                    des = user['designation'].lower()
                    info.text = ''
                    self.parent.parent.parent.ids.scrn_op.children[0].ids.loggedin_user.text = uname
                    if des == 'administrator'.lower():
                        self.parent.parent.current = 'scrn_admin'
                    else:
                        self.parent.parent.current = 'scrn_op'
                else:
                    info.text = "[color=#FF0000]Invalid username or password[/color]"

    def go_to_signup(self):
        self.parent.parent.current = 'scrn_signup'

    def forgot_password(self):
        layout = BoxLayout(orientation='vertical', spacing=12, padding=20)
        layout.size_hint = (None, None)
        layout.size = (450, 450)

        uname_input = TextInput(
            hint_text="Enter your username",
            multiline=False,
            size_hint_y=None,
            height=40
        )
        new_pwd_input = TextInput(
            hint_text="Enter new password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=40
        )
        confirm_pwd_input = TextInput(
            hint_text="Confirm new password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=40
        )

        message_label = Label(
            text='',
            markup=True,
            color=(1, 0, 0, 1),
            size_hint_y=None,
            height=30,
            font_size='16sp'
        )

        def reset_pwd(instance):
            uname = uname_input.text.strip()
            new_pwd = new_pwd_input.text
            confirm_pwd = confirm_pwd_input.text

            if not uname or not new_pwd or not confirm_pwd:
                message_label.text = "[color=#FF0000]All fields are required[/color]"
                return

            if new_pwd != confirm_pwd:
                message_label.text = "[color=#FF0000]Passwords do not match[/color]"
                return

            client = MongoClient(MONGO_URI)
            db = client[MONGO_DB]
            users = db.users
            user = users.find_one({"user_name": uname})

            if user is None:
                message_label.text = "[color=#FF0000]Username not found[/color]"
            else:
                hashed_pwd = hashlib.sha256(new_pwd.encode()).hexdigest()
                users.update_one({"user_name": uname}, {"$set": {"password": hashed_pwd}})
                message_label.text = "[color=#00AA00]Password reset successfully[/color]"

        reset_btn = Button(
            text="Reset Password",
            size_hint_y=None,
            height=45,
            font_size='16sp',
            background_normal='',
            background_color=get_color_from_hex("#2962FF"),
            color=(1, 1, 1, 1)
        )
        reset_btn.bind(on_release=reset_pwd)

        layout.add_widget(Label(
            text="[b][color=#0D47A1]Reset Your Password[/color][/b]",
            markup=True,
            font_size='20sp',
            size_hint_y=None,
            height=40,
            halign='center'
        ))
        layout.add_widget(uname_input)
        layout.add_widget(new_pwd_input)
        layout.add_widget(confirm_pwd_input)
        layout.add_widget(message_label)
        layout.add_widget(reset_btn)

        popup = Popup(
            title="Password Recovery",
            title_align='center',
            title_color=(0.16, 0.4, 0.64, 1),
            content=layout,
            size_hint=(None, None),
            size=(480, 500),
            auto_dismiss=True
        )
        popup.open()

class SigninApp(App):
    def build(self):
        return SigninWindow()

if __name__ == "__main__":
    sa = SigninApp()
    sa.run()
