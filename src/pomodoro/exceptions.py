from fastapi import HTTPException, status


HTTPException400 = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail='Wrong input')
HTTPException409 = HTTPException(
    status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='can\'t create becouse invalid ID'
)
