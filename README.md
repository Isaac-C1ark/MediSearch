MEDISEARCH

A cross-platform application that can allow users to navigate to the nearest pharmacy that has their required medicine in stock. Created 
using Python(Backend Logic), Kivy(Frontend application interface), SQLite(Local database system). During medical emergencies, waiting hours or days for a medicine delivery isn't an option, seconds matter. However, driving around from store to store looking for a rare or out-of-stock medication wastes critical time.
This application bridges that gap. Instead of guessing, a user simply selects or searches for their required medicine. The app instantly cross-references local pharmacy inventories and plots live markers on a map, showing the user exactly which nearby stores have the medicine on their shelves right now.

FEATURES

1. Interactive Native Mapping - (Kivy_garden.mapview): Full-screen map tracking user location coordinates with reactive custom map markers.
2. OpenRouteService Integration - Accurately draws route paths from the buyer to local pharmacies.
3. Custom Markers - To distinguish between the nearest pharmacies and other pharmacies.

PREREQUISITES

1. Make sure you have python 3.10+ installed
2. Clone the repository
3. Install dependencies such as Kivy, Kivymd, requests
4. Go to openrouteservice and get your API key and paste it in the (config.py) file
5. Run the Application (main.py)
