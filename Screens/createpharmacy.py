from kivy.animation import Animation
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ColorProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
import requests

Builder.load_file('kv/createpharmacy.kv')

from database.db import create_pharmacy
from Utils import session
from Utils.Geocoding import geocode_address


class HoverCreateSaveButton(Button):
    bg_color = ColorProperty([0.83, 0.69, 0.22, 1])
    txt_color = ColorProperty([0.05, 0.44, 0.29, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(bg_color=[0.08, 0.63, 0.29, 0.98], txt_color=[1, 1, 1, 1], duration=0.2, t="out_quad").start(self)
        else:
            Animation(bg_color=[0.83, 0.69, 0.22, 1], txt_color=[1, 1, 1, 1], duration=0.2, t="out_quad").start(self)


class HoverCreateBackButton(Button):
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


class CreatePharmacy(Screen):

    def on_enter(self):
        self.ids.create_pharmacy_card.opacity = 0
        self.ids.create_pharmacy_card.pos_hint = {"center_x": 0.5, "center_y": 0.4}

        entrance_anim = Animation(
            opacity=1,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            duration=0.9,
            transition="out_cubic"
        )
        entrance_anim.start(self.ids.create_pharmacy_card)

    def on_leave(self):
        self.ids.pharmacy_name_input.text = ""
        self.ids.pharmacy_address_input.text = ""
        self.ids.pharmacy_phone_input.text = ""
        self.ids.message_label.text = ""

    def geocode_pharmacy_location(self, text_address):
        try:
            url = f"https://nominatim.openstreetmap.org/search?q={text_address},+India&format=json"
            headers = {'User-Agent': 'PharmacyApp_Seller_Client_System'}
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200 and r.json():
                return float(r.json()[0]["lat"]), float(r.json()[0]["lon"])
        except Exception as e:
            print("Nominatim store lookup failed, jumping to primary API utility:", e)
        lat, lon = geocode_address(text_address)
        if lat is not None and lon is not None:
            return lat, lon
        return 26.1445, 91.7362

    def save_pharmacy(self, instance=None):
        name = self.ids.pharmacy_name_input.text.strip()
        address = self.ids.pharmacy_address_input.text.strip()
        phone = self.ids.pharmacy_phone_input.text.strip()
        if not name or not address or not phone:
            self.ids.message_label.color = (0.8, 0.2, 0.2, 1)
            self.ids.message_label.text = "All fields are required"
            return

        self.ids.message_label.color = (0.83, 0.69, 0.22, 1)
        self.ids.message_label.text = "Pinpointing branch coordinates..."
        latitude, longitude = self.geocode_pharmacy_location(address)

        seller_id = session.current_user["id"]

        try:
            create_pharmacy(seller_id, name, address, phone, latitude, longitude)
            self.ids.message_label.color = (0.05, 0.44, 0.29, 1)
            self.ids.message_label.text = "Pharmacy branch registered successfully!"
            self.manager.current = "manage_pharmacies"
        except Exception as e:
            self.ids.message_label.color = (0.8, 0.2, 0.2, 1)
            self.ids.message_label.text = "Database error saving pharmacy branch"
            print("DB Error:", e)

    def go_back(self, instance=None):
        self.manager.current = "manage_pharmacies"