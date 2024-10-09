import re
import json
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from datetime import datetime


class TutorProfileValidator:
    """
    Validator class for handling and validating the data of a tutor's profile.
    This class performs various checks on fields such as email, phone number,
    date of birth (DOB), education details, and others.
    """

    def __init__(self, data) -> None:
        """
        Initialize the validator with data to validate.
        
        :param data: Dictionary containing the profile data to validate.
        """
        self.data = data
        self.errors = {}  # Dictionary to store validation errors.

    def validate(self):
        """
        Perform all validations on the provided profile data.
        
        :return: Dictionary of errors if any validation fails, otherwise an empty dictionary.
        """
        self.validate_required_fields()  # Validate mandatory fields.
        self.validate_email()            # Validate email format.
        self.validate_phone()            # Validate phone number format.
        self.validate_dob()              # Validate date of birth (DOB).
        self.validate_cv()               # Validate if CV is a valid file.
        self.validate_education()        # Validate education details.

        return self.errors  # Return any validation errors found.

    def validate_required_fields(self):
        """
        Validate that required fields are present and not empty.
        
        Adds error messages to self.errors if required fields are missing.
        """
        required_fields = {
            'first_name': 'First name is required',
            'last_name': 'Last name is required',
            'public_name': 'Public name is required',
            'headline': 'Headline is required',
            'bio': 'Bio is required',
            'profile': 'Profile is required'
        }
        # Loop through required fields and check if each field is present and non-empty.
        for field, message in required_fields.items():
            if not self.data.get(field):  # Check if the field exists and has a value.
                self.errors[field] = message  # Add error if the field is missing.

    def validate_email(self):
        """
        Validate the email format.
        
        Adds an error to self.errors if the email is invalid.
        """
        try:
            # Use Django's validate_email utility to check the email format.
            validate_email(self.data['email'])
        except ValidationError:
            self.errors['Email'] = 'Invalid email address'

    def validate_phone(self):
        """
        Validate the phone number format.
        
        Phone number should be between 10 and 15 digits and may include a '+' prefix.
        Adds an error if the phone format is invalid.
        """
        phone = self.data.get('phone')
        if phone:
            # Regular expression to check phone number format.
            if not re.match(r'^\+?\d{10,15}$', phone):
                self.errors['Phone'] = 'Invalid phone number format'
        else:
            self.errors['Phone'] = 'Phone is required'

    def validate_dob(self):
        """
        Validate the date of birth (DOB) field.
        
        Ensures the date is not in the future and follows the YYYY-MM-DD format.
        Adds an error if the DOB format is incorrect or if the date is invalid.
        """
        dob = self.data.get('dob')
        if dob:
            try:
                # Parse the DOB string to a datetime object.
                dob_date = datetime.strptime(dob, '%Y-%m-%d')
                # Ensure DOB is not in the future.
                if dob_date > datetime.now():
                    self.errors['Date of Birth'] = 'Date of birth cannot be in the future'
            except ValueError:
                # Catch any parsing errors due to invalid date format.
                self.errors['Date of Birth'] = 'Invalid date format for DOB'

    def validate_cv(self):
        """
        Validate the CV field, ensuring it contains a valid file.
        
        Adds an error if CV is not a valid file object.
        """
        cv = self.data.get('cv')
        if cv:
            # Check if the CV has a valid 'file' attribute, indicating it's a file object.
            if not hasattr(cv, 'file'):
                self.errors['CV'] = 'CV must be a valid file'

    def validate_education(self):
        """
        Validate the education field, ensuring it is a valid JSON string and contains 
        necessary details like highest qualification, institution, and year.
        
        Adds errors if the education format is invalid or if required fields are missing.
        """
        education = self.data.get('education')
        if education:
            try:
                # Parse the education field assuming it is a JSON string.
                education_data = json.loads(education)
                for edu in education_data:
                    # Check if each education entry has a highest qualification, institution, and year.
                    if not edu.get('highestQualification'):
                        self.errors['Education'] = 'Each education entry must have a highest qualification'
                    if not edu.get('institute'):
                        self.errors['Education'] = 'Each education entry must have an institution'
                    if not edu.get('year'):
                        self.errors['Education'] = 'Each education entry must have a year'
            except json.JSONDecodeError:
                # Catch errors if the education field is not valid JSON.
                self.errors['Education'] = 'Invalid JSON format for education'
