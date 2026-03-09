from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # Fetch joke from free API
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        if response.status_code == 200:
            joke_data = response.json()
            setup = joke_data['setup']
            punchline = joke_data['punchline']
        else:
            setup = "Could not fetch joke!"
            punchline = ""
    except Exception as e:
        setup = "Error fetching joke!"
        punchline = str(e)

    return render_template('index.html', setup=setup, punchline=punchline)

if __name__ == '__main__':
    app.run(debug=True)