from kivy.animation import Animation
from kivy.core.window import Window
from kivy.properties import ColorProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
import requests
from database.db import create_user_profile
from Utils import session
from Utils.Geocoding import geocode_address

Builder.load_file('kv/createprofile.kv')


class HoverCreateSaveButton(Button):
    bg_color = ColorProperty([0.83, 0.69, 0.22, 1])
    txt_color = ColorProperty([0.05, 0.44, 0.29, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(bg_color=[0.08, 0.63, 0.29, 0.98], txt_color=[1, 1, 1, 1], duration=0.1, t="out_quad").start(self)
        else:
            Animation(bg_color=[0.83, 0.69, 0.22, 1], txt_color=[0.05, 0.44, 0.29, 1], duration=0.1,
                      t="out_quad").start(self)


class CreateProfile(Screen):

    def on_enter(self):
        self.ids.create_profile_card.opacity = 0
        self.ids.create_profile_card.pos_hint = {"center_x": 0.5, "center_y": 0.4}

        entrance_anim = Animation(
            opacity=1,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            duration=0.9,
            transition="out_cubic"
        )
        entrance_anim.start(self.ids.create_profile_card)

    def geocode_full_location(self, full_address, pin):
        headers = {'User-Agent': 'PharmacyApp_Kivy_Client_Project'}

        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "street": full_address,
                "postalcode": pin,
                "country": "India",
                "format": "json",
                "limit": 1
            }

            r = requests.get(url, params=params, headers=headers, timeout=5)
            if r.status_code == 200 and r.json():
                return float(r.json()[0]["lat"]), float(r.json()[0]["lon"])

            print("Structured query street match missed. Trying bounded free-form match...")

            fallback_params = {
                "q": full_address,
                "country": "India",
                "format": "json",
                "limit": 1
            }
            r_free = requests.get(url, params=fallback_params, headers=headers, timeout=4)
            if r_free.status_code == 200 and r_free.json():
                return float(r_free.json()[0]["lat"]), float(r_free.json()[0]["lon"])

        except Exception as e:
            print("Nominatim precision engine encountered an issue:", e)

        print("Switching to OpenRouteService API Fallback engine...")
        combined_fallback = f"{full_address}, {pin}, India"
        lat, lon = geocode_address(combined_fallback)
        if lat is not None and lon is not None:
            return lat, lon

        return 26.1445, 91.7362

    def save_profile(self):
        first = self.ids.first_name.text.strip()
        last = self.ids.last_name.text.strip()
        phone = self.ids.phone_number.text.strip()
        address = self.ids.address_input.text.strip()
        pin = self.ids.pin_input.text.strip()

        if not all([first, last, phone, address, pin]):
            self.ids.message_label.color = (1, 0.3, 0.3, 1)
            self.ids.message_label.text = "All fields are required!"
            return

        user_id = session.current_user["id"]
        self.ids.message_label.color = (0.58, 0.77, 0.45, 1)
        self.ids.message_label.text = "Resolving precision address parameters..."

        latitude, longitude = self.geocode_full_location(address, pin)

        try:
            create_user_profile(
                user_id,
                first,
                last,
                phone,
                address,
                pin,
                latitude,
                longitude
            )
            self.manager.current = "buyer_main"
        except Exception as e:
            self.ids.message_label.color = (1, 0.3, 0.3, 1)
            self.ids.message_label.text = "Failed to save profile data."
            print("Profile registration write error:", e)

    def on_leave(self):
        self.ids.first_name.text = ""
        self.ids.last_name.text = ""
        self.ids.phone_number.text = ""
        self.ids.address_input.text = ""
        self.ids.pin_input.text = ""
        self.ids.message_label.text = ""