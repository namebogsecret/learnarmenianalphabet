"""
Пользовательские исключения для Armenian Learning Bot.

Содержит классы исключений для различных типов ошибок в приложении.
"""


class BotException(Exception):
    """
    Базовое исключение для всех ошибок бота.
    
    Attributes:
        message: Сообщение об ошибке.
        user_id: ID пользователя, для которого произошла ошибка.
    """
    
    def __init__(self, message: str, user_id: int = None):
        """
        Инициализирует исключение.
        
        Args:
            message: Сообщение об ошибке.
            user_id: ID пользователя, для которого произошла ошибка.
        """
        self.message = message
        self.user_id = user_id
        super().__init__(self.message)


class DatabaseException(BotException):
    """
    Исключение для ошибок базы данных.
    
    Attributes:
        message: Сообщение об ошибке.
        query: SQL-запрос, вызвавший ошибку.
        params: Параметры запроса.
        user_id: ID пользователя, для которого произошла ошибка.
    """
    
    def __init__(self, message: str, query: str = None, params: tuple = None, user_id: int = None):
        """
        Инициализирует исключение.
        
        Args:
            message: Сообщение об ошибке.
            query: SQL-запрос, вызвавший ошибку.
            params: Параметры запроса.
            user_id: ID пользователя, для которого произошла ошибка.
        """
        self.query = query
        self.params = params
        super().__init__(message, user_id)
    
    def __str__(self):
        """
        Возвращает строковое представление исключения.
        
        Returns:
            Строковое представление исключения.
        """
        if self.query:
            query_str = f"\nQuery: {self.query}"
            if self.params:
                query_str += f"\nParams: {self.params}"
            return f"{self.message}{query_str}"
        return self.message


class APIException(BotException):
    """
    Исключение для ошибок внешних API.
    
    Attributes:
        message: Сообщение об ошибке.
        api_name: Название API.
        status_code: Код HTTP-статуса.
        response: Ответ API.
        user_id: ID пользователя, для которого произошла ошибка.
    """
    
    def __init__(self, message: str, api_name: str = None, status_code: int = None,
                 response: str = None, user_id: int = None):
        """
        Инициализирует исключение.
        
        Args:
            message: Сообщение об ошибке.
            api_name: Название API.
            status_code: Код HTTP-статуса.
            response: Ответ API.
            user_id: ID пользователя, для которого произошла ошибка.
        """
        self.api_name = api_name
        self.status_code = status_code
        self.response = response
        super().__init__(message, user_id)
    
    def __str__(self):
        """
        Возвращает строковое представление исключения.
        
        Returns:
            Строковое представление исключения.
        """
        error_str = self.message
        if self.api_name:
            error_str += f"\nAPI: {self.api_name}"
        if self.status_code:
            error_str += f"\nStatus Code: {self.status_code}"
        if self.response:
            error_str += f"\nResponse: {self.response}"
        return error_str


class ValidationException(BotException):
    """
    Исключение для ошибок валидации данных.
    
    Attributes:
        message: Сообщение об ошибке.
        field: Поле, в котором произошла ошибка.
        value: Значение, вызвавшее ошибку.
        user_id: ID пользователя, для которого произошла ошибка.
    """
    
    def __init__(self, message: str, field: str = None, value: str = None, user_id: int = None):
        """
        Инициализирует исключение.
        
        Args:
            message: Сообщение об ошибке.
            field: Поле, в котором произошла ошибка.
            value: Значение, вызвавшее ошибку.
            user_id: ID пользователя, для которого произошла ошибка.
        """
        self.field = field
        self.value = value
        super().__init__(message, user_id)
    
    def __str__(self):
        """
        Возвращает строковое представление исключения.
        
        Returns:
            Строковое представление исключения.
        """
        if self.field:
            field_str = f"\nField: {self.field}"
            if self.value:
                field_str += f"\nValue: {self.value}"
            return f"{self.message}{field_str}"
        return self.message


class NotEnoughPermissionsException(BotException):
    """
    Исключение для ошибок доступа.
    
    Attributes:
        message: Сообщение об ошибке.
        required_permission: Требуемое разрешение.
        user_id: ID пользователя, для которого произошла ошибка.
    """
    
    def __init__(self, message: str = "Недостаточно прав", required_permission: str = None,
                 user_id: int = None):
        """
        Инициализирует исключение.
        
        Args:
            message: Сообщение об ошибке.
            required_permission: Требуемое разрешение.
            user_id: ID пользователя, для которого произошла ошибка.
        """
        self.required_permission = required_permission
        super().__init__(message, user_id)
    
    def __str__(self):
        """
        Возвращает строковое представление исключения.
        
        Returns:
            Строковое представление исключения.
        """
        if self.required_permission:
            return f"{self.message}\nRequired Permission: {self.required_permission}"
        return self.message


class ResourceNotFoundException(BotException):
    """
    Исключение для ошибок отсутствия ресурса.
    
    Attributes:
        message: Сообщение об ошибке.
        resource_type: Тип ресурса.
        resource_id: ID ресурса.
        user_id: ID пользователя, для которого произошла ошибка.
    """
    
    def __init__(self, message: str = "Ресурс не найден", resource_type: str = None,
                 resource_id: str = None, user_id: int = None):
        """
        Инициализирует исключение.
        
        Args:
            message: Сообщение об ошибке.
            resource_type: Тип ресурса.
            resource_id: ID ресурса.
            user_id: ID пользователя, для которого произошла ошибка.
        """
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(message, user_id)
    
    def __str__(self):
        """
        Возвращает строковое представление исключения.
        
        Returns:
            Строковое представление исключения.
        """
        error_str = self.message
        if self.resource_type:
            error_str += f"\nResource Type: {self.resource_type}"
        if self.resource_id:
            error_str += f"\nResource ID: {self.resource_id}"
        return error_str


class RateLimitException(BotException):
    """
    Исключение для ошибок превышения лимита запросов.
    
    Attributes:
        message: Сообщение об ошибке.
        limit: Лимит запросов.
        period: Период времени в секундах.
        retry_after: Время до сброса лимита в секундах.
        user_id: ID пользователя, для которого произошла ошибка.
    """
    
    def __init__(self, message: str = "Превышен лимит запросов", limit: int = None,
                 period: int = None, retry_after: int = None, user_id: int = None):
        """
        Инициализирует исключение.
        
        Args:
            message: Сообщение об ошибке.
            limit: Лимит запросов.
            period: Период времени в секундах.
            retry_after: Время до сброса лимита в секундах.
            user_id: ID пользователя, для которого произошла ошибка.
        """
        self.limit = limit
        self.period = period
        self.retry_after = retry_after
        super().__init__(message, user_id)
    
    def __str__(self):
        """
        Возвращает строковое представление исключения.
        
        Returns:
            Строковое представление исключения.
        """
        error_str = self.message
        if self.limit and self.period:
            error_str += f"\nLimit: {self.limit} requests per {self.period} seconds"
        if self.retry_after:
            error_str += f"\nRetry After: {self.retry_after} seconds"
        return error_str