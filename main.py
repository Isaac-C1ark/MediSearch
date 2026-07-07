from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from Screens.loginscreen import LoginScreen
from Screens.managepharmacy import ManagePharmaciesScreen
from Screens.sellerhome import SellerHome
from Screens.createpharmacy import CreatePharmacy
from Screens.manageinventory import ManageInventory
from Screens.signup import SignupScreen
from Screens.addmedicine import AddMedicine
from database.db import create_tables
from Screens.createprofile import CreateProfile
from Screens.buyer_main_screen import BuyerMainScreen
from Screens.updatepharmacy import UpdatePharmacyScreen

class PharmacyApp(App):
    def build(self):
        create_tables()
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(SellerHome(name="seller_home"))
        sm.add_widget(CreatePharmacy(name="create_pharmacy"))
        sm.add_widget(ManageInventory(name="manage_inventory"))
        sm.add_widget(AddMedicine(name="add_medicine"))
        sm.add_widget(CreateProfile(name="create_profile"))
        sm.add_widget(BuyerMainScreen(name="buyer_main"))
        sm.add_widget(ManagePharmaciesScreen(name="manage_pharmacies"))
        sm.add_widget(UpdatePharmacyScreen(name="update_pharmacy"))
        return sm

if __name__ == "__main__":
    PharmacyApp().run()