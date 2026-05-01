from flask import Flask, render_template, request

server = Flask(__name__)

knowledge_base = {
    "emergency": "Emergency Unit is active 24/7 at Gate A. Immediate response available.",
    "doctor": "Doctors available: Cardiology, Neurology, Orthopedics, Pediatrics.",
    "appointment": "Appointments can be booked online or at reception desk.",
    "room": "Room types: General Ward, Private Room, ICU (limited availability).",
    "visiting": "Visiting hours: 5:00 PM to 8:00 PM daily."
}

@server.route("/", methods=["GET", "POST"])
def dashboard():
    response = "Ask me about hospital services"

    if request.method == "POST":
        user_input = request.form["user_text"].lower()

        response = "Sorry, I could not understand your query"

        for key, value in knowledge_base.items():
            if key in user_input:
                response = value
                break

    return render_template("home.html", response_text=response)

if __name__ == "__main__":
    server.run(debug=True)