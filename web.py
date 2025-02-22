from flask import Flask, render_template_string, request, jsonify
import json

app = Flask(__name__)

# Route to render the map with polygon drawing feature
@app.route('/')
def home():
    return render_template_string(open('template.html').read())

# Route to handle the polygon submission
@app.route('/submit_polygon', methods=['POST'])
def submit_polygon():
    try:
        data = request.get_json()  # Get the polygon data from the frontend
        coordinates = data.get('coordinates')

        # Process coordinates (e.g., save to database, calculate area, etc.)
        print("Received coordinates:", coordinates)

        # For demonstration, just return the received coordinates
        return jsonify({"status": "success", "coordinates": coordinates})
    
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/load_valkey_data', methods=['GET'])
def load_valkey_data():
    import valkey
    geo_data_key = "map"
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
        print("error in fetch_geo_data: " + str(e))
    return jsonify({"geo_data": geo_data})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
