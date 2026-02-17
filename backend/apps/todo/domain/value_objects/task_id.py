from ulid import ULID


class ULIDGenerator:
    """Generator for ULID-based unique identifiers."""

    @staticmethod
    def generate() -> str:
        """Generate a new ULID string."""
        return str(ULID())

    @staticmethod
    def is_valid(ulid_str: str) -> bool:
        """Validate ULID string format."""
        try:
            ULID.from_str(ulid_str)
            return True
        except (ValueError, AttributeError):
            return False
