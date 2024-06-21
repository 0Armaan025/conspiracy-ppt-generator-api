from flask import Flask, request, jsonify
import anthropic

client = anthropic.Anthropic()

app = Flask(__name__)


def get_conspiracy_theory_idea(genre):
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        temperature=0,
        system="You are amazing scientist who works on various conspiracy theories and ideas",
        messages=[
            {
                "role": "user",
                "content": f"Please give any 1 random conspiracy theory title"
            }
        ]
    )
    print(message.content[0].text)

@app.route('/')
def home():
    return 'Hello arcade people'

@app.route('/recommend', methods=['GET'])
def recommend():
    genre = request.args.get('genre', 'science fiction')  # Default to 'science fiction' if no genre is provided
    idea = get_conspiracy_theory_idea(genre)
    return jsonify({'recommendation': idea})

if __name__ == '__main__':
    app.run(debug=True)
