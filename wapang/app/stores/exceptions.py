from wapang.common.exceptions import WapangException

class StoreAlreadyExistsException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=409, 
            error_code="ERR_008", 
            error_msg="STORE ALREADY EXISTS"
        )

class StoreInfoConflictException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=409, 
            error_code="ERR_009", 
            error_msg="STORE INFO CONFLICT"
        )

class StoreNotFoundException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=404, 
            error_code="ERR_010", 
            error_msg="STORE NOT FOUND"
        )

class NoStoreOwnedException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=403, 
            error_code="ERR_011", 
            error_msg="NO STORE OWNED"
        )

class NotYourStoreException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=403, 
            error_code="ERR_012", 
            error_msg="NOT YOUR STORE"
        )