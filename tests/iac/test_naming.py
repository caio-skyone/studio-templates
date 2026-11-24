import uuid

import pytest

from studio_iac.iac.errors import (
    IACDuplicateOperationName,
    IACDuplicateParameterName,
)
from studio_iac.iac.models import (
    IACModule,
    IACModuleSettings,
    IACOperation,
    IACParameter,
    IACRequestUrl,
    IACRestRequest,
)
from studio_iac.iac.naming import (
    ensure_operation_name_available,
    ensure_operation_names_available_for_batch,
    ensure_parameter_name_available,
    ensure_parameter_names_available_for_batch,
    ensure_unique_operation_names,
    ensure_unique_parameter_names,
)


def _uuid4() -> str:
    return str(uuid.uuid4())


def _rest_request() -> IACRestRequest:
    return IACRestRequest(method="GET", url=IACRequestUrl(path=["api"]))


def _operation(name: str, operation_id: str | None = None) -> IACOperation:
    return IACOperation(
        id=operation_id or _uuid4(),
        name=name,
        request=_rest_request(),
    )


def _parameter(name: str, parameter_id: str | None = None) -> IACParameter:
    return IACParameter(
        id=parameter_id or _uuid4(),
        name=name,
        type="string",
        required=True,
        sensitive=False,
        sample="1",
    )


def test_ensure_unique_operation_names_raises_on_duplicate():
    operations = [_operation("List"), _operation("List")]

    with pytest.raises(IACDuplicateOperationName, match="List"):
        ensure_unique_operation_names(operations)


def test_ensure_operation_name_available_ignores_excluded_operation():
    operation_id = _uuid4()
    operations = [_operation("List", operation_id=operation_id)]

    ensure_operation_name_available(
        operations,
        "List",
        exclude_operation_id=operation_id,
    )


def test_ensure_operation_names_available_for_batch_rejects_intra_batch_duplicate():
    with pytest.raises(IACDuplicateOperationName, match="List"):
        ensure_operation_names_available_for_batch([], ["List", "List"])


def test_ensure_unique_parameter_names_raises_on_duplicate():
    parameters = [_parameter("user_id"), _parameter("user_id")]

    with pytest.raises(IACDuplicateParameterName, match="user_id"):
        ensure_unique_parameter_names(parameters)


def test_ensure_parameter_name_available_rejects_existing_name():
    parameters = [_parameter("user_id")]

    with pytest.raises(IACDuplicateParameterName, match="user_id"):
        ensure_parameter_name_available(parameters, "user_id")


def test_ensure_parameter_names_available_for_batch_rejects_existing_name():
    parameters = [_parameter("user_id")]

    with pytest.raises(IACDuplicateParameterName, match="user_id"):
        ensure_parameter_names_available_for_batch(parameters, ["user_id", "page"])


def test_module_rejects_duplicate_operation_names():
    with pytest.raises(Exception, match="operation name 'List'"):
        IACModule(
            id=_uuid4(),
            type="rest",
            settings=IACModuleSettings(),
            operations=[_operation("List"), _operation("List")],
        )


def test_module_rejects_duplicate_parameter_names_in_operation():
    operation_id = _uuid4()
    with pytest.raises(Exception, match="parameter name 'user_id'"):
        IACModule(
            id=_uuid4(),
            type="rest",
            settings=IACModuleSettings(),
            operations=[
                IACOperation(
                    id=operation_id,
                    name="List",
                    request=_rest_request(),
                    parameters=[_parameter("user_id"), _parameter("user_id")],
                ),
            ],
        )
