import re
import pandas as pd
import pyttsx3
from sklearn import preprocessing
from sklearn.tree import DecisionTreeClassifier, _tree
from sklearn.model_selection import train_test_split
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
import csv
import warnings
from flask import Flask, render_template, request

app = Flask(__name__)

# Suppress warnings for DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Global variables for chatbot functionality
severityDictionary = {}
description_list = {}
precautionDictionary = {}
symptoms_dict = {}

# Load training data
training = pd.read_csv('Data/Training.csv')
cols = training.columns[:-1]
x = training[cols]
y = training['prognosis']

# Encode target labels
le = preprocessing.LabelEncoder()
le.fit(y)
y = le.transform(y)

# Initialize decision tree classifier
clf = DecisionTreeClassifier()
clf.fit(x, y)

# Load symptom severity descriptions
def getSeverityDict():
    global severityDictionary
    with open('MasterData/symptom_severity.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) >= 2:
                severityDictionary[row[0]] = int(row[1])

# Load symptom descriptions
def getDescription():
    global description_list
    with open('MasterData/symptom_Description.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) >= 2:
                description_list[row[0]] = row[1]

# Load precautionary measures for symptoms
def getprecautionDict():
    global precautionDictionary
    with open('MasterData/symptom_precaution.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if len(row) >= 5:
                precautionDictionary[row[0]] = [row[1], row[2], row[3], row[4]]

# Initialize all data
def initialize_data():
    getSeverityDict()
    getDescription()
    getprecautionDict()

# Function to predict secondary disease based on symptoms
def sec_predict(symptoms_exp):
    input_vector = np.zeros(len(cols))
    for item in symptoms_exp:
        if item in symptoms_dict:
            input_vector[symptoms_dict[item]] = 1
    return le.inverse_transform(clf.predict([input_vector]))

# Function to read aloud
def read_aloud(nstr):
    engine = pyttsx3.init()
    engine.setProperty('voice', "english+f5")
    engine.setProperty('rate', 130)
    engine.say(nstr)
    engine.runAndWait()
    engine.stop()

# Function to check pattern
def check_pattern(dis_list, inp):
    pred_list = []
    inp = inp.replace(' ', '_')
    patt = f"{inp}"
    regexp = re.compile(patt)
    pred_list = [item for item in dis_list if regexp.search(item)]
    if len(pred_list) > 0:
        return 1, pred_list
    else:
        return 0, []

# Function to calculate condition severity
def calc_condition(exp, days):
    sum_severity = sum(severityDictionary[item] for item in exp)
    if (sum_severity * days) / (len(exp) + 1) > 13:
        return "You should take consultation from a doctor."
    else:
        return "It might not be that bad, but you should take precautions."

# Function to handle user interaction with decision tree
def tree_to_code(disease_input, num_days):
    tree_ = clf.tree_
    feature_name = [cols[i] if i != _tree.TREE_UNDEFINED else "undefined!" for i in tree_.feature]
    chk_dis = ",".join(cols).split(",")
    symptoms_present = []

    def recurse(node, depth):
        indent = "  " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            if name == disease_input:
                val = 1
            else:
                val = 0
            if val <= threshold:
                recurse(tree_.children_left[node], depth + 1)
            else:
                symptoms_present.append(name)
                recurse(tree_.children_right[node], depth + 1)
        else:
            present_disease = le.inverse_transform(tree_.value[node].argmax())
            symptoms_exp = [symptom for symptom in reduced_data.columns[reduced_data.loc[present_disease].values[0].nonzero()] if input(f"Are you experiencing the following symptoms?: {symptom}? : ").lower() == 'yes']

            second_prediction = sec_predict(symptoms_exp)
            return (present_disease, second_prediction, symptoms_exp, symptoms_present)

@app.route('/')
def index():
    initialize_data()
    return render_template('index.html')



@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        symptom = request.form['symptom']
        days = int(request.form['days'])
        disease_input, second_prediction, symptoms_exp, symptoms_present = tree_to_code(symptom, days)
        condition = calc_condition(symptoms_exp, days)

        return render_template('result.html', 
                               disease=disease_input[0], 
                               description=description_list.get(disease_input[0], 'Description not available.'), 
                               second_disease=second_prediction[0], 
                               condition=condition, 
                               precautions=precautionDictionary.get(disease_input[0], []))
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
