import re
import pytest
import pandas as pd
import great_expectations as gx
from great_expectations import expectations as gxe

df = pd.read_csv("customer_data.csv")

context = gx.get_context()

data_source = context.data_sources.add_pandas(name="customer_data_source")
print("Data source created: customer_data_source")

data_asset = data_source.add_dataframe_asset(name="customer_data_asset")
print("Data asset created: customer_data_asset")

data_asset.add_batch_definition_whole_dataframe(name="customer_data_batch")
print("Batch definition created: customer_data_batch")

suite = gx.ExpectationSuite(name="customer_data_expectations")
print("Expectation suite created: customer_data_expectations")

context.suites.add(suite)
print("Great Expectations Part 1 setup completed successfully.")

# customer_id must not be null
suite.add_expectation(
    gxe.ExpectColumnValuesToNotBeNull(
        column="customer_id"
    )
)
print("Added expectation: customer_id NOT null")

# customer_id must be unique
suite.add_expectation(
    gxe.ExpectColumnValuesToBeUnique(
        column="customer_id"
    )
)
print("Added expectation: customer_id is unique")

# age must be between 0 and 120
suite.add_expectation(
    gxe.ExpectColumnValuesToBeBetween(
        column="age",
        min_value=0,
        max_value=120
    )
)
print("Added expectation: age between 0 & 120")

# email must match a valid format
suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="email",
        regex=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    )
)
print("Added expectation: email matches valid format")

# salary must be present in at least 95% of rows
suite.add_expectation(
    gxe.ExpectColumnValuesToNotBeNull(
        column="salary",
        mostly=0.95
    )
)
print("Added expectation: salary present in 95 percent of rows")

# country must be one of the allowed values
suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="country",
        value_set=["USA", "Canada", "UK", "Australia"]
    )
)
print("Added expectation: country is one of valid options")

# signup_date must be parseable as a date/datetime
suite.add_expectation(
    gxe.ExpectColumnValuesToBeDateutilParseable(
        column="signup_date"
    )
)
print("Added expectation: signup_date is of datetime type")

# table row count must be between 500 and 1000
suite.add_expectation(
    gxe.ExpectTableRowCountToBeBetween(
        min_value=500,
        max_value=1000
    )
)
print("Added expectation: row count between 500 & 1000")

print("Part 2 completed successfully. Added 8 expectations to customer_data_expectations.")


# Retrieve the data source, asset, and batch definition created earlier
batch_definition = (
    context.data_sources.get("customer_data_source")
    .get_asset("customer_data_asset")
    .get_batch_definition("customer_data_batch")
)

# Create a validation definition
validation_definition = gx.ValidationDefinition(
    name="customer_data_validation",
    data=batch_definition,
    suite=suite
)

# Run validation against the dataframe
validation_result = validation_definition.run(
    batch_parameters={"dataframe": df},
    result_format="COMPLETE"
)

def salary_to_numeric(value):
    if pd.isna(value):
        return pd.NA

    value = str(value)
    value = value.replace("$", "").replace(",", "").strip()

    return pd.to_numeric(value, errors="coerce")


def is_valid_email(email):
    if pd.isna(email):
        return False

    email = str(email).strip()
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return bool(re.match(pattern, email))


def is_clean_phone_format(phone):
    if pd.isna(phone):
        return False

    digits = re.sub(r"\D", "", str(phone))

    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    return len(digits) == 10

issues = {}

# customer_id issues
issues["Missing customer_id values"] = int(df["customer_id"].isna().sum())
issues["Duplicate customer_id values"] = int(df["customer_id"].duplicated().sum())

# age issues
age_numeric = pd.to_numeric(df["age"], errors="coerce")
issues["Missing age values"] = int(df["age"].isna().sum())
issues["Invalid age values outside 0 to 120"] = int(
    ((age_numeric < 0) | (age_numeric > 120)).sum()
)

# email issues
issues["Missing email values"] = int(df["email"].isna().sum())
issues["Invalid email formats"] = int((~df["email"].apply(is_valid_email)).sum())

# salary issues
salary_numeric = df["salary"].apply(salary_to_numeric)
issues["Missing salary values"] = int(df["salary"].isna().sum())
issues["Invalid salary values that cannot be converted to numeric"] = int(
    salary_numeric.isna().sum()
)
issues["Negative salary values"] = int((salary_numeric < 0).sum())

# country issues
valid_countries = ["USA", "Canada", "UK", "Australia"]
issues["Invalid country values"] = int((~df["country"].isin(valid_countries)).sum())

# phone issues
issues["Invalid or uncleanable phone numbers"] = int(
    (~df["phone"].apply(is_clean_phone_format)).sum()
)

# signup_date issues
signup_dates = pd.to_datetime(df["signup_date"], errors="coerce")
issues["Invalid signup_date values"] = int(signup_dates.isna().sum())

# row count
row_count = len(df)
issues["Row count outside 500 to 1000"] = int(not (500 <= row_count <= 1000))

print("\nSummary of issues:")
for issue, count in issues.items():
    print(f"{issue}: {count}")

# Build Great Expectations Data Docs
context.build_data_docs()

print("Great Expectations Data Docs generated.")

context.open_data_docs()

print("Part 3 completed successfully.")

def load_csv(filepath):
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")
    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")

    if df.empty:
        raise ValueError("CSV file is empty")

    return df

def clean_phone(phone):
    if phone is None:
        return None

    phone = str(phone).strip()

    if phone == "":
        return None

    # Remove all non-digit characters
    digits = re.sub(r"\D", "", phone)

    # Handle leading country code
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    if len(digits) != 10:
        return None

    return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"

def validate_email(email):
    if email is None:
        return False

    email = str(email).strip()

    if email == "":
        return False

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return bool(re.match(pattern, email))

def test_load_csv_success(tmp_path):
    file_path = tmp_path / "sample.csv"
    file_path.write_text("customer_id,age,email\n1,25,test@example.com\n")

    df = load_csv(file_path)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert list(df.columns) == ["customer_id", "age", "email"]

def test_load_csv_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_csv("missing_file.csv")

def test_load_csv_empty_file(tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("")

    with pytest.raises(ValueError):
        load_csv(file_path)

def test_load_csv_headers_only_file(tmp_path):
    file_path = tmp_path / "headers_only.csv"
    file_path.write_text("customer_id,age,email\n")

    with pytest.raises(ValueError):
        load_csv(file_path)

def test_clean_phone_already_clean():
    assert clean_phone("123-456-7890") == "123-456-7890"

def test_clean_phone_with_parentheses():
    assert clean_phone("(123) 456-7890") == "123-456-7890"

def test_clean_phone_with_spaces():
    assert clean_phone("123 456 7890") == "123-456-7890"

def test_clean_phone_with_dots():
    assert clean_phone("123.456.7890") == "123-456-7890"

def test_clean_phone_with_country_code():
    assert clean_phone("+1 123 456 7890") == "123-456-7890"

def test_clean_phone_numeric_input():
    assert clean_phone(1234567890) == "123-456-7890"

def test_clean_phone_invalid_short_number():
    assert clean_phone("12345") is None

def test_clean_phone_invalid_long_number():
    assert clean_phone("123456789012345") is None

def test_clean_phone_none():
    assert clean_phone(None) is None

def test_clean_phone_empty_string():
    assert clean_phone("") is None

def test_clean_phone_letters_only():
    assert clean_phone("abc-def-ghij") is None

def test_validate_email_valid_basic():
    assert validate_email("student@example.com") is True

def test_validate_email_valid_with_period():
    assert validate_email("first.last@example.com") is True

def test_validate_email_valid_with_plus():
    assert validate_email("student+test@example.com") is True

def test_validate_email_valid_subdomain():
    assert validate_email("student@mail.example.com") is True

def test_validate_email_invalid_missing_at():
    assert validate_email("studentexample.com") is False

def test_validate_email_invalid_missing_username():
    assert validate_email("@example.com") is False

def test_validate_email_invalid_missing_domain():
    assert validate_email("student@") is False

def test_validate_email_invalid_missing_extension():
    assert validate_email("student@example") is False

def test_validate_email_none():
    assert validate_email(None) is False

def test_validate_email_empty_string():
    assert validate_email("") is False

def test_validate_email_with_spaces():
    assert validate_email("   student@example.com   ") is True