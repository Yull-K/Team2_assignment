from wapang.common.exceptions import WapangException


class ItemNotFoundException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=404,
            error_code="ERR_013",
            error_msg="ITEM NOT FOUND"
        )


class NotEnoughStockException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=409,
            error_code="ERR_017",
            error_msg="NOT ENOUGH STOCK"
        )


class EmptyItemListException(WapangException):
    def __init__(self):
        super().__init__(
            status_code=422,
            error_code="ERR_018",
            error_msg="EMPTY ITEM LIST"
        )