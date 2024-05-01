from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey


RESPONSES = "response"

app = Flask(__name__)
app.config['SECRET_KEY'] = "Key-Value-1"

debug = DebugToolbarExtension(app)

##Default Homepage
@app.route("/")
def default_home_start():
    """Select Survey"""

    return render_template("survey_start.html", survey=survey)

@app.route("/start", methods=["POST"])
def start_survey():
    """Clear Previous responses"""

    ##Session responses reset
    session[RESPONSES] = []

    return redirect("/questions/0")

@app.route("/answer", methods=["POST"])
def answer_logic():
    """Save response, got to next question"""

    #response choice
    choice = request.form['answer']

    #save response to session
    responses = session[RESPONSES]
    responses.append(choice)
    session[RESPONSES] = responses

    #check if the the survey has reached the end.
    if(len(responses) == len(survey.questions)):
        #redirect to survey complete
        return redirect("/completed")
    
    else:
        #redirect to the next question
        return redirect(f"/questions/{len(responses)}")
    

@app.route("/questions/<int:qno>")
def question_logic(qno):
    """Display Current Question"""
    responses = session.get(RESPONSES)

    if(responses == None):
        return redirect("/")

    if(len(responses) == len(survey.questions)):
        return redirect("/completed")

    if(len(responses) != qno):
        flash(f"Invalid Question Number: {qno}")
        return redirect(f"/questions/{len(responses)}")
    
    question = survey.questions[qno]
    return render_template("question.html", question_number=qno, question=question)


@app.route("/completed")
def completed():
    """Survey Completed Logic"""

    return render_template("completed.html")