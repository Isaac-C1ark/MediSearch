from kivy.animation import Animation
from kivy.core.window import Window
from kivy.properties import ListProperty, NumericProperty, ColorProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from database.db import get_connection

Builder.load_file('kv/updatepharmacy.kv')

class HoverUpdateUpdateButton(Button):
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


class HoverUpdateBackButton(Button):
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


class UpdatePharmacyScreen(Screen):
    current_pharmacy_id = NumericProperty(-1)

    def on_current_pharmacy_id(self, instance, value):
        if value != -1:
            self.fetch_and_populate_fields()

    def on_enter(self):
        self.ids.details_card.opacity = 0
        self.ids.details_card.pos_hint = {"center_x": 0.5, "center_y": 0.4}

        if self.current_pharmacy_id != -1:
            self.fetch_and_populate_fields()

        Animation.stop_all(self.ids.details_card)
        card_entry = Animation(
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            opacity=1,
            duration=0.45,
            t="out_cubic"
        )
        card_entry.start(self.ids.details_card)

    def fetch_and_populate_fields(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, address, phone FROM pharmacies WHERE id = ?",
            (self.current_pharmacy_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            name, address, phone = row
            self.ids.name_input.text = str(name) if name else ""
            self.ids.address_input.text = str(address) if address else ""
            self.ids.phone_input.text = str(phone) if phone else ""

    def save_pharmacy_data(self):
        updated_name = self.ids.name_input.text.strip()
        updated_address = self.ids.address_input.text.strip()
        updated_phone = self.ids.phone_input.text.strip()

        if not updated_name or not updated_address:
            print("Error: Name and Address fields cannot be left empty.")
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pharmacies 
                SET name = ?, address = ?, phone = ? 
                WHERE id = ?
            """, (updated_name, updated_address, updated_phone, self.current_pharmacy_id))
            conn.commit()
            conn.close()
            print("Pharmacy info saved successfully!")
            self.go_back()
        except Exception as e:
            print("Database update structural fault error:", e)

    def go_back(self):
        self.current_pharmacy_id = -1
        self.manager.current = 'manage_pharmacies'