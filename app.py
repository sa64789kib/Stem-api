from flask import Flask, request, send_file
import os, subprocess, uuid, shutil
from zipfile import ZipFile

app = Flask(__name__)

@app.route('/separate', methods=['POST'])
def separate_audio():
    if 'file' not in request.files:
        return 'No file part', 400
    audio = request.files['file']
    if audio.filename == '':
        return 'No selected file', 400

    session_id = str(uuid.uuid4())
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("separated", exist_ok=True)
    os.makedirs("zips", exist_ok=True)

    input_path = f"uploads/{session_id}.mp3"
    audio.save(input_path)

    out_dir = f"separated/{session_id}"
    subprocess.run(["demucs", "-n", "htdemucs", "-o", "separated", input_path], check=True)

    track_name = os.listdir(f"{out_dir}/htdemucs")[0]
    track_folder = f"{out_dir}/htdemucs/{track_name}"

    zip_path = f"zips/{session_id}.zip"
    with ZipFile(zip_path, 'w') as zipf:
        for fname in os.listdir(track_folder):
            zipf.write(f"{track_folder}/{fname}", arcname=fname)

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
