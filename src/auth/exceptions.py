from fastapi import HTTPException, status


HTTPException400 = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST, detail='bad_request')

HTTPException401 = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="Inputed values isn't correct")

HTTPException409 = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail='Already exists')
