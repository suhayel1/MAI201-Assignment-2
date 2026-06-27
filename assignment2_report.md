GREAT EXPECTATIONS VALIDATION RESULTS:

<img width="1240" height="4351" alt="Screenshot_26-6-2026_2238_" src="https://github.com/user-attachments/assets/5e72bf41-6472-4e65-b44a-06a65af078ce" />


LIST OF ALL DATA QUALITY ISSUES WITH COUNTS:

Summary of issues:<br>
Missing customer_id values: 150<br>
Duplicate customer_id values: 452<br>
Missing age values: 147<br>
Invalid age values outside 0 to 120: 384<br>
Missing email values: 438<br>
Invalid email formats: 784<br>
Missing salary values: 425<br>
Invalid salary values that cannot be converted to numeric: 425<br>
Negative salary values: 159<br>
Invalid country values: 342<br>
Invalid or uncleanable phone numbers: 1066<br>
Invalid signup_date values: 256<br>
Row count outside 500 to 1000: 1<br>

SCREENSHOT OF PYTEST EXECUTION:

<img width="1115" height="628" alt="Screenshot 2026-06-26 213842" src="https://github.com/user-attachments/assets/94c9d1f3-ead7-4617-b541-e6310662330e" />


REFLECTION:

The data quality issue that would most impact ML model performance is the salary column issue.<br>
Salary is likely to be an important numerical feature in a customer dataset because it can influence customer behavior, segmentation, purchasing power, and predictions in ML models. However, the dataset contains salary values stored as strings with dollar signs, missing salary values, and negative salary values.<br>
If salary isn’t cleaned properly, it may cause problems during model training because ML models usually require numerical input. Values such as “$50,000” may be read as a string instead of int, which means the model cannot use the feature correctly. Missing salary values can reduce the quality of the training data, while negative salary values are unrealistic and may distort statistics such as averages, distributions, and scaling.<br>
