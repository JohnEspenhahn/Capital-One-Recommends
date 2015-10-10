import json
import yelp
import nessie
from flask import Flask, render_template, request, send_from_directory
app = Flask(__name__, static_url_path='')

@app.route("/")
def main():
    return render_template('main.html')

@app.route('/lib/<path:path>')
def send_lib(path):
    return send_from_directory('lib', path)

@app.route("/geocodes", methods=['POST', 'GET'])
def geocodesPost():
    accID = request.form.get('accID')
    if accID is not None:
        return json.dumps(nessie.getGeolocations(accID))
    else:
        return "{error:'Invalid input'}"

@app.route("/yelp", methods=['POST'])
def yelpPost():
    sw_latitude = request.form.get('sw_latitude', type=float)
    sw_longitude = request.form.get('sw_longitude', type=float)
    ne_latitude = request.form.get('ne_latitude', type=float)
    ne_longitude = request.form.get('ne_longitude', type=float)

    if sw_latitude is not None and sw_longitude is not None and ne_latitude is not None and ne_longitude is not None:
        return json.dumps(yelp.search(sw_latitude, sw_longitude, ne_latitude, ne_longitude))

    return "{error:'Invalid input'}"

if __name__ == "__main__":
    app.run()