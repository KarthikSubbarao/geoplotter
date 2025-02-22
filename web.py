from flask import Flask, render_template_string, request, jsonify
import json

app = Flask(__name__)

# Route to render the map with polygon drawing feature
@app.route('/')
def home():
    return render_template_string(open('template.html').read())

# Route to handle the polygon submission
@app.route('/save_locations', methods=['POST'])
def save_locations():
    import valkey
    count = 0
    try:
        data = request.get_json()  # Get the polygon data from the frontend
        location_markers = data.get('locationMarkers', [])
        print("Received location_markers: " + str(location_markers))    
        r = valkey.StrictValkey(host='localhost', port=7000, db=0)
        key = "MAP"
        for marker in location_markers:
            lon = marker.get('lon')
            lat = marker.get('lat')
            name = marker.get('name')
            resp = r.execute_command('GEOADD', key, lon, lat, name)
            print(resp)        
    except Exception as e:
        print("Error in save_locations: " + str(e))
        return jsonify({"success": False, "error": "Error while adding locations"}), 400
    return jsonify({"success": True})        

# Route to handle the polygon submission
@app.route('/submit_polygon', methods=['POST'])
def submit_polygon():
    import valkey
    # Set up valkey connection
    geo_data = []
    try:
        data = request.get_json()  # Get the polygon data from the frontend
        cmd = str(data.get('cmd'))
        print("Received cmd:", cmd)
        r = valkey.StrictValkey(host='localhost', port=7000, db=0)
        # Fetch all members from the search
        geolist = r.execute_command(cmd)
        for item in geolist:
            geo_data.append({
                "member": item.decode("utf-8"),  # Decode byte string to string
            })
    except Exception as e:
        print("error in submit_polygon: " + str(e))
    print(geo_data)
    return jsonify({"geo_data": geo_data})

@app.route('/load_valkey_data', methods=['GET'])
def load_valkey_data():
    import valkey
    geo_data_key = "MAP"
    geo_data = []
    # Set up valkey connection
    try:
        r = valkey.StrictValkey(host='localhost', port=7000, db=0)
        # Fetch all members from the sorted set (this gets the names of the locations)
        members = r.zrange(geo_data_key, 0, -1)
        print("Fetched members:", members)  # Debugging line to print fetched members
        for member in members:
            # Fetch the position of each member using GEOPOS
            pos = r.geopos(geo_data_key, member)
            print(f"Position for {member}: {pos}")  # Debugging line to print each position
            if pos and pos[0]:
                geo_data.append({
                    "member": member.decode("utf-8"),  # Decode byte string to string
                    "lat": pos[0][1],
                    "lng": pos[0][0]
                })
    except Exception as e:
        print("error in load_valkey_data: " + str(e))
    return jsonify({"geo_data": geo_data})


@app.route('/flush_valkey', methods=['GET'])
def flush_valkey():
    import valkey
    # Set up valkey connection
    try:
        r = valkey.StrictValkey(host='localhost', port=7000, db=0)
        r.execute_command("FLUSHALL")
    except Exception as e:
        print("error in flush_valkey: " + str(e))
        return jsonify({"success": False})
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
