from fastapi import HTTPException


def http_unauthorized(detail: str = "Unauthorized") -> HTTPException:
    return HTTPException(status_code=401, detail=detail)


def http_unprocessable(detail: str) -> HTTPException:
    return HTTPException(status_code=422, detail=detail)


def http_internal(detail: str = "Internal error") -> HTTPException:
    return HTTPException(status_code=500, detail=detail)
