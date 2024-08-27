import io

from flask import Flask, render_template, request, send_file
from fpdf import FPDF
from groq import Groq

app = Flask(__name__)


client = Groq(api_key='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')
latest_response = ""
latest_question = ""

def create_pdf(question, text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', size=14)
    pdf.cell(200, 10, txt=f"Question: {question}", ln=True, align="L")
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    
    pdf_output = io.BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))  
    pdf_output.seek(0)
    
    return pdf_output

@app.route("/", methods=["GET", "POST"])
def index():
    global latest_response, latest_question
    if request.method == "POST":
        user_input = request.form["user_input"]
        latest_question = user_input  
        try:
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": user_input,
                    }
                ],
                model="llama3-8b-8192",
            )
            
            
            latest_response = chat_completion.choices[0].message.content
        except Exception as e:
            latest_response = f"An error occurred: {e}"
    
    return render_template("index.html", question=latest_question, response=latest_response)

@app.route("/download", methods=["GET"])
def download_pdf():
    global latest_response, latest_question
    if not latest_response:
        return "No response available to download."
    
    filename_keyword = latest_question.strip().replace(" ", "_").lower()[:50]
 
    pdf_output = create_pdf(latest_question, latest_response)
    
    filename = f"{filename_keyword}.pdf"
    
    return send_file(
        pdf_output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(debug=True)
