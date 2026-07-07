from kivy.animation import Animation
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import NumericProperty, ColorProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from Utils import session
from database.db import get_connection
Builder.load_file('kv/sellerhome.kv')

class HoverLogoutButton(Button):
    bg_color = ColorProperty([0.83, 0.69, 0.22, 1])
    txt_color = ColorProperty([0.05, 0.44, 0.29, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(
                bg_color=[0.88, 0.35, 0.41, 0.82],
                txt_color=[1, 1, 1, 1],
                duration=0.2,
                t="out_quad"
            ).start(self)
        else:
            Animation(
                bg_color=[0.83, 0.69, 0.22, 1],
                txt_color=[1, 1, 1, 1],
                duration=0.2,
                t="out_quad"
            ).start(self)

class HoverCardButton(Button):
    bg_alpha = NumericProperty(0.15)
    border_alpha = NumericProperty(0.3)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(bg_alpha=0.35, border_alpha=0.9, duration=0.2, t="out_quad").start(self)
        else:
            Animation(bg_alpha=0.15, border_alpha=0.3, duration=0.2, t="out_quad").start(self)

class SellerHome(Screen):
    def on_enter(self):
        self.ids.main_container.opacity = 0
        fade_in = Animation(opacity=1, duration=0.5, transition="out_quad")
        fade_in.start(self.ids.main_container)

    def go_manage_pharmacy(self, instance=None):
        self.manager.current = "manage_pharmacies"

    def go_inventory(self, instance=None):
        user_id = session.current_user["id"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM pharmacies WHERE seller_id = ?", (user_id,))
        pharmacies = cursor.fetchall()
        conn.close()

        if len(pharmacies) == 1:
            single_branch_id = pharmacies[0][0]
            session.current_pharmacy_id = single_branch_id
            self.manager.current = "manage_inventory"

        elif len(pharmacies) > 1:
            self.manager.current = "manage_pharmacies"

        else:
            self.manager.current = "create_pharmacy"

    def logout(self, instance=None):
        self.manager.current = "login"