import pandas as pd

# Define the structure for company data
company_data = {
    "name": ["Company A", "Company B"],
    "address": ["1234 Elm Street", "5678 Oak Avenue"],
    "phone": ["123-456-7890", "987-654-3210"],
    "email": ["info@companya.com", "contact@companyb.com"],
    "website": ["www.companya.com", "www.companyb.com"],
    "no. of employees": [150, 250],
    "founded date": ["2000-01-01", "2010-06-15"],
    "industry type": ["Technology", "Healthcare"],
    "contact_name": ["John Doe", "Jane Smith"],
    "contact_email": ["john.doe@companya.com", "jane.smith@companyb.com"],
    "contact_phone": ["111-222-3333", "444-555-6666"],
    "dob": ["1980-05-10", "1985-07-20"],
    "contact_type": ["Primary", "Secondary"]
}

# Convert the dictionary into a DataFrame
df = pd.DataFrame(company_data)

# Convert the 'founded date' and 'dob' columns to datetime
df["founded date"] = pd.to_datetime(df["founded date"])
df["dob"] = pd.to_datetime(df["dob"])

# Save the DataFrame to an Excel file
df.to_excel("company_contact_data.xlsx", index=False)

print("Excel file generated successfully!")
