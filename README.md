# DonationServer

API endpoints

GET /user
POST /user
DELETE /user
GET /user/:username/:password
GET /item
POST /item
DELETE /item
GET /item/name/:name (fuzzy and partial search for names)
GET /item/category/:category
GET /item/location/:location_id (use location_id, not name)
GET /location
POST /location
DELETE /location

For the moment, all POST call should be one item at a time, will update soon to allow creating multiple items with one call
Start server by going to the src file in the terminal then execute python server.py
If you don't have python, download the newest version of python 3, but mostly just leave a bug report or request for me to fix
