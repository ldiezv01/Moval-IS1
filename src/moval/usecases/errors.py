class UseCaseError(Exception): pass
class ValidationError(UseCaseError): pass
class NotFoundError(UseCaseError): pass
class PermissionError(UseCaseError): pass
class ConflictError(UseCaseError): pass
class InfrastructureError(UseCaseError): pass