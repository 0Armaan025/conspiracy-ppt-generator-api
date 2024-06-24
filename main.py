from flask import Flask, jsonify
import anthropic
import os
from dotenv import load_dotenv
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches
import logging

load_dotenv()

app = Flask(__name__)

client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

slides_preset = ['title', 'bullets', 'text', 'chart', 'text', 'thanks']

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def get_theory():
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0,
            system="You are a conspiracy scientist who writes about conspiracies just for fun, and not in a serious way for kids books.",
            messages=[
                {
                    "role": "user",
                    "content": "Please suggest a conspiracy theory idea for a movie, only one string."
                }
            ]
        )
        return response.content[0].text
    except Exception as e:
        logging.error(f"Error getting theory: {e}")
        return "Default Conspiracy Theory"

def get_slide_content(title, slide_type):
    try:
        prompt = f"Generate content for a slide titled '{title}' with the slide type '{slide_type}'."
        if slide_type == 'title':
            prompt = f"Generate a title slide for the theory '{title}' with a paragraph of introduction."
        elif slide_type == 'bullets':
            prompt = f"Generate bullet points for a slide titled '{title}'."
        elif slide_type == 'text':
            prompt = f"Generate a paragraph of text for a slide titled '{title}'."
        elif slide_type == 'chart':
            prompt = f"Generate chart data for a slide titled '{title}'. Provide categories and values in a comma-separated format."
        elif slide_type == 'thanks':
            prompt = f"Generate a thank you slide for a presentation titled '{title}'."

        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            temperature=0,
            system="You are a conspiracy scientist creating a presentation",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        return response.content[0].text
    except Exception as e:
        logging.error(f"Error getting slide content for {title} ({slide_type}): {e}")
        return "Default Slide Content"

@app.route('/')
def home():
    return 'Hello arcade people'

@app.route('/generate_ppt', methods=['GET'])
def generate_ppt():
    try:
        theory = get_theory()
        slide_contents = [get_slide_content(theory, slide_type) for slide_type in slides_preset]

        prs = Presentation()

        for idx, slide_type in enumerate(slides_preset):
            slide = prs.slides.add_slide(prs.slide_layouts[5])  # Using blank slide layout
            title_shape = slide.shapes.title
            title_shape.text = theory

            if slide_type == 'title':
                content = slide_contents[idx]
                text_frame = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(5.5)).text_frame
                p = text_frame.add_paragraph()
                p.text = content

            elif slide_type == 'bullets':
                content = slide_contents[idx]
                text_frame = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(5.5)).text_frame
                for bullet_point in content.split('\n'):
                    p = text_frame.add_paragraph()
                    p.text = bullet_point

            elif slide_type == 'text':
                content = slide_contents[idx]
                text_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(5.5))
                text_box.text = content

            elif slide_type == 'chart':
                content = slide_contents[idx].split('\n')
                if len(content) >= 2:
                    categories = content[0].split(',')
                    try:
                        values = list(map(float, content[1].split(',')))
                    except ValueError:
                        values = [0.0] * len(categories)  # Default to zero values if parsing fails

                    chart_data = CategoryChartData()
                    chart_data.categories = categories
                    chart_data.add_series('Series 1', values)

                    x, y, cx, cy = Inches(2), Inches(2), Inches(6), Inches(4.5)
                    slide.shapes.add_chart(
                        XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
                    ).chart
                else:
                    text_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(5.5))
                    text_box.text = "Chart data is not available."

            elif slide_type == 'thanks':
                content = slide_contents[idx]
                text_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(5.5))
                text_box.text = content

        prs.save('generated_presentation.pptx')

        return jsonify({'message': 'Presentation generated and saved to local storage as generated_presentation.pptx'})

    except Exception as e:
        logging.error(f"Error generating presentation: {e}")
        return jsonify({'error': 'An error occurred while generating the presentation.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
