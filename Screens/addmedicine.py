from kivy.animation import Animation
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ColorProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from database.db import add_medicine
from Utils import session

Builder.load_file('kv/addmedicine.kv')

class HoveraddSaveButton(Button):
    bg_color = ColorProperty([0.83, 0.69, 0.22, 1])
    txt_color = ColorProperty([0.05, 0.44, 0.29, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(
                bg_color=[0.08, 0.63, 0.29, 0.98],
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

class HoveraddBackButton(Button):
    bg_color = ColorProperty([0.83, 0.69, 0.22, 1])
    txt_color = ColorProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(
                bg_color=[0.08, 0.63, 0.29, 0.98],
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

class AddMedicine(Screen):
    def on_enter(self):
        self.ids.add_medicine_card.opacity = 0
        self.ids.add_medicine_card.pos_hint = {"center_x": 0.5, "center_y": 0.4}

        entrance_anim = Animation(
            opacity=1,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            duration=0.9,
            transition="out_cubic"
        )
        entrance_anim.start(self.ids.add_medicine_card)

    def save_medicine(self, instance=None):
        name = self.ids.medicine_name_input.text.strip()
        price_str = self.ids.price.text.strip()
        stock_str = self.ids.stock.text.strip()

        if not name or not price_str or not stock_str:
            self.ids.message_label.text = "All fields are required!"
            return

        try:
            price = float(price_str)
            stock = int(stock_str)
        except ValueError:
            self.ids.message_label.text = "Price and Stock must be numeric numbers"
            return

        pharmacy_id = getattr(session, 'current_pharmacy_id', None)

        if not pharmacy_id:
            self.ids.message_label.text = "Error: Active pharmacy branch not found"
            print("No active pharmacy session context found")
            return

        try:
            add_medicine(pharmacy_id, name, price, stock)
            self.ids.medicine_name_input.text = ""
            self.ids.price.text = ""
            self.ids.stock.text = ""

            self.ids.message_label.color = (0.58, 0.77, 0.45, 1)
            self.ids.message_label.text = "Medicine saved successfully!"

        except Exception as e:
            self.ids.message_label.color = (1, 0.3, 0.3, 1)
            self.ids.message_label.text = "Database write error saving stock"
            print("DB Write Error:", e)

    def go_back(self, instance=None):
        self.manager.current = "manage_inventory"