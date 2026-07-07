from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import ColorProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

from database.db import get_user_by_email, get_pharmacy_by_seller, get_profile_by_user
from Utils import session

Builder.load_file('kv/login.kv')

class HoverLoginLoginButton(Button):
    bg_color = ColorProperty([0.83, 0.69, 0.22, 1])
    txt_color = ColorProperty([0.05, 0.44, 0.29, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(bg_color=[0.08, 0.63, 0.29, 0.98], txt_color=[1, 1, 1, 1], duration=0.1, t="out_quad").start(self)
        else:
            Animation(bg_color=[0.83, 0.69, 0.22, 1], txt_color=[1, 1, 1, 1], duration=0.1, t="out_quad").start(self)

class HoverLinkButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(color=[0.05, 0.44, 0.29, 1], duration=0.2, t="out_quad").start(self)
        else:
            Animation(color=[0, 0, 0, 1], duration=0.2, t="out_quad").start(self)

class LoginScreen(Screen):

    def on_enter(self):
        self.ids.login_card.opacity = 0
        self.ids.login_card.pos_hint = {"center_x": 0.5, "center_y": 0.4}

        entrance_anim = Animation(
            opacity=1,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            duration=0.9,
            transition="out_cubic"
        )
        entrance_anim.start(self.ids.login_card)

    def on_leave(self):
        self.ids.password_input.text = ""
        self.ids.message_label.text = ""

    def login_user(self, instance=None):
        email = self.ids.email_input.text.strip()
        password = self.ids.password_input.text.strip()
        user = get_user_by_email(email)

        if user is None:
            self.ids.message_label.text = "User not found"
            return

        user_id, db_email, db_password, role = user

        if password != db_password:
            self.ids.message_label.text = "Incorrect password"
            return

        session.current_user = {
            "id": user_id,
            "email": db_email,
            "role": role
        }

        if role == "buyer":
            profile = get_profile_by_user(user_id)
            if profile:
                self.manager.current = "buyer_main"
            else:
                self.manager.current = "create_profile"
        elif role == "seller":
            pharmacy = get_pharmacy_by_seller(user_id)
            if pharmacy:
                self.manager.current = "seller_home"
            else:
                self.manager.current = "create_pharmacy"