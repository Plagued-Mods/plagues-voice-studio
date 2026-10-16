"""Human-readable errors that do not depend on Qt or model imports."""
from __future__ import annotations

def friendly_generation_error(exc: Exception) -> str:
    """Diagnose known OS resource errors without masking underlying exceptions."""
    detail = str(exc)
    if ('paging file is too small' in detail.lower()
            or 'os error 1455' in detail.lower()
            or 'winerror 1455' in detail.lower()):
        return (
            'Windows error 1455: not enough virtual memory available to load the speech model. '
            'Enable a system-managed Windows paging file (or enlarge it), leave sufficient '
            'free disk space, then reboot. For lower CPU memory use, select Nano. '
            f'Original error: {detail}'
        )
    return detail


