# import pandas as pd
# import joblib
#
# # Load the saved model pipeline
# model_pipeline = joblib.load(r'C:\Users\cssre\OneDrive\Desktop\insurance claim\insurance\myapp\fraud_detection_model.pkl')
#
# # Example new data for prediction (replace with your actual new data as a dictionary)
# new_data = {
#     'months_as_customer': 134,
#     'age': 29,
#     'policy_number': 687698,
#     'policy_bind_date': 6-9-2000,
#     'policy_state': 'OH',
#     'policy_csl': '100/300',
#     'policy_deductable': 2000,
#     'policy_annual_premium': 1413.14,
#     'umbrella_limit': 5000000,
#     'insured_zip': 430632,
#     'insured_sex': 'FEMALE',
#     'insured_education_level': 'phD',
#     'insured_occupation': 'sales',
#     'insured_hobbies': 'board-games',
#     'insured_relationship': 'own-child',
#     'capital-gains': 35100,
#     'capital-loss': 0,
#     'incident_date': 22-2-2015,
#     'incident_type': 'Multi-Vehicle collision',
#     'collision_type': 'Rear collision',
#     'incident_severity': 'Minor Damage',
#     'authorities_contacted': 'Police',
#     'incident_state': 'NY',
#     'incident_city': 'Columbus',
#     'incident_location': '7121 Francis Lane',
#     'incident_hour_of_the_day': 7,
#     'number_of_vehicles_involved': 3,
#     'property_damage': 'NO',
#     'bodily_injuries': 2,
#     'witnesses': 3,
#     'police_report_available': 'NO',
#     'total_claim_amount': 34650,
#     'injury_claim': 7700,
#     'property_claim': 3850,
#     'vehicle_claim': 23100,
#     'auto_make': 'Dodge',
#     'auto_model': 'RAM',
#     'auto_year': 2007
#     # Add any other columns if missing, matching the training data
# }
#
# # Convert new data to DataFrame (model expects DataFrame input)
# new_df = pd.DataFrame([new_data])
#
# # Make prediction
# prediction = model_pipeline.predict(new_df)
# probability = model_pipeline.predict_proba(new_df)[:, 1]  # Probability of fraud (class 1)
#
# # Output the result
# if prediction[0] == 1:
#     print("Prediction: Fraud Detected")
# else:
#     print("Prediction: No Fraud")
# print("Fraud Probability:", probability[0])



import pandas as pd
import joblib

# Load the saved model pipeline
# model_pipeline = joblib.load(r'C:\Users\cssre\OneDrive\Desktop\insurance claim\insurance\myapp\fraud_detection_model.pkl')
model_pipeline = joblib.load(r'C:\Users\GAYATHRI\Music\insurance\insurance claim\insurance\myapp\fraud_detection_model.pkl')

# Define the features expected by the model (based on the provided example)
features = [
    'months_as_customer', 'age', 'policy_number', 'policy_bind_date', 'policy_state',
    'policy_csl', 'policy_deductable', 'policy_annual_premium', 'umbrella_limit',
    'insured_zip', 'insured_sex', 'insured_education_level', 'insured_occupation',
    'insured_hobbies', 'insured_relationship', 'capital-gains', 'capital-loss',
    'incident_date', 'incident_type', 'collision_type', 'incident_severity',
    'authorities_contacted', 'incident_state', 'incident_city', 'incident_location',
    'incident_hour_of_the_day', 'number_of_vehicles_involved', 'property_damage',
    'bodily_injuries', 'witnesses', 'police_report_available', 'total_claim_amount',
    'injury_claim', 'property_claim', 'vehicle_claim', 'auto_make', 'auto_model',
    'auto_year'
]

# Dictionary to store user input
new_data = {}

# Prompt user to input values for each feature in the terminal
print("Enter the values for the following features:")
for feature in features:
    value = input(f"{feature}: ")
    new_data[feature] = value

# Convert date fields to the correct format (assuming dates are entered as DD-MM-YYYY)
date_cols = ['policy_bind_date', 'incident_date']
for col in date_cols:
    if new_data[col]:
        try:
            # Parse the input date and convert to Excel serial date format
            date_val = pd.to_datetime(new_data[col], format='%d-%m-%Y')
            # Convert to days since Excel epoch (1899-12-30)
            new_data[col] = (date_val - pd.Timestamp('1899-12-30')).days
        except ValueError:
            print(f"Warning: Invalid date format for {col}. Please use DD-MM-YYYY. Setting to None.")
            new_data[col] = None

# Convert numerical fields to appropriate types
numerical_cols = [
    'months_as_customer', 'age', 'policy_number', 'policy_deductable',
    'policy_annual_premium', 'umbrella_limit', 'insured_zip', 'capital-gains',
    'capital-loss', 'incident_hour_of_the_day', 'number_of_vehicles_involved',
    'bodily_injuries', 'witnesses', 'total_claim_amount', 'injury_claim',
    'property_claim', 'vehicle_claim', 'auto_year'
]
for col in numerical_cols:
    try:
        new_data[col] = float(new_data[col]) if new_data[col] else None
    except ValueError:
        print(f"Warning: Invalid numerical value for {col}. Setting to None.")
        new_data[col] = None

# Convert new data to DataFrame (model expects DataFrame input)
new_df = pd.DataFrame([new_data])

# Make prediction
prediction = model_pipeline.predict(new_df)
probability = model_pipeline.predict_proba(new_df)[:, 1]  # Probability of fraud (class 1)

# Output the result
if prediction[0] == 1:
    print("Prediction: Fraud Detected")
else:
    print("Prediction: No Fraud")
print(f"Fraud Probability: {probability[0]:.4f}")