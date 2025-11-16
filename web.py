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
        index_name = data.get('indexName', 'MAP')
        print("Received location_markers: " + str(location_markers))    
        r = valkey.StrictValkey(host='localhost', port=7000, db=0)
        for marker in location_markers:
            lon = marker.get('lon')
            lat = marker.get('lat')
            name = marker.get('name')
            resp = r.execute_command('GEOADD', index_name, lon, lat, name)
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

@app.route('/load_valkey_data', methods=['POST'])
def load_valkey_data():
    import valkey
    try:
        data = request.get_json()
        if not data:
            data = {}
        geo_data_key = data.get('indexName', 'MAP')
        geo_data = []
        print(f"Loading data from GEO index: {geo_data_key}")
        
        # Set up valkey connection
        r = valkey.StrictValkey(host='localhost', port=7000, db=0)
        
        # Check if key exists
        if not r.exists(geo_data_key):
            print(f"GEO index '{geo_data_key}' does not exist")
            return jsonify({"geo_data": []})
        
        # Fetch all members from the sorted set (this gets the names of the locations)
        members = r.zrange(geo_data_key, 0, -1)
        print(f"Fetched {len(members)} members from {geo_data_key}: {members}")
        
        for member in members:
            try:
                # Fetch the position of each member using GEOPOS
                pos = r.geopos(geo_data_key, member)
                print(f"Position for {member}: {pos}")
                if pos and pos[0]:
                    geo_data.append({
                        "name": member.decode("utf-8") if isinstance(member, bytes) else str(member),
                        "lat": pos[0][1],
                        "lon": pos[0][0]
                    })
            except Exception as member_error:
                print(f"Error processing member {member}: {member_error}")
                continue
        
        print(f"Returning {len(geo_data)} geo data points")
        return jsonify({"geo_data": geo_data})
    except Exception as e:
        print(f"Error in load_valkey_data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


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

# Geofence routes
@app.route('/gf_add_points', methods=['POST'])
def gf_add_points():
    import valkey
    try:
        data = request.get_json()
        location_markers = data.get('locationMarkers', [])
        index_name = data.get('indexName', 'gf_index')
        r = valkey.StrictValkey(host='localhost', port=7000, db=0)
        
        for marker in location_markers:
            lon = marker.get('lon')
            lat = marker.get('lat')
            name = marker.get('name')
            r.execute_command('GF.ADD', index_name, lon, lat, name)
            
        return jsonify({"success": True, "count": len(location_markers)})
    except Exception as e:
        print("Error in gf_add_points: " + str(e))
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/gf_add_polygon', methods=['POST'])
def gf_add_polygon():
    import valkey
    try:
        data = request.get_json()
        coordinates = data.get('coordinates', [])
        polygon_name = data.get('polygonName', 'polygon')
        index_name = data.get('indexName', 'gf_index')
        r = valkey.StrictValkey(host='localhost', port=7000, db=0)
        
        # Build GF.PADD command
        cmd = ['GF.PADD', index_name, len(coordinates)]
        for coord in coordinates:
            cmd.extend([coord[0], coord[1]])  # lon, lat
        cmd.append(polygon_name)
        
        r.execute_command(*cmd)
        return jsonify({"success": True})
    except Exception as e:
        print("Error in gf_add_polygon: " + str(e))
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/gf_search', methods=['POST'])
def gf_search():
    import valkey
    try:
        data = request.get_json()
        index_name = data.get('indexName', 'gf_index')
        search_type = data.get('searchType')  # WITHIN, CONTAINS, INTERSECTS
        search_method = data.get('searchMethod')  # FROMPOLY, FROMMEMBERCOORD, FROMPOLYCOORD
        search_params = data.get('searchParams', [])
        
        r = valkey.StrictValkey(host='localhost', port=7000, db=0)
        
        cmd = ['GF.SEARCH', index_name, search_type, search_method] + search_params
        result = r.execute_command(*cmd)
        
        search_results = [item.decode('utf-8') if isinstance(item, bytes) else str(item) for item in result]
        return jsonify({"success": True, "results": search_results})
    except Exception as e:
        print("Error in gf_search: " + str(e))
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/gf_cluster', methods=['POST'])
def gf_cluster():
    import valkey
    try:
        data = request.get_json()
        index_name = data.get('indexName', 'gf_index')
        algorithm = data.get('algorithm')  # GEOHASH or KMEANS
        params = data.get('params', [])
        
        r = valkey.StrictValkey(host='localhost', port=7000, db=0)
        
        cmd = ['GF.CLUSTER', index_name, algorithm] + params
        result = r.execute_command(*cmd)
        
        clusters = []
        for cluster in result:
            clusters.append({
                'id': cluster[0].decode('utf-8') if isinstance(cluster[0], bytes) else str(cluster[0]),
                'count': int(cluster[1]),
                'centroid_lon': float(cluster[2]),
                'centroid_lat': float(cluster[3])
            })
        
        return jsonify({"success": True, "clusters": clusters})
    except Exception as e:
        print("Error in gf_cluster: " + str(e))
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/geo_cluster', methods=['POST'])
def geo_cluster():
    import valkey
    try:
        data = request.get_json()
        index_name = data.get('indexName', 'MAP')
        precision = data.get('precision')
        max_count = data.get('maxCount')
        
        r = valkey.StrictValkey(host='localhost', port=7000, db=0)
        
        cmd = ['GEOCLUSTER', index_name]
        if precision:
            cmd.extend(['PRECISION', str(precision)])
        if max_count:
            cmd.extend(['MAXCOUNT', str(max_count)])
        
        result = r.execute_command(*cmd)
        
        clusters = []
        for cluster in result:
            clusters.append({
                'id': cluster[0].decode('utf-8') if isinstance(cluster[0], bytes) else str(cluster[0]),
                'count': int(cluster[1]),
                'centroid_lon': float(cluster[2]),
                'centroid_lat': float(cluster[3])
            })
        
        return jsonify({"success": True, "clusters": clusters})
    except Exception as e:
        print("Error in geo_cluster: " + str(e))
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/load_geofence_data', methods=['POST'])
def load_geofence_data():
    import valkey
    try:
        data = request.get_json()
        index_name = data.get('indexName', 'gf_index')
        r = valkey.StrictValkey(host='localhost', port=7000, db=0)
        
        # Get all items (points and polygons) within world-spanning polygon
        result = r.execute_command('GF.SEARCH', index_name, 'WITHIN', 'FROMPOLYCOORD', '4',
                                 '-180', '-85', '180', '-85', '180', '85', '-180', '85', 'WITHCOORD')
        
        geo_data = []
        for item in result:
            if isinstance(item, list) and len(item) == 2:
                name = item[0].decode('utf-8') if isinstance(item[0], bytes) else str(item[0])
                coords = item[1]
                if len(coords) == 2:  # Point: [lon, lat]
                    geo_data.append({
                        'name': name,
                        'type': 'point',
                        'lon': float(coords[0]),
                        'lat': float(coords[1])
                    })
                else:  # Polygon: [lon1, lat1, lon2, lat2, ...]
                    coord_pairs = []
                    for i in range(0, len(coords), 2):
                        coord_pairs.append([float(coords[i]), float(coords[i+1])])
                    geo_data.append({
                        'name': name,
                        'type': 'polygon',
                        'coordinates': coord_pairs
                    })
        
        return jsonify({"success": True, "geo_data": geo_data})
    except Exception as e:
        print("Error in load_geofence_data: " + str(e))
        return jsonify({"success": False, "error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)
