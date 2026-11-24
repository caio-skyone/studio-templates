"""Local, network-free validation entry point."""

from studio_iac.iac.models import (
    IACModule,
    IACValidationError,
    IACValidationResult,
)
from studio_iac.iac.rules import validate_module


def local_validation(module: IACModule) -> IACValidationResult:
    """Full offline validation, with every path prefixed `local:`."""
    result = validate_module(module)
    return IACValidationResult(
        ok=result.ok,
        errors=[_prefixed(error, "local") for error in result.errors],
        warnings=[_prefixed(warning, "local") for warning in result.warnings],
    )


def local_naming_validation(module: IACModule) -> IACValidationResult | None:
    """Back-compat shim: None when clean, a failure result otherwise."""
    result = local_validation(module)
    return None if result.ok else result


def _prefixed(error: IACValidationError, layer: str) -> IACValidationError:
    return IACValidationError(path=f"{layer}:{error.path}", message=error.message)


def prefixed_result(result: IACValidationResult, layer: str) -> IACValidationResult:
    return IACValidationResult(
        ok=result.ok,
        errors=[_prefixed(error, layer) for error in result.errors],
        warnings=[_prefixed(warning, layer) for warning in result.warnings],
    )
