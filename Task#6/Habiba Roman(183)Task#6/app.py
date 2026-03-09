from flask import Flask, render_template, request, redirect, url_for
import cv2
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            # Save original video
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(original_path)

            # Open video
            cap = cv2.VideoCapture(original_path)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)

            # Output processed MP4 video
            mp4_filename = "processed_" + file.filename.split('.')[0] + ".mp4"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], mp4_filename)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            # Background subtraction for object detection
            fgbg = cv2.createBackgroundSubtractorMOG2()

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                fgmask = fgbg.apply(frame)
                _, thresh = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                count = 0
                for cnt in contours:
                    if cv2.contourArea(cnt) > 500:  # minimum object size
                        x, y, w, h = cv2.boundingRect(cnt)
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        count += 1

                # Show object count on frame
                cv2.putText(frame, f'Objects: {count}', (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                out.write(frame)

            cap.release()
            out.release()
            return render_template('index.html', filename=mp4_filename)

    return render_template('index.html', filename=None)


@app.route('/display/<filename>')
def display_video(filename):
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == '__main__':
    app.run(debug=True)