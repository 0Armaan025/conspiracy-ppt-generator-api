from flask import Flask, jsonify
import anthropic
import os
from dotenv import load_dotenv
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches, Pt
import logging
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
    text = text.replace('*', ' ')
    return text

bullets = []
text_content = None

def get_slide_content(slide_number, theory):
    global bullets
    global text_content

    preset = slides_preset[slide_number]

    if preset == 'title':
        title = call_gemini(f'Create an amazing title for the presentation about the theory: {theory}')
        intro_paragraph = call_gemini(f'Write a short 40-word introduction about the theory: {theory}. Use easy English, include some real evidence and some false made-up evidence, just for entertainment.')
        return title, intro_paragraph
    elif preset == 'bullets':
        bullets_title = call_gemini(f'Create an amazing title for the presentation slide, the slide will contain bullets, so create a title for the bullets, theory title is {theory}')
        bullets = []
        for i in range(10):
            bullet = call_gemini(f'Create a bullet point to prove this theory right in a fun way of course, anything can happen ;) , theory: {theory}. Use easy English, include some real evidence and some false made-up evidence, just for entertainment.')
            bullets.append(bullet.replace('-', ' '))
        return bullets_title, bullets
    elif preset == 'text':
        text_content = call_gemini(f'Write a paragraph for the paragraph slide on the theory: {theory}. Use easy English, include some real evidence and some false made-up evidence, just for entertainment.')
        return None, text_content
    elif preset == 'chart':
        return 'Chart Title', None
    elif preset == 'thanks':
        return 'Thank You!', None
    return None, None

def get_theory():
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("You are a conspiracy scientist who writes about conspiracies just for fun, and not in a serious way for kids books. Please suggest a conspiracy theory idea for a movie, only one string. Use easy English and ensure it is in English only.")
        text = response.text
        text = text.replace('*', ' ')
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
    theory = get_theory()
    prs = Presentation()

    for i, preset in enumerate(slides_preset):
        slide_layout = prs.slide_layouts[1] if preset != 'title' else prs.slide_layouts[0]
        slide = prs.slides.add_slide(slide_layout)
        
        title, content = get_slide_content(i, theory)

        if preset == 'title':
            slide.shapes.title.text = title
            text_frame = slide.shapes.placeholders[1].text_frame
            text_frame.text = content
            text_frame.paragraphs[0].font.size = Pt(16)
        elif preset == 'bullets':
            slide.shapes.title.text = title
            left_text_frame = slide.shapes.placeholders[1].text_frame
            left_bullets = content[:5]
            right_bullets = content[5:]
            for bullet in left_bullets:
                p = left_text_frame.add_paragraph()
                p.text = bullet
                p.font.size = Pt(14)
            # Add a new textbox for the right bullets
            left = Inches(5.5)
            top = Inches(1.5)
            width = Inches(4)
            height = Inches(4.5)
            textbox = slide.shapes.add_textbox(left, top, width, height)
            right_text_frame = textbox.text_frame
            for bullet in right_bullets:
                p = right_text_frame.add_paragraph()
                p.text = bullet
                p.font.size = Pt(14)
        elif preset == 'text':
            slide.shapes.title.text = "Details"
            text_frame = slide.shapes.placeholders[1].text_frame
            text_frame.text = content
            for paragraph in text_frame.paragraphs:
                paragraph.font.size = Pt(18)
        elif preset == 'chart':
            chart_data = CategoryChartData()
            chart_data.categories = ['Category 1', 'Category 2', 'Category 3']
            chart_data.add_series('Series 1', (19.2, 21.4, 16.7))
            chart_data.add_series('Series 2', (22.3, 28.6, 15.2))
            x, y, cx, cy = Inches(2), Inches(2), Inches(6), Inches(4.5)
            chart = slide.shapes.add_chart(
                XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
            ).chart
        elif preset == 'thanks':
            slide.shapes.title.text = title
            left = Inches(2)
            top = Inches(3)
            width = Inches(6)
            height = Inches(1.5)
            textbox = slide.shapes.add_textbox(left, top, width, height)
            text_frame = textbox.text_frame
            p = text_frame.add_paragraph()
            p.text = "Thank You!"
            p.font.size = Pt(32)
            p.font.bold = True
            p.alignment = PP_ALIGN.CENTER

    prs.save('generated_presentation.pptx')

    return jsonify({'message': 'Presentation generated and saved to local storage as generated_presentation.pptx'})

if __name__ == '__main__':
    app.run(debug=True)
