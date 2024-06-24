from flask import Flask, jsonify
import anthropic
import os
from dotenv import load_dotenv
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches
import logging
from IPython.display import Markdown

import google.generativeai as genai



load_dotenv()

app = Flask(__name__)

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
gemini_api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_api_key)

slides_preset = ['title', 'bullets', 'text', 'chart', 'text', 'thanks']


logging.basicConfig(level=logging.DEBUG)


def call_gemini(prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    text = response.text
    text = text.replace('*',' ')
    return text




def get_slide_content(slide_number, theory):
    preset = slides_preset[slide_number]

    
        


def get_theory():
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("You are a conspiracy scientist who writes about conspiracies just for fun, and not in a serious way for kids books, Please suggest a conspiracy theory idea for a movie, only one string.")
        # response = client.messages.create(
        #     model="claude-3-opus-20240229",
        #     max_tokens=1000,
        #     temperature=0,
        #     system="You are a conspiracy scientist who writes about conspiracies just for fun, and not in a serious way for kids books.",
        #     messages=[
        #         {
        #             "role": "user",
        #             "content": "Please suggest a conspiracy theory idea for a movie, only one string."
        #         }
        #     ]
        # )
        text = response.text
        text = text.replace('*',' ')
        return text
    except Exception as e:
        logging.error(f"Error getting theory: {e}")
        return "Default Conspiracy Theory"


@app.route('/')
def home():
    theory = get_theory()
    return theory

@app.route('/generate_ppt', methods=['GET'])
def generate_ppt():
    

        prs.save('generated_presentation.pptx')

        return jsonify({'message': 'Presentation generated and saved to local storage as generated_presentation.pptx'})

   

if __name__ == '__main__':
    app.run(debug=True)
