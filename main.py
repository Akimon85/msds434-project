#Module3

import os

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():

    return jsonify({'output':'Hello World! (I hope this works)'})

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
