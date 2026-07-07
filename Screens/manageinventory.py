from kivy.animation import Animation
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import ColorProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.factory import Factory

from database.db import get_connection
from Utils import session

Builder.load_file('kv/manageinventory.kv')


class HoverUpdateButton(Button):
    bg_color = ColorProperty([0.45, 0.82, 0.55, 0.82])
    txt_color = ColorProperty([0, 0, 0, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(bg_color=[0.08, 0.63, 0.29, 0.98], txt_color=[1, 1, 1, 1], duration=0.2, t="out_quad").start(self)
        else:
            Animation(bg_color=[0.45, 0.82, 0.55, 0.82], txt_color=[0, 0, 0, 1], duration=0.2, t="out_quad").start(self)


class HoverAddMedicineButton(Button):
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


class HoverManageBackButton(Button):
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


class ManageInventory(Screen):
    master_inventory_list = []

    def on_enter(self):
        self.ids.medicine_name_input.text = ""
        self.ids.medicine_name_input.bind(text=self.filter_inventory_items)
        self.ids.manage_inventory_card.opacity = 0
        self.ids.action_card.opacity = 0
        anim = Animation(opacity=1, duration=0.4, t="out_quad")
        anim.start(self.ids.manage_inventory_card)
        anim.start(self.ids.action_card)

        self.load_inventory_items()

    def load_inventory_items(self):
        active_pharmacy_id = getattr(session, 'current_pharmacy_id', None)
        if not active_pharmacy_id:
            print("Error: No active pharmacy context selected.")
            return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name, price, stock 
            FROM medicines 
            WHERE pharmacy_id = ?
        """, (active_pharmacy_id,))

        self.master_inventory_list = cursor.fetchall()
        conn.close()
        self.render_list(self.master_inventory_list)

    def filter_inventory_items(self, instance, query_text):
        query = query_text.strip().lower()
        if not query:
            self.render_list(self.master_inventory_list)
            return
        filtered_items = [
            (name, price, stock) for name, price, stock in self.master_inventory_list
            if query in name.lower()
        ]
        self.render_list(filtered_items)

    def render_list(self, items_to_display):
        self.ids.list_container.clear_widgets()
        if not items_to_display:
            self.ids.list_container.add_widget(
                Label(text="No medicines found in this branch.", color=(0.2, 0.2, 0.2, 1), size_hint_y=None, height=44)
            )
            return
        for name, price, stock in items_to_display:
            item_row = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, padding=5, spacing=10)
            name_lbl = Label(text=name.capitalize(), color=(0.1, 0.1, 0.1, 1), halign="left", size_hint_x=0.38)
            name_lbl.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
            price_lbl = Label(text=f"₹{price}", color=(0.2, 0.2, 0.2, 1), size_hint_x=0.2)

            if stock == 0:
                stock_lbl = Label(text="OUT OF STOCK", color=(0.8, 0.2, 0.2, 1), bold=True, size_hint_x=0.2)
            elif stock <= 10:
                stock_lbl = Label(text=f"Low: {stock}", color=(0.88, 0.35, 0.41, 0.82), bold=True, size_hint_x=0.2)
            else:
                stock_lbl = Label(text=f"Qty: {stock}", color=(0.2, 0.2, 0.2, 1), size_hint_x=0.2)

            adjust_btn = Factory.HoverUpdateButton(text="Update")
            if stock <= 0:
                adjust_btn.disabled = True
            adjust_btn.bind(
                on_press=lambda instance, m_name=name, m_stock=stock: self.open_adjustment_popup(m_name, m_stock))

            item_row.add_widget(name_lbl)
            item_row.add_widget(price_lbl)
            item_row.add_widget(stock_lbl)
            item_row.add_widget(adjust_btn)
            self.ids.list_container.add_widget(item_row)

    def open_adjustment_popup(self, medicine_name, current_stock):
        popup = Factory.AdjustmentPopup()
        popup.medicine_name = medicine_name
        popup.current_stock = current_stock
        popup.caller_screen = self
        popup.open()

    def execute_stock_reduction(self, medicine_name, current_stock, remove_qty_str, error_label, popup):
        if not remove_qty_str.strip():
            error_label.text = "Only Numeric Values"
            return
        try:
            remove_qty = int(remove_qty_str)
        except ValueError:
            error_label.text = "Must be an integer"
            return
        if remove_qty <= 0:
            error_label.text = "Must be higher than 0"
            return
        if remove_qty > current_stock:
            error_label.text = f"Deduction limit bounds exceeded ({current_stock} max)."
            return
        new_stock = current_stock - remove_qty
        active_pharmacy_id = session.current_pharmacy_id
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE medicines 
                SET stock = ? 
                WHERE name = ? AND pharmacy_id = ?
            """, (new_stock, medicine_name, active_pharmacy_id))
            conn.commit()
            popup.dismiss()
        except Exception as e:
            error_label.text = "Database storage transaction error."
            print(e)
        finally:
            conn.close()
        self.load_inventory_items()

    def go_add_medicine(self, instance=None):
        self.manager.current = "add_medicine"

    def go_back(self, instance=None):
        self.manager.current = "seller_home"