import pandas as pd
import hashlib
import json
import math
import matplotlib.pyplot as plt

# Load JSON data
with open('./DataEngineeringQ2.json') as file:
    json_data = file.read()

# Parse JSON data
data = json.loads(json_data)

#a
appointments = []
for item in data:
    patient_details = item['patientDetails']
    gender = patient_details.get('gender', None)
    birth_date = patient_details.get('birthDate', None)
    appointment = {
        'appointmentId': item['appointmentId'],
        'phoneNumber': item['phoneNumber'],
        'firstName': patient_details['firstName'],
        'lastName': patient_details['lastName'],
        'gender': gender if gender in ['M', 'F'] else None,
        'DOB': birth_date,
        'medicines': item['consultationData']['medicines']
    }
    appointments.append(appointment)

df = pd.DataFrame(appointments)

df.rename(columns={"birthDate": "DOB"}, inplace=True)

# b
df["fullName"] = df["firstName"] + " " + df["lastName"]

# c
def is_valid_mobile(number):
    if number is None:
        return False
    number = str(number)
    if number.startswith("+91"):
        number = number[3:]
    elif number.startswith("91"):
        number = number[2:]
    return number.isdigit() and 6000000000 <= int(number) <= 9999999999


df["isValidMobile"] = df["phoneNumber"].apply(is_valid_mobile)


# d
def hash_phone_number(number):
    if number is None or not is_valid_mobile(number):
        return None
    number = str(number)
    if number.startswith("+91"):
        number = number[3:]
    elif number.startswith("91"):
        number = number[2:]
    return hashlib.sha256(number.encode()).hexdigest()

df["phoneNumberHash"] = df["phoneNumber"].apply(hash_phone_number)

# e
def calculate_age(birth_date):
    if birth_date is None:
        return None
    birth_date = pd.to_datetime(birth_date)
    today = pd.Timestamp.now()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age

df["Age"] = df["DOB"].apply(calculate_age)

# f&g 
df["noOfMedicines"] = df["medicines"].apply(lambda x: len(x))
df["noOfActiveMedicines"] = df["medicines"].apply(lambda x: sum(1 for med in x if med["isActive"]))
df["noOfInactiveMedicines"] = df["medicines"].apply(lambda x: sum(1 for med in x if not med["isActive"]))
df["medicineNames"] = df["medicines"].apply(lambda x: ", ".join(med["medicineName"] for med in x if med["isActive"]))

#CSV file
df.to_csv("output.csv", sep="~", index=False)

df = df.astype(object)
df["phoneNumber"] = df["phoneNumber"].astype(str)

# h1
aggregated_data = {
    "Age": df["Age"].mean(),
    "gender": df["gender"].value_counts().to_dict(),
    "validPhoneNumbers": df["isValidMobile"].sum(),
    "appointments": len(df),
    "medicines": df["noOfMedicines"].sum(),
    "activeMedicines": df["noOfActiveMedicines"].sum()
}

with open("aggregated_data.json", "w") as file:
    json.dump(aggregated_data, file, indent=4)


# h2
gender_counts = df["gender"].value_counts(dropna=False)
plt.pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%")
plt.axis("equal")
plt.title("Number of Appointments by Gender")
plt.show()