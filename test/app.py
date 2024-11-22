from flask import Flask, render_template, request, redirect, url_for, session
from random import randint, sample
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Sample shapes for the Shape Memory Test
SHAPES = ["circle", "square", "triangle", "star", "heart", "diamond", "hexagon", "octagon"]

@app.route('/')
def welcome():
    return render_template("welcome.html")

@app.route('/about-us')
def about_us():
    return render_template("about.html")

@app.route('/privacy-policy')
def privacy_policy():
    return render_template("privacy_policy.html")

@app.route('/terms-of-service')
def terms_of_service():
    return render_template("terms_of_service.html")

@app.route('/research-behind-test')
def research_behind_test():
    return render_template("research.html")

# ---------------------
# Personal Information Route
# ---------------------
@app.route('/personal-info', methods=['GET', 'POST'])
def personal_info():
    if request.method == 'POST':
        errors = {}
        form_data = request.form.to_dict()

        # First Name validation: Only alphabets, required
        first_name = form_data.get('first_name', '').strip()
        if not first_name:
            errors['first_name'] = "First name is required."
        elif not first_name.replace(' ', '').isalpha():
            errors['first_name'] = "First name must contain only letters."

        # Last Name validation: Only alphabets, required
        last_name = form_data.get('last_name', '').strip()
        if not last_name:
            errors['last_name'] = "Last name is required."
        elif not last_name.replace(' ', '').isalpha():
            errors['last_name'] = "Last name must contain only letters."

        # Street Address: Alphanumeric characters, required
        street_address = form_data.get('street_address', '').strip()
        if not street_address:
            errors['street_address'] = "Street address is required."
        elif not any(char.isalpha() for char in street_address):
            errors['street_address'] = "Street address must contain letters."

        # City validation: Alphabets only, required
        city = form_data.get('city', '').strip()
        if not city:
            errors['city'] = "City is required."
        elif not city.replace(' ', '').isalpha():
            errors['city'] = "City must contain only letters."

        # ZIP Code validation: Must be 5 digits
        zip_code = form_data.get('zip_code', '').strip()
        if not zip_code:
            errors['zip_code'] = "ZIP code is required."
        elif not zip_code.isdigit() or len(zip_code) != 5:
            errors['zip_code'] = "ZIP code must be a 5-digit number."

        # Age validation: Must be positive number
        age = form_data.get('age', '').strip()
        if not age:
            errors['age'] = "Age is required."
        elif not age.isdigit() or int(age) <= 0:
            errors['age'] = "Age must be a positive number."

        # Gender validation
        gender = form_data.get('gender', '').strip()
        if gender not in ['Male', 'Female', 'Other']:
            errors['gender'] = "Please select a valid gender."

        # Ethnicity validation
        ethnicity = form_data.get('ethnicity', '').strip()
        if ethnicity not in ['White', 'Black or African American', 'Hispanic or Latino', 'Asian', 'Other']:
            errors['ethnicity'] = "Please select a valid ethnicity."

        # State validation
        state = form_data.get('state', '').strip()
        valid_states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA',
            'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK',
            'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]
        if state not in valid_states:
            errors['state'] = "Please select a valid state."

        # If there are errors, return form with errors
        if errors:
            return render_template('personal_info.html', errors=errors, form_data=form_data)

        # Save data in session and proceed to next step
        session.update(form_data)
        return redirect(url_for('lifestyle_genetic_questions'))

    # For GET request, return empty form
    return render_template('personal_info.html', errors={}, form_data={})



# ---------------------
# Lifestyle and Genetic Questions Route
# ---------------------
@app.route('/lifestyle-genetic-questions', methods=['GET', 'POST'])
def lifestyle_genetic_questions():
    if request.method == 'POST':
        session['family_history'] = int(request.form.get('family_history', 0))
        session['apoe_status'] = int(request.form.get('apoe_status', 0))
        session['diet'] = int(request.form.get('diet', 0))
        session['exercise'] = int(request.form.get('exercise', 0))
        session['social_engagement'] = int(request.form.get('social_engagement', 0))

        session['lifestyle_genetic_score'] = (
            session['family_history'] +
            session['apoe_status'] +
            session['diet'] +
            session['exercise'] +
            session['social_engagement']
        )
        return redirect(url_for('memory_test'))

    return render_template('lifestyle_genetic_questions.html')


# ---------------------
# Memory Test Route
# ---------------------
@app.route('/memory-test', methods=['GET', 'POST'])
def memory_test():
    if request.method == 'POST':
        user_words = {word.strip().lower() for word in request.form.get("user_words", "").split(",")}
        correct_words = {word.lower() for word in session.get('correct_words', [])}
        correct_count = len(correct_words & user_words)

        memory_score = 5
        incorrect_count = len(correct_words) - correct_count
        memory_score -= incorrect_count
        memory_score = max(memory_score, 0)

        session['memory_score'] = memory_score
        return redirect(url_for('digit_test'))

    session['correct_words'] = sample(["apple", "banana", "car", "tree", "house"], 5)
    return render_template("memory_test.html", words=session['correct_words'])


# ---------------------
# Digit Test Route
# ---------------------
@app.route('/digit-test', methods=['GET', 'POST'])
def digit_test():
    if request.method == 'POST':
        errors = []
        user_digits_raw = request.form.get("user_digits", "").strip()  # Get raw input
        
        # Validate the input for emptiness and format
        if not user_digits_raw:
            errors.append("Input cannot be empty. Please enter the digits you remember.")
        else:
            try:
                # Convert input into a list of integers
                user_digits = [int(num) for num in user_digits_raw.split()]
            except ValueError:
                errors.append("Please enter valid digits separated by spaces.")
        
        # If there are errors, re-render the template with error messages
        if errors:
            return render_template(
                "digit_test.html",
                digits=session.get('digit_sequence', []),
                errors=errors,
                user_input=user_digits_raw
            )

        # Proceed with scoring if there are no errors
        correct_digits = session.get('digit_sequence', [])
        correct_count = len([digit for digit in user_digits if digit in correct_digits])

        digit_score = 5
        incorrect_count = len(correct_digits) - correct_count
        digit_score -= incorrect_count
        digit_score = max(digit_score, 0)

        session['digit_score'] = digit_score
        return redirect(url_for('shape_memory_test'))

    # Generate a new sequence of random digits for the test
    session['digit_sequence'] = [randint(0, 9) for _ in range(5)]
    return render_template(
        "digit_test.html",
        digits=session['digit_sequence'],
        errors=[],
        user_input=""
    )



# ---------------------
# Shape Memory Test Route
# ---------------------
@app.route('/shape-memory-test', methods=['GET', 'POST'])
def shape_memory_test():
    if request.method == 'POST':
        # Get the shapes selected by the user
        user_selected_shapes = {shape for shape in request.form.getlist('selected_shapes')}
        correct_shapes = set(session.get('correct_shapes', []))  # Retrieve correct shapes from the session

        # Calculate the number of correct selections
        correct_count = len(correct_shapes & user_selected_shapes)

        # Store only the correct count in the session for compatibility with result calculations
        session['shape_memory_score'] = correct_count

        # Optional: Store detailed information for debugging or future use
        session['shape_memory_details'] = {
            'correct_count': correct_count,
            'total_correct': len(correct_shapes),
            'correct_shapes': list(correct_shapes),
            'user_selected_shapes': list(user_selected_shapes)
        }

        return redirect(url_for('result'))

    # Generate shapes for the test
    correct_shapes = sample(SHAPES, 3)  # Choose 3 shapes to memorize
    all_shapes = sample(SHAPES, len(SHAPES))  # Randomize all shapes for display

    # Store the correct shapes in the session for use in POST requests
    session['correct_shapes'] = correct_shapes
    session['all_shapes'] = all_shapes

    # Pass data to the template
    return render_template('shape_memory_test.html', correct_shapes=correct_shapes, all_shapes=all_shapes)


def cognitive_risk(total_questions, correct_answers):
    """errors['zip_code']
    Calculates the risk based on the number of correct answers and total questions.
    """
    incorrect_answers = total_questions - correct_answers
    if incorrect_answers == 0:
        return "Low Risk"
    elif incorrect_answers <= 2:
        return "Moderate Risk"
    else:
        return "High Risk"

# ---------------------
# Result Page Route
# ---------------------
@app.route('/result')
def result():
    # Retrieve scores
    total_memory_questions = len(session.get('correct_words', []))
    total_digit_questions = len(session.get('digit_sequence', []))
    total_shape_questions = len(session.get('correct_shapes', []))

    memory_score_raw = session.get('memory_score', 0)
    digit_score_raw = session.get('digit_score', 0)

    shape_memory_score = session.get('shape_memory_score', 0)
    if isinstance(shape_memory_score, int):
        shape_memory_score = {"correct_count": shape_memory_score, "total_correct": total_shape_questions}
    correct_shape_count = shape_memory_score.get("correct_count", 0)

    # Total incorrect scores (for risk calculation)
    memory_risk_score = total_memory_questions - memory_score_raw
    digit_risk_score = total_digit_questions - digit_score_raw
    shape_risk_score = total_shape_questions - correct_shape_count

    total_cognitive_risk_score = memory_risk_score + digit_risk_score + shape_risk_score
    lifestyle_genetic_score = (
        session.get('family_history', 0) +
        session.get('apoe_status', 0) +
        session.get('diet', 0) +
        session.get('exercise', 0) +
        session.get('social_engagement', 0)
    )
    total_risk_score = total_cognitive_risk_score + lifestyle_genetic_score

    # Maximum possible score
    max_total_score = total_memory_questions + total_digit_questions + total_shape_questions + 20  # Lifestyle-genetic max score = 20
    risk_percentage = (total_risk_score * 100) // max_total_score

    # Determine risk category
    risk_category = (
        "Very Low Risk" if risk_percentage <= 20 else
        "Low Risk" if risk_percentage <= 40 else
        "Moderate Risk" if risk_percentage <= 60 else
        "High Risk" if risk_percentage <= 80 else
        "Very High Risk"
    )

    # Pass data to template
    return render_template(
        "result.html",
        total_memory_questions=total_memory_questions,
        total_digit_questions=total_digit_questions,
        total_shape_questions=total_shape_questions,
        memory_score_raw=memory_score_raw,
        digit_score_raw=digit_score_raw,
        shape_memory_score=correct_shape_count,
        memory_risk_score=memory_risk_score,
        digit_risk_score=digit_risk_score,
        shape_risk_score=shape_risk_score,
        total_cognitive_risk_score=total_cognitive_risk_score,
        lifestyle_genetic_score=lifestyle_genetic_score,
        total_risk_score=total_risk_score,
        max_total_score=max_total_score,
        risk_percentage=risk_percentage,
        risk_category=risk_category
    )



if __name__ == '__main__':
    app.run(debug=True)
