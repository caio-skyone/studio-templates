from studio_iac.iac.errors import IACValidationFailed
from studio_iac.iac.models import (
    IACValidationError,
    IACValidationResult,
)


def test_validation_failed_formats_error_details():
    validation = IACValidationResult(
        ok=False,
        errors=[
            IACValidationError(
                path="settings.authentication_type",
                message="must_be_one_value (value='bearer')",
            ),
            IACValidationError(
                path="operations[0].request.header[0].enabled",
                message="required_field",
            ),
        ],
    )

    error = IACValidationFailed(validation)

    assert str(error) == (
        "IAC validation failed:\n"
        "  settings.authentication_type: must_be_one_value (value='bearer')\n"
        "  operations[0].request.header[0].enabled: required_field"
    )


def test_validation_failed_without_errors_uses_generic_message():
    error = IACValidationFailed(IACValidationResult(ok=False))

    assert str(error) == "IAC validation failed before import"
