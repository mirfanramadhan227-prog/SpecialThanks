from flask import (
    Flask,
    request,
    jsonify
)

from modules.data_loader import load_data
from modules.map_builder import build_map
from modules.upload_manager import import_excel_to_postgres

app = Flask(__name__)

gdf, df = load_data()

m = build_map(
    gdf,
    df
)

@app.route("/")
def home():

    gdf, df = load_data()

    m = build_map(
        gdf,
        df
    )

    return m.get_root().render()

@app.route(
    "/upload_excel",
    methods=["POST"]
)
def upload_excel():

    if "file" not in request.files:

        return jsonify({
            "success": False,
            "message": "No file uploaded"
        })

    file = request.files["file"]

    if file.filename == "":

        return jsonify({
            "success": False,
            "message": "Empty filename"
        })

    temp_file = "temp_upload.xlsx"

    file.save(temp_file)

    try:

        rows = import_excel_to_postgres(
            temp_file
        )

        return jsonify({
            "success": True,
            "rows": rows
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        })

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )