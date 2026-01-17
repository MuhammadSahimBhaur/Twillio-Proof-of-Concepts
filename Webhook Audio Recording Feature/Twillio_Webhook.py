from flask import Flask, Response, request
from twilio.twiml.voice_response import Record, VoiceResponse
import os
import json
import requests
import mimetypes


app = Flask(__name__)

@app.route("/", methods=["POST", "GET"])
def forward_call():
    resp = VoiceResponse()

    resp.record(timeout=5, transcribe=True, action="https://a772a20e96ca.ngrok-free.app/action", recordingStatusCallback="https://a772a20e96ca.ngrok-free.app/save", trim="do-not-trim")
    return Response(str(resp), mimetype="text/xml")


@app.route("/action", methods=["POST", "GET"])
def action():
    try:
        print("args",request.args.to_dict(flat=True))
    except:
        print("No arg RecordingUrl")

    return {"status": "saved"}, 200


@app.route("/save", methods=["POST", "GET"])
def save():
    print("saved")

    data = request.form.to_dict()
    print("Received data:", data)

    os.makedirs("saved_requests", exist_ok=True)

    with open("saved_requests/request2.json", "w") as f:
        json.dump(data, f, indent=4)

    RecordingUrl = data["RecordingUrl"]+".mp3"

    print(RecordingUrl)

    wav_file_data = response = requests.get(
    RecordingUrl,
    stream=True,
    auth=("AC4cb87321ece5adc594eb9a3c15de5a99", "531f04d3879d368420fe02c709f44328")
)

    os.makedirs("saved_audio", exist_ok=True)
    with open("saved_audio/audio.mp3", "wb") as f:
        for chunk in wav_file_data.iter_content(chunk_size=8192):
            f.write(chunk)

    return {"status": "saved"}, 200

if __name__ == "__main__":
    app.run(debug=True)