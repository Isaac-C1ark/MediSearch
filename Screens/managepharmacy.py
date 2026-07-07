from kivy.animation import Animation
from kivy.core.window import Window
from kivy.properties import ColorProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.lang import Builder
from Utils import session
from database.db import get_connection

Builder.load_file('kv/managepharmaciesscreen.kv')

class HoverManageRegisterButton(Button):
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


class HoverManageBackButton(Button):
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


class HoverPharmacyButton(Button):
    bg_color = ColorProperty([1, 1, 1, 0.08])
    line_color = ColorProperty([0.83, 0.69, 0.22, 0.3])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(bg_color=[1, 1, 1, 0.30], line_color=[0.83, 0.69, 0.22, 1], duration=0.1, t="out_quad").start(
                self)
        else:
            Animation(bg_color=[1, 1, 1, 0.08], line_color=[0.83, 0.69, 0.22, 0.3], duration=0.1, t="out_quad").start(
                self)


class ManagePharmaciesScreen(Screen):
    active_pharmacy_id = None

    def on_enter(self):
        self.dismiss_action_drawer(immediate=True)
        self.load_owner_pharmacies()

    def show_action_popup(self, pharmacy_id):
        self.active_pharmacy_id = pharmacy_id
        Animation.stop_all(self.ids.action_drawer)
        slide_up = Animation(pos_hint={"center_x": 0.5, "center_y": 0.35}, duration=0.4, t="out_cubic")
        slide_up.start(self.ids.action_drawer)

    def dismiss_action_drawer(self, instance=None, immediate=False):
        Animation.stop_all(self.ids.action_drawer)
        if immediate:
            self.ids.action_drawer.pos_hint = {"center_x": 0.5, "center_y": -0.5}
        else:
            slide_down = Animation(pos_hint={"center_x": 0.5, "center_y": -0.5}, duration=0.3, t="in_quad")
            slide_down.start(self.ids.action_drawer)

    def trigger_inventory(self):
        if self.active_pharmacy_id:
            session.current_pharmacy_id = self.active_pharmacy_id
            self.manager.current = 'manage_inventory'

    def trigger_details(self):
        if self.active_pharmacy_id:
            update_screen = self.manager.get_screen('update_pharmacy')
            update_screen.current_pharmacy_id = self.active_pharmacy_id
            self.manager.current = 'update_pharmacy'

    def load_owner_pharmacies(self):
        container = self.ids.pharmacy_list_container
        container.clear_widgets()
        user_id = session.current_user["id"]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, address, phone FROM pharmacies WHERE seller_id = ?", (user_id,))
        pharmacies = cursor.fetchall()
        conn.close()

        if not pharmacies:
            no_store_lbl = Label(
                text="No branches registered yet.\nClick the button below to get started!",
                halign="center", valign="middle", color=(1, 1, 1, 0.6), size_hint_y=None, height=150
            )
            no_store_lbl.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
            container.add_widget(no_store_lbl)
            return

        for p_id, name, address, phone in pharmacies:
            store_card = HoverPharmacyButton(
                text=f"[b]{name}[/b]\n[size=13][color=b0dfb0]{address}[/color]\n{phone if phone else 'N/A'}[/size]"
            )
            store_card.bind(on_release=lambda instance, idx=p_id: self.show_action_popup(idx))
            container.add_widget(store_card)

    def add_new_location(self):
        self.manager.current = 'create_pharmacy'

    def go_back(self):
        self.manager.current = 'seller_home'