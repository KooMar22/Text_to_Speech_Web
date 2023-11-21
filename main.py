# Install required modules
from flask import Flask, render_template, request, send_file, flash
from gtts import gTTS
from pypdf import PdfReader
import io
from decouple import config


app = Flask(__name__)
# Read credentials from ".env" file
app.secret_key = config("SECRET_KEY")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        pdf_file = request.files.get('pdf_file')
        if not pdf_file or not pdf_file.filename.endswith('.pdf'):
            flash("Invalid file or no file uploaded.", "danger")
            return render_template("index.html")

        language = request.form.get('language', 'en')
        text = extract_text_from_pdf(pdf_file)
        if text:
            try:
                audio_bytes = convert_text_to_audio(text, language)
                flash("Conversion completed successfully", "success")
                return send_file(
                    io.BytesIO(audio_bytes),
                    mimetype='audio/mp3',
                    as_attachment=True,
                    download_name='converted_audio.mp3'
                )
            except Exception as e:
                flash(f"Conversion failed: {e}", "danger")
        else:
            flash("Failed to extract text from PDF.", "danger")

    return render_template("index.html")


def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file.stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        print(e)
        flash("An error occurred while reading the PDF file.", "danger")
        return None


def convert_text_to_audio(text, language):
    try:
        tts = gTTS(text=text, lang=language)
        mp3_file = io.BytesIO()
        tts.write_to_fp(mp3_file)
        mp3_file.seek(0)
        return mp3_file.read()
    except Exception as e:
        print(e)
        flash("An error occurred while converting text to audio.", "danger")
        return None


if __name__ == '__main__':
    app.run(debug=True)