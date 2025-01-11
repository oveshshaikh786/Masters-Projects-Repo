from flask import Flask, request, render_template, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
import time
from apriori_2860166 import apriori, load_transactions, get_maximal_frequent_itemsets

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  #Ensuring this folder exists
app.config['ALLOWED_EXTENSIONS'] = {'csv'}  #It will only allow CSV files
app.secret_key = 'your_secret_key'  #It is required for session management

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                min_support = int(request.form['min_support'])
                transactions = load_transactions(filepath)  #Loading transactions from the CSV files

                #Start timing
                start_time = time.time()

                #Running the Apriori algorithm
                frequent_itemsets = apriori(transactions, min_support)
                maximal_itemsets = get_maximal_frequent_itemsets(frequent_itemsets)

                #End timing
                end_time = time.time()
                elapsed_time = end_time - start_time

                #Sorting itemsets by length (ascending order)
                sorted_itemsets = sorted(maximal_itemsets, key=len)

                #formatting itemsets correctly
                formatted_itemsets = ["{" + ", ".join(map(str, filter(None, itemset))) + "}" for itemset in sorted_itemsets]

                #Performs Join itemsets with spaces here
                formatted_output = "{ " + " ".join(formatted_itemsets) + " }"

                #Adding to the session to render in the template
                session['output'] = formatted_output
                session['total_itemsets'] = len(maximal_itemsets)
                session['elapsed_time'] = elapsed_time
                session['input_file'] = filename
                session['min_support'] = min_support


                return redirect(url_for('output'))
            except Exception as e:
                return f"Error processing the file: {str(e)}", 500
        else:
            return "Invalid file format. Please upload a CSV file.", 400

    return render_template("index.html")


@app.route("/output")
def output():
    output = session.pop('output', None)
    total_itemsets = session.pop('total_itemsets', None)
    elapsed_time = session.pop('elapsed_time', None)
    input_file = session.pop('input_file', None)
    min_support = session.pop('min_support', None)

    if output is None:
        return redirect(url_for('index'))  #After refresh, it will redirect back to the input form if no session data

    return render_template("output.html",
                           output=output,
                           total_itemsets=total_itemsets,
                           elapsed_time=elapsed_time,
                           input_file=input_file,
                           min_support=min_support)


if __name__ == "__main__":
    app.run(debug=True)
