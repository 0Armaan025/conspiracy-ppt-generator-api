from flask import Flask

app = Flask(__name__)



async def get_conspiracy_theory_idea():


@app.route('/')
def home():
    return 'Hello arcade people'

if __name__ == '__main__':
    app.run(debug=True)