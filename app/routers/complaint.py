from fastapi import APIRouter, status, HTTPException, Response
from loguru import logger

from app.access.complaint import access_complaint
from app.dto.complaint import ComplaintDto

complaint_router = APIRouter(prefix="/complaint", tags=["Жалобы"])


@complaint_router.get(
    "/get_open_complaints", 
    status_code=status.HTTP_200_OK, 
)
async def get_open_complaints(response: Response):
    complaint_dump = {'method': 'get', 'route': "get_open_complaints"}
    response = await access_complaint(**complaint_dump)
    if isinstance(response, HTTPException):
        return HTTPException(
            status_code=response.status_code, 
            detail=response.detail,
            args=response.args,
        )
    return response


@complaint_router.get(
    "/{id}",
    status_code=status.HTTP_200_OK, 
)
async def get_complaint(id: int, response: Response):

    complaint_dump = {'method': 'get', 'id': id}
    complaint_resp = await access_complaint(**complaint_dump)
    
    if isinstance(complaint_resp, dict):
        response.status_code = status.HTTP_200_OK
        return complaint_resp
    elif isinstance(complaint_resp, HTTPException):
        response.status_code = complaint_resp.status_code
        return complaint_resp
    else:
        response.status_code = 500
        return complaint_resp     # Если возникла ошибка


@complaint_router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=ComplaintDto.Response
)
async def create_complaint(complaint_dto: ComplaintDto.Create):

    complaint_dump = {'method': 'post', 'dto': complaint_dto.model_dump()}
    response = await access_complaint(**complaint_dump)

    # TODO: поправить обработку ошибок
    if isinstance(response, HTTPException):
        if hasattr(response, 'detail'):
            logger.error(response.detail)
        return HTTPException(status_code=response.status_code, detail=response.detail)
    return response


@complaint_router.patch(
    "/close_complaint/{id}",
    status_code=status.HTTP_200_OK
)
async def close_complaint(id: int):
    complaint_dump = {
        'method': 'patch', 
        'route': "close_complaint", 
        'id': id
    }
    response = await access_complaint(**complaint_dump)
    if isinstance(response, HTTPException):
        return HTTPException(
            status_code=response.status_code, 
            detail=response.detail,
            args=response.args,
        )
    return response


@complaint_router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
)
async def delete_complaint(id: int, response: Response):
    complaint_dump = {'method': 'delete', 'id': id}
    complaint_resp = await access_complaint(**complaint_dump)
    if isinstance(complaint_resp, HTTPException):
        response.status_code = complaint_resp.status_code
        return complaint_resp
    elif not isinstance(complaint_resp, dict):
        response.status_code = 500
        raise HTTPException(status_code=500, detail="Internal server error")
    return complaint_resp