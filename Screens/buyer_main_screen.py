import webbrowser
import math
import requests
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.animation import Animation
from kivy.properties import ColorProperty
from kivy.uix.screenmanager import Screen
from kivy_garden.mapview import MapMarkerPopup, MapLayer
from kivy.uix.button import Button
from kivy.graphics import Color, Line
from Utils import session
from database.db import get_connection
from openrouteservice import convert
from config import ORS_API_KEY

class HoverCallButton(Button):
    bg_color = ColorProperty([0.58, 0.77, 0.45, 0.3])
    txt_color = ColorProperty([1,1,1,1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(
                bg_color=[0.08, 0.63, 0.29, 0.75],
                txt_color=[1, 1, 1, 1],
                duration=0.2,
                t="out_quad"
            ).start(self)
        else:
            Animation(
                bg_color=[0.58, 0.77, 0.45, 0.3],
                txt_color=[1, 1, 1, 1],
                duration=0.2,
                t="out_quad"
            ).start(self)

class HoverDismissButton(Button):
    bg_color = ColorProperty([0.58, 0.77, 0.45, 0.3])
    txt_color = ColorProperty([1,1,1,1])

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
                bg_color=[0.58, 0.77, 0.45, 0.3],
                txt_color=[1, 1, 1, 1],
                duration=0.2,
                t="out_quad"
            ).start(self)

class HoverRouteButton(Button):
    bg_color = ColorProperty([0.58, 0.77, 0.45, 0.3])
    txt_color = ColorProperty([1,1,1,1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(
                bg_color=[0.08, 0.63, 0.29, 0.75],
                txt_color=[1, 1, 1, 1],
                duration=0.2,
                t="out_quad"
            ).start(self)
        else:
            Animation(
                bg_color=[0.58, 0.77, 0.45, 0.3],
                txt_color=[1, 1, 1, 1],
                duration=0.2,
                t="out_quad"
            ).start(self)

class HoverSearchButton(Button):
    bg_color = ColorProperty([0.58, 0.77, 0.45, 0.75])
    txt_color = ColorProperty([1,1,1,1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, window, pos):
        if self.get_root_window() and self.collide_point(*self.to_widget(*pos)):
            Animation(
                bg_color=[0.08, 0.63, 0.29, 0.75],
                txt_color=[1, 1, 1, 1],
                duration=0.2,
                t="out_quad"
            ).start(self)
        else:
            Animation(
                bg_color=[0.58, 0.77, 0.45, 0.75],
                txt_color=[1, 1, 1, 1],
                duration=0.2,
                t="out_quad"
            ).start(self)

class RouteLayer(MapLayer):
    def __init__(self, mapview, points, **kwargs):
        super().__init__(**kwargs)
        self.mapview = mapview
        self.points = points
        self.mode = "scatter"

        with self.canvas.before:
            Color(0.05, 0.44, 0.29, 0.9)
            self.line = Line(points=[], width=4)

        self.reposition()

    def reposition(self):
        coords = []
        for lat, lon in self.points:
            x, y = self.mapview.get_window_xy_from(lat, lon, self.mapview.zoom)
            coords.extend([x, y])
        self.line.points = coords


class BuyerMainScreen(Screen):
    _kv_loaded = False
    def __init__(self, **kwargs):
        if not BuyerMainScreen._kv_loaded:
            Builder.load_file('kv/buyermainscreen.kv')
            BuyerMainScreen._kv_loaded = True

        super().__init__(**kwargs)
        self.pharmacy_markers = []
        self.current_open_marker = None
        self.selected_pharmacy = None
        self.route_layer = None
        self.map = None
        self.user_marker = None

    def on_enter(self):
        if not self.map:
            from kivy.clock import Clock
            self.map = self.ids.map_view_widget
            Clock.schedule_once(self._init_map_positions, 0.05)

    def _init_map_positions(self, dt):
        lat, lon = self.get_user_coordinates()
        self.map.center_on(lat, lon)
        self.map.zoom = 15
        self.user_marker = MapMarkerPopup(lat=lat, lon=lon, source="assets/smalluser.png")
        self.map.add_widget(self.user_marker)

    def get_user_coordinates(self):
        try:
            user_id = session.current_user["id"]
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT latitude, longitude FROM user_profiles WHERE user_id=?",
                (user_id,)
            )
            result = cursor.fetchone()
            conn.close()

            if result and result[0] is not None and result[1] is not None:
                return float(result[0]), float(result[1])
        except Exception as e:
            print("DB Coordinate loading error:", e)
        return 26.1445, 91.7362

    def on_text_change(self, instance, value):
        self.ids.suggestion_box.clear_widgets()
        if not value:
            self.ids.suggestion_box.height = 0
            self.ids.suggestion_box.opacity = 0
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT TRIM(LOWER(name)) 
            FROM medicines
            WHERE LOWER(name) LIKE ?
            LIMIT 5
        """, (value + "%",))
        results = cursor.fetchall()
        conn.close()

        if not results:
            self.ids.suggestion_box.height = 0
            self.ids.suggestion_box.opacity = 0
            return

        for row in results:
            btn = Button(
                text=row[0].capitalize(),
                size_hint_y=None,
                height=40,
                background_normal='',
                background_color=(0, 0, 0, 0),
                color=(0.05, 0.44, 0.29, 1),
                bold=True,
                halign="left",
                valign="middle"
            )
            btn.bind(size=lambda s, w: setattr(s, 'text_size', (s.width - 20, None)))
            btn.bind(on_release=self.select_medicine)
            self.ids.suggestion_box.add_widget(btn)

        self.ids.suggestion_box.height = min(len(results) * 40, 200) + 16
        self.ids.suggestion_box.opacity = 1

    def select_medicine(self, instance):
        self.ids.search_input.text = instance.text
        self.ids.suggestion_box.clear_widgets()
        self.ids.suggestion_box.height = 0
        self.ids.suggestion_box.opacity = 0

    def on_search_pressed(self, instance):
        medicine_name = self.ids.search_input.text.strip()
        if not medicine_name:
            return
        self.show_pharmacies_on_map(medicine_name)

    def show_pharmacies_on_map(self, medicine_name):
        self.hide_panel(None)
        if self.route_layer and self.route_layer in self.map._layers:
            self.map.remove_layer(self.route_layer)
            self.route_layer = None

        for marker in self.pharmacy_markers:
            self.map.remove_widget(marker)
        self.pharmacy_markers = []

        user_lat, user_lon = self.get_user_coordinates()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.id, p.name, p.latitude, p.longitude, p.address, p.phone, m.price, m.stock
            FROM medicines m
            JOIN pharmacies p ON m.pharmacy_id = p.id
            WHERE LOWER(m.name) = LOWER(?)
        """, (medicine_name.lower(),))
        results = cursor.fetchall()
        conn.close()

        if not results:
            return

        nearest = None
        nearest_distance = float("inf")

        for pid, name, lat, lon, address, phone, price, stock in results:
            if lat is None or lon is None:
                continue
            distance = self.calculate_distance(user_lat, user_lon, lat, lon)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest = (pid, name, lat, lon)

        for pid, name, lat, lon, address, phone, price, stock in results:
            if lat is None or lon is None:
                continue

            is_nearest = (nearest and pid == nearest[0])
            marker_src = "assets/nearestpharmacy_small.png" if is_nearest else "assets/pharmacy_small.png"

            marker = MapMarkerPopup(lat=lat, lon=lon, source=marker_src)
            marker.pharmacy_name = name
            marker.pharmacy_lat = lat
            marker.pharmacy_lon = lon
            marker.pharmacy_address = address
            marker.pharmacy_phone = phone
            marker.medicine_price = price
            marker.medicine_stock = stock
            marker.bind(on_release=self.on_marker_press)

            self.map.add_widget(marker)
            self.pharmacy_markers.append(marker)

        if nearest:
            self.map.center_on(nearest[2], nearest[3])

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) *
             math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

    def draw_route(self, dest_lat, dest_lon, info_label):
        user_lat, user_lon = self.get_user_coordinates()
        if self.route_layer and self.route_layer in self.map._layers:
            self.map.remove_layer(self.route_layer)
        url = "https://api.openrouteservice.org/v2/directions/driving-car"
        headers = {"Authorization": ORS_API_KEY, "Content-Type": "application/json"}
        body = {"coordinates": [[user_lon, user_lat], [dest_lon, dest_lat]]}
        try:
            r = requests.post(url, json=body, headers=headers, timeout=10)
            if r.status_code != 200:
                return
            data = r.json()
            geometry = data["routes"][0]["geometry"]
            summary = data["routes"][0]["summary"]
            distance_km = round(summary["distance"] / 1000, 2)
            duration_min = round(summary["duration"] / 60, 1)
            info_label.text = f"Distance: {distance_km} km\nETA: {duration_min} min"
            coords = convert.decode_polyline(geometry)
            route_points = [(pt[1], pt[0]) for pt in coords["coordinates"]]

        except Exception as e:
            print("Routing error:", e)
            return

        self.route_layer = RouteLayer(self.map, route_points)
        self.map.add_layer(self.route_layer)

    def on_marker_press(self, marker):
        self.map.center_on(marker.pharmacy_lat, marker.pharmacy_lon)
        user_lat, user_lon = self.get_user_coordinates()
        dist = self.calculate_distance(user_lat, user_lon, marker.pharmacy_lat, marker.pharmacy_lon)
        self.ids.panel_distance.text = f"Distance: {round(dist, 2)} km | ETA: --"
        if self.current_open_marker and self.current_open_marker != marker:
            self.current_open_marker.is_open = False

        if self.route_layer and self.route_layer in self.map._layers:
            self.map.remove_layer(self.route_layer)
        self.route_layer = None
        self.current_open_marker = marker
        self.ids.info_panel.opacity = 1
        Animation(height=200, d=0.25, t="out_quad").start(self.ids.info_panel)
        self.ids.panel_name.text = marker.pharmacy_name
        self.ids.panel_address.text = marker.pharmacy_address
        self.ids.panel_medicine.text = f"Medicine: {self.ids.search_input.text}"
        self.ids.panel_price_stock.text = f"Price: ₹{marker.medicine_price} | Stock: {marker.medicine_stock}"
        self.selected_pharmacy = marker

    def route_from_panel(self, instance):
        if not self.selected_pharmacy:
            return
        self.draw_route(self.selected_pharmacy.pharmacy_lat, self.selected_pharmacy.pharmacy_lon,
                        self.ids.panel_distance)

    def hide_panel(self, instance):
        anim = Animation(height=0, d=0.2, t="out_quad")
        anim.bind(on_complete=lambda *x: setattr(self.ids.info_panel, "opacity", 0))
        anim.start(self.ids.info_panel)
        self.selected_pharmacy = None

    def call_pharmacy(self, instance):
        if not self.selected_pharmacy:
            return
        phone = self.selected_pharmacy.pharmacy_phone
        if phone:
            webbrowser.open(f"tel:{phone}")

    def go_back(self, instance=None):
        self.manager.current = "login"