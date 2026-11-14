from wapang.common.exceptions import WapangException


class StoreNotFoundException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            error_code="ERR_010",
            error_msg="STORE NOT FOUND",
        )


class NoStoreOwnedException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=403,
            error_code="ERR_011",
            error_msg="NO STORE OWNED",
        )


class ItemNotFoundException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=404,
            error_code="ERR_013",
            error_msg="ITEM NOT FOUND",
        )


class NotYourItemException(WapangException):
    def __init__(self) -> None:
        super().__init__(
            status_code=403,
            error_code="ERR_014",
            error_msg="NOT YOUR ITEM",
        )
