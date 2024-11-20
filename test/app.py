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

# ---------------------
# Step 1: Personal Questions
# ---------------------
@app.route('/personal-info', methods=['GET', 'POST'])
def personal_info():
    if request.method == 'POST':
        # Validate the form inputs
        errors = {}
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        street_address = request.form.get('street_address', '').strip()
        city = request.form.get('city', '').strip()
        zip_code = request.form.get('zip_code', '').strip()
        age = request.form.get('age', '').strip()
        gender = request.form.get('gender', '').strip()
        ethnicity = request.form.get('ethnicity', '').strip()
        state = request.form.get('state', '').strip()

        # First Name and Last Name: Only alphabets allowed
        if not first_name.isalpha():
            errors['first_name'] = "First name must contain only alphabets."
        if not last_name.isalpha():
            errors['last_name'] = "Last name must contain only alphabets."

        # Street Address: Required field (can contain alphanumeric characters and spaces)
        if not street_address:
            errors['street_address'] = "Street address is required."

        # City: Only alphabets allowed
        if city and not city.replace(' ', '').isalpha():
            errors['city'] = "City name must contain only alphabets."

        # ZIP Code: Must be 5-digit number
        if not zip_code.isdigit() or len(zip_code) != 5:
            errors['zip_code'] = "ZIP code must be a 5-digit number."

        # Age: Must be a positive integer
        if not age.isdigit() or int(age) <= 0:
            errors['age'] = "Age must be a positive number."

        # Gender: Must be one of the provided options
        if gender not in ['Male', 'Female', 'Other']:
            errors['gender'] = "Please select a valid gender."

        # Ethnicity: Must be one of the provided options
        if ethnicity not in ['White', 'Black or African American', 'Hispanic or Latino', 'Asian', 'Other']:
            errors['ethnicity'] = "Please select a valid ethnicity."

        # State: Must be one of the provided state abbreviations
        valid_states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA',
            'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK',
            'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]
        if state not in valid_states:
            errors['state'] = "Please select a valid state."

        # If there are errors, re-render the form with error messages and input data
        if errors:
            return render_template('personal_info.html', errors=errors, form_data=request.form)

        # Store valid inputs in session
        session['first_name'] = first_name
        session['last_name'] = last_name
        session['street_address'] = street_address
        session['city'] = city
        session['zip_code'] = zip_code
        session['age'] = age
        session['gender'] = gender
        session['ethnicity'] = ethnicity
        session['state'] = state

        return redirect(url_for('lifestyle_genetic_questions'))

    return render_template('personal_info.html', errors={}, form_data={})


# ---------------------
# Step 2: Lifestyle and Genetic Questions
# ---------------------
@app.route('/lifestyle-genetic-questions', methods=['GET', 'POST'])
def lifestyle_genetic_questions():
    if request.method == 'POST':
        # Store lifestyle and genetic data in session
        family_history = int(request.form.get('family_history', 0))
        apoe_status = int(request.form.get('apoe_status', 0)) if request.form.get('apoe_status') else 0
        diet = int(request.form.get('diet', 0))
        exercise = int(request.form.get('exercise', 0))
        social_engagement = int(request.form.get('social_engagement', 0))

        # Calculate total risk score
        total_score = family_history + apoe_status + diet + exercise + social_engagement
        session['lifestyle_genetic_score'] = total_score
        session['family_history'] = family_history
        session['apoe_status'] = apoe_status
        session['diet'] = diet
        session['exercise'] = exercise
        session['social_engagement'] = social_engagement
        return redirect(url_for('memory_test'))

    return render_template('lifestyle_genetic_questions.html')

# ---------------------
# Step 3: Cognitive Tests
# ---------------------
def generate_random_words(num_words=5):
    word_list = [
        "apple", "banana", "grape", "orange", "peach", "car", "bike", "house",
        "tree", "book", "table", "chair", "cat", "dog", "fish", "pen", "laptop", "phone"
    ]
    return sample(word_list, num_words)

def generate_digit_sequence(length=5):
    return [randint(0, 9) for _ in range(length)]

@app.route('/memory-test', methods=['GET', 'POST'])
def memory_test():
    if request.method == 'POST':
        # Process user input
        user_words = {word.strip().lower() for word in request.form.get("user_words", "").split(",")}
        correct_words = {word.lower() for word in session.get('correct_words', [])}
        session['memory_score'] = len(correct_words & user_words)
        session['user_words'] = list(user_words)  # Store for result display
        return redirect(url_for('digit_test'))

    # Generate random words for the test
    session['correct_words'] = generate_random_words()
    return render_template("memory_test.html", words=session['correct_words'])


@app.route('/digit-test', methods=['GET', 'POST'])
def digit_test():
    errors = []
    form_data = {}

    if request.method == 'POST':
        # Retrieve and validate user input
        user_digits_raw = request.form.get("user_digits", "").strip()
        form_data['user_digits'] = user_digits_raw  # Preserve input for display in case of errors

        # Check if input is empty
        if not user_digits_raw:
            errors.append("Input cannot be empty. Please enter the digits you remember.")

        # Validate format: digits separated by spaces
        elif not all(num.isdigit() for num in user_digits_raw.split()):
            errors.append("Input must contain only digits separated by spaces.")

        # If there are validation errors, re-render the form with errors
        if errors:
            digits = session.get('digit_sequence', [])  # Ensure digits are available for re-render
            return render_template("digit_test.html", errors=errors, form_data=form_data, digits=digits)

        # Process user input if validation passes
        user_digits = [int(num) for num in user_digits_raw.split()]
        correct_digits = session.get('digit_sequence', [])

        # Calculate the score as the count of correct matches
        score = len([digit for digit in user_digits if digit in correct_digits])

        # Ensure the score does not exceed the total number of correct digits
        score = min(score, len(correct_digits))

        session['digit_score'] = score
        session['user_digits'] = user_digits  # Store for result display
        return redirect(url_for('clock_test'))

    # For GET request, generate random digits for the test
    session['digit_sequence'] = generate_digit_sequence()  # Ensure digits are generated and stored
    return render_template("digit_test.html", digits=session['digit_sequence'], errors=[], form_data={})



@app.route('/clock-test', methods=['GET', 'POST'])
def clock_test():
    errors = []

    if request.method == 'POST':
        # Retrieve hour hand and minute hand input
        hour_hand = request.form.get('hour_hand', '').strip()
        minute_hand = request.form.get('minute_hand', '').strip()

        # Validate hour hand
        if not hour_hand.isdigit() or not (1 <= int(hour_hand) <= 12):
            errors.append("Hour hand must be an integer between 1 and 12.")

        # Validate minute hand
        if not minute_hand.isdigit() or not (1 <= int(minute_hand) <= 12):
            errors.append("Minute hand must be an integer between 1 and 12.")

        # If there are validation errors, render the form with error messages
        if errors:
            target_time = session.get('target_time', {'hour': 10, 'minute': 10})  # Default to 10:10 if not set
            return render_template('clock_test_simple.html', errors=errors, target_time=target_time)

        # If validation passes, process the inputs
        hour_hand = int(hour_hand) % 12  # Normalize the hour hand
        minute_hand = int(minute_hand) % 12  # Normalize the minute hand

        # Redirect to the next step
        return redirect(url_for('shape_memory_test'))

    # For GET request, set the target time and render the clock test form
    target_hour = 10  # Example fixed target hour
    target_minute = 10  # Example fixed target minute
    session['target_time'] = {'hour': target_hour, 'minute': target_minute}

    return render_template('clock_test_simple.html', errors=[], target_time=session['target_time'])


@app.route('/shape-memory-test', methods=['GET', 'POST'])
def shape_memory_test():
    if request.method == 'POST':
        user_selected_shapes = {shape for shape in request.form.getlist('selected_shapes')}
        correct_shapes = set(session.get('correct_shapes', []))

        correct_count = len(correct_shapes & user_selected_shapes)
        total_correct = len(correct_shapes)

        session['shape_memory_score'] = {
            'correct_count': correct_count,
            'total_correct': total_correct,
            'correct_shapes': list(correct_shapes),
            'user_selected_shapes': list(user_selected_shapes)
        }

        return redirect(url_for('result'))

    correct_shapes = sample(SHAPES, 3)
    all_shapes = sample(SHAPES, len(SHAPES))
    session['correct_shapes'] = correct_shapes
    session['all_shapes'] = all_shapes
    return render_template('shape_memory_test.html', correct_shapes=correct_shapes, all_shapes=all_shapes)

# ---------------------
# Step 4: Result Page
# ---------------------

# Function to calculate risk based on incorrect answers

def cognitive_risk(total_questions, correct_answers, thresholds):
    incorrect_answers = total_questions - correct_answers
    if incorrect_answers == 0:  # No incorrect answers
        return 0  # Low risk
    elif incorrect_answers <= thresholds['moderate']:
        return 2  # Moderate risk
    else:
        return 4  # High risk


@app.route('/result')
def result():
    # Retrieve scores
    total_memory_questions = len(session.get('correct_words', []))
    total_digit_questions = len(session.get('digit_sequence', []))
    total_shape_questions = len(session.get('correct_shapes', []))
    memory_score_raw = session.get('memory_score', 0)
    digit_score_raw = session.get('digit_score', 0)
    shape_memory_score = session.get('shape_memory_score', {}).get('correct_count', 0)

    memory_risk = cognitive_risk(total_memory_questions, memory_score_raw, {'moderate': 5})
    digit_risk = cognitive_risk(total_digit_questions, digit_score_raw, {'moderate': 5})
    shape_risk = cognitive_risk(total_shape_questions, shape_memory_score, {'moderate': 5})
    cognitive_total_score = memory_risk + digit_risk + shape_risk

    lifestyle_genetic_score = (
        session.get('family_history', 0) +
        session.get('apoe_status', 0) +
        session.get('diet', 0) +
        session.get('exercise', 0) +
        session.get('social_engagement', 0)
    )

    total_risk_score = lifestyle_genetic_score + cognitive_total_score
    risk_category = "Low Risk" if total_risk_score <= 5 else "Moderate Risk" if total_risk_score <= 10 else "High Risk"

    # Generate a pie chart
    labels = ['Cognitive Tests', 'Lifestyle & Genetics']
    scores = [cognitive_total_score, lifestyle_genetic_score]
    colors = ['#4CAF50', '#FF5722']

    plt.figure(figsize=(6, 6))
    wedges, texts, autotexts = plt.pie(
        scores,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=140,
        textprops={'fontsize': 12}
    )
    
    # Adjust label placement to avoid clipping
    for text in texts:
        text.set_horizontalalignment('center')

    plt.title('Risk Distribution', fontsize=16, pad=20)
    plt.axis('equal')  # Keep the chart circular

    # Save the chart as a base64-encoded image
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches="tight")
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode('utf-8')
    plt.close()

    return render_template(
        "result.html",
        lifestyle_genetic_score=lifestyle_genetic_score,
        memory_score_raw=memory_score_raw,
        digit_score_raw=digit_score_raw,
        shape_memory_score=shape_memory_score,
        memory_risk=memory_risk,
        digit_risk=digit_risk,
        shape_risk=shape_risk,
        cognitive_total_score=cognitive_total_score,
        total_risk_score=total_risk_score,
        risk_category=risk_category,
        chart_url=chart_url
    )


@app.route('/form-website')
def form_website():
    return render_template('form_website.html')


@app.route('/')
def home():
    return render_template('index.html')
@app.route('/about-us')
def about_us():
    return render_template('about.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/research-behind-test')
def research_behind_test():
    return render_template('research.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_of_service.html')



if __name__ == '__main__':
    app.run(debug=True)
