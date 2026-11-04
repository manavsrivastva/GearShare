class GearShareError(Exception):
    """Base exception for all GearShare application errors."""


class ValidationError(GearShareError):
    """Raised when supplied data is invalid."""


class InvalidSKUError(ValidationError):
    """Raised when an SKU is invalid or does not exist."""


class CustomerNotFoundError(GearShareError):
    """Raised when a customer cannot be found."""


class DisplayItemRentalError(GearShareError):
    """Raised when someone tries to rent a display-only item."""


class UnpaidFineError(GearShareError):
    """Raised when unpaid fines exceed the permitted limit."""


class TierLimitError(GearShareError):
    """Raised when a customer exceeds their rental limit."""


class DuplicateRentalError(GearShareError):
    """Raised when a customer already has the same item."""


class ItemUnavailableError(GearShareError):
    """Raised when no unit of an item is available."""


class ExtensionNotAllowedError(GearShareError):
    """Raised when a rental cannot be extended."""