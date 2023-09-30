from flask import Flask, render_template, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY") 

def generate_question(previous_questions, previous_answers):
    conversation = [
        {"role": "system", "content": "You are a 20 Questions game AI trained to ask insightful and clever questions. Your goal is to guess the person the user is thinking of by asking non-redundant and logical questions.Start by asking broad, general questions to narrow down the field. Focus on characteristics like whether the person is alive, their time period, nationality, and whether they are fictional or not etc etc. Ask broader questions and as the game progresses, get more specific.And always be logical like if the person has said that the person is alive so you should not suggest someone who is dead as your answer."},
        {"role": "user", "content": "The game begins now."}
    ]
    
    for q, a in zip(previous_questions, previous_answers):
        conversation.append({"role": "system", "content": q})
        conversation.append({"role": "user", "content": a})
        
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        temperature=0.7,
        top_p=0.8
    )
    
    next_question = completion.choices[0].message['content']
    return next_question.strip()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    user_response = request.json.get('response', '')
    previous_questions = request.json.get('previous_questions', [])
    previous_answers = request.json.get('previous_answers', [])
    question_count = request.json.get('question_count', 0)
    
    previous_answers.append(user_response)
    
    if question_count >= 20:
        return jsonify({"next_question": "I can't guess it. What was the correct answer?", "game_over": True})
    
    next_question = generate_question(previous_questions, previous_answers)
    previous_questions.append(next_question)
    
    return jsonify({"next_question": next_question, "game_over": False, "question_count": question_count + 1})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)