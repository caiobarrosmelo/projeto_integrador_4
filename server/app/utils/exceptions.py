"""
Exceções customizadas para a API
Padroniza tratamento de erros em toda a aplicação
"""


class APIException(Exception):
    """Exceção base da API"""
    status_code = 500
    message = "Erro interno do servidor"
    error_code = "INTERNAL_ERROR"
    
    def __init__(self, message=None, status_code=None, error_code=None):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code
        if error_code:
            self.error_code = error_code
        super().__init__(self.message)
    
    def to_dict(self):
        """Converte exceção para dicionário"""
        return {
            'error': self.message,
            'error_code': self.error_code,
            'status_code': self.status_code
        }


class ValidationError(APIException):
    """Erro de validação de dados"""
    status_code = 400
    message = "Dados inválidos"
    error_code = "VALIDATION_ERROR"


class NotFoundError(APIException):
    """Recurso não encontrado"""
    status_code = 404
    message = "Recurso não encontrado"
    error_code = "NOT_FOUND"


class DatabaseError(APIException):
    """Erro de banco de dados"""
    status_code = 500
    message = "Erro ao acessar banco de dados"
    error_code = "DATABASE_ERROR"


class AuthenticationError(APIException):
    """Erro de autenticação"""
    status_code = 401
    message = "Não autenticado"
    error_code = "AUTHENTICATION_ERROR"


class AuthorizationError(APIException):
    """Erro de autorização"""
    status_code = 403
    message = "Não autorizado"
    error_code = "AUTHORIZATION_ERROR"


class RateLimitError(APIException):
    """Erro de rate limiting"""
    status_code = 429
    message = "Muitas requisições. Tente novamente mais tarde."
    error_code = "RATE_LIMIT_EXCEEDED"

