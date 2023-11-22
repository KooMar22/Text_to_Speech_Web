# Install required modules
import os
import io
from flask import Flask, render_template, request, flash, send_file
from gtts import gTTS
from pypdf import PdfReader
from decouple import config

app = Flask(__name__)
app.secret_key = config("SECRET_KEY")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        pdf_file = request.files.get('pdf_file')
        if not pdf_file or not pdf_file.filename.endswith('.pdf'):
            flash("Invalid file or no file uploaded.", "danger")
            return render_template("index.html", converting=False)
        else:
            language = request.form.get('language', 'en')
            text = extract_text_from_pdf(pdf_file)
            if text:
                try:
                    audio_bytes = convert_text_to_audio(text, language)
                    mp3_filename = os.path.splitext(
                        pdf_file.filename)[0] + ".mp3"
                    # Return the file immediately after conversion
                    response = send_file(
                        io.BytesIO(audio_bytes),
                        mimetype='audio/mp3',
                        as_attachment=True,
                        download_name=mp3_filename
                    )
                    flash("Conversion completed successfully", "success")
                    return response
                except Exception as e:
                    flash(f"Conversion failed: {e}", "danger")
            else:
                flash("Failed to extract text from PDF.", "danger")
        # In case of failure, return to the form
        return render_template("index.html", converting=False)
    # GET request or initial page load
    return render_template("index.html", converting=False)


def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file.stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        flash("An error occurred while reading the PDF file.", "danger")
        return None


def convert_text_to_audio(text, language):
    try:
        tts = gTTS(text=text, lang=language)
        mp3_io = io.BytesIO()
        tts.write_to_fp(mp3_io)
        mp3_io.seek(0)
        return mp3_io.read()
    except Exception as e:
        flash("An error occurred while converting text to audio.", "danger")
        return None


if __name__ == '__main__':
    app.run(debug=True)