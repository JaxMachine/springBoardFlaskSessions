from flask import Flask, request, render_template, redirect, make_response, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

CURRENT_SURVEY = 'current_sruvey'
RESPONSES = "response"

app = Flask(__name__)
app.config['SECRET_KEY'] = "Key-Value-1"

debug = DebugToolbarExtension(app)

##Default Homepage
@app.route("/")
def default_home_start():
    """Survey select form"""

    return render_template("survey_selection.html", surveys=surveys)

@app.route("/", methods=["POST"])
def pick_survey():
    """Select a Survey"""

    selected_survey = request.form['survey_name']


    if request.cookies.get(f"{selected_survey}_completed"):
        return render_template("already-completed.html")
    
    survey = surveys[selected_survey]
    session[CURRENT_SURVEY] = selected_survey

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
    text = request.form.get("text", "")

    #save response to session
    responses = session[RESPONSES]
    responses.append({"choice":choice, "text": text})
    session[RESPONSES] = responses
    survey_name=session[CURRENT_SURVEY]
    survey = surveys[survey_name]

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
    survey_name=session[CURRENT_SURVEY]
    survey=surveys[survey_name]

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
    selected_survey =session[CURRENT_SURVEY]
    survey = surveys[selected_survey]
    responses = session[RESPONSES]

    html = render_template("completed.html", survey=survey, responses=responses)
    
    #Cookie to save suyrvey status
    response= make_response(html)
    response.set_cookie(f"{selected_survey}_completed", "yes", max_age=30)
    return response