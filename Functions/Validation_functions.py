from marshmallow.validate import Length, And, Regexp, Email, Range


# I dont know if this the standard way of doing it, but made sense to me. I can save a lot of code and potential use theses functions in 100's of schema's if the application requires it.


def string_validation(*args, **kwargs):
    # just get the keyword arguments to set the variables for min and max
    maximum_length = kwargs.get("max") if kwargs.get("max") else 2000
    minimum_length = kwargs.get("min") if kwargs.get("min") else 2
    validation = [
        And(
            Length(
                min=minimum_length,
                error=f"Name must be at least {minimum_length} characters long",
            ),
            Length(
                max=maximum_length,
                error=f"Name must not be more than {str(maximum_length)} characters long",
            ),
        )
    ]

    # figured out i could make the validation a list and just append the regexp i need to it. depending on what kwargs are passed.
    if kwargs.get("email"):
        validation.append(Email(error="Invalid email format"))

    elif kwargs.get("all_char"):
        validation.append(
            Regexp(
                "^[a-zA-Z0-9,.;:\-\s! ]+$",
                error="Characters can be alphanumeric A-Z, 0-9 and '-,.;:!' ",
            )
        )
    else:
        validation.append(
            Regexp(
                "^[a-zA-Z ]+$",
                error="Names can only contain alphabetical characters A-Z",
            )
        )

    return validation


def password_validation(*args, **kwargs):
    validation = And(
        Length(min=8, error="Password must be at least 8 characters long"),
        Length(max=25, error="Password must not be more than 25 characters long"),
        Regexp(
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$",
            error="Password must contain at least one lowercase letter, one uppercase letter, one digit.",
        ),
    )
    return validation


def integer_validation(*args, **kwargs):
    maximum = kwargs.get("max") if kwargs.get("max") else 10
    minimum = kwargs.get("min") if kwargs.get("min") else 0
    validation = And(
        Range(min=0, error=f"Must be a number equally to or greater than {minimum}."),
        Range(
            max=maximum, error=f"must be a number equally to or less than {maximum}."
        ),
    )
    return validation
