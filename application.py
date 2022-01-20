from datetime import datetime, time
from flask import Flask, render_template, send_file, Response, request
import os
import pathlib

application = app = Flask(__name__)

# baseDatos = [["audios/ID.mp3","ID"],["audios/ID1.mp3","ID1"]] # Fecha, URLVideo, URLTexto

UPLOAD_PATH = str(pathlib.Path().resolve())

print(os.listdir("textos/"))
print("hola")


def get_file_date(path_to_file: str):
    """We extract date from file"""
    file_data = os.stat(path_to_file)
    return datetime.fromtimestamp(file_data.st_mtime)

@app.route("/")
def hello_world():
    
    baseDatos = [[f'audios/{i}', i.split('.').pop(0)] for i in os.listdir('audios/')]
    return render_template("speechRview.html", len = len(baseDatos), variables = baseDatos, get_file_date = get_file_date)

@app.route("/input")
def input_form():
    # @todo
    return render_template('input_form.html')
#@app.route("/videoView")
#def hello_worlds():
#    return render_template("videoView.html")

@app.route("/audios/<path:filename>", methods=["GET","POST"])
def getAudios(filename):
    try:
        path_to_file = f"audios/{ filename }"
        # We validate that the file exists 
        if not os.path.exists(path_to_file):
            return Response(
                "Not found",
                status = 404
            )
        print(get_file_date(path_to_file))
        return send_file(path_to_file)
    except Exception as e:
        return Response(
            e.__str__(),
            status = 500
        )

@app.route("/textos/<path:filename>", methods=["GET","POST"])
def getTextos(filename):
    return send_file("textos/"+filename)

@app.route('/disparame', methods=["GET","POST"])
def postTexto():
    if request.method == 'POST':        
        if 'texto' not in request.files or 'audio' not in request.files:
            return "Where are the files?", 400

        text_file = request.files.get('texto')
        audio_file = request.files.get('audio')
        
        try:
            text_file.save(os.path.join(UPLOAD_PATH, 'textos',text_file.filename))
            audio_file.save(os.path.join(UPLOAD_PATH, 'audios',audio_file.filename))
            return 'Files uploaded successfully', 200
        except Exception as e:
            print(e)
            return 'There was a problem when uploading the files', 500
        
    return "I don't like GET requests, shot me only POSTs", 400

if __name__ == '__main__':
   
    app.run(debug=False, host='0.0.0.0')