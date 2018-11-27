# DonationServer

API endpoints

GET /user <br />
POST /user <br />
DELETE /user <br />
GET /user/:username/:password <br />
GET /item <br />
POST /item <br />
DELETE /item <br />
GET /item/name/:name (fuzzy and partial search for names) <br />
GET /item/category/:category <br />
GET /item/location/:location_id (use location_id, not name) <br />
GET /location <br />
POST /location <br />
DELETE /location <br />
 
For the moment, all POST call should be one item at a time, will update soon to allow creating multiple items with one call <br />
Start server by going to the src file in the terminal then execute python server.py <br />
If you don't have python, download the newest version of python 3, but mostly just leave a bug report or request for me to fix <br />
