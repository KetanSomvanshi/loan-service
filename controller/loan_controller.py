import http

from fastapi import APIRouter, Depends

from controller.context_manager import build_request_context
from models.base import GenericResponseModel
from models.loan import LoanModel, LoanInsertModel
from models.user import UserInsertModel, UserLoginModel
from server.auth import rbac_access_checker, RBACResource, RBACAccessType
from service.loan_service import LoanService
from service.user_service import UserService
from utils.helper import build_api_response

loan_router = APIRouter(prefix="/v1/loan", tags=["loan", "repayment"])


@loan_router.post("", status_code=http.HTTPStatus.CREATED, response_model=GenericResponseModel)
@rbac_access_checker(resource=RBACResource.loan, rbac_access_type=RBACAccessType.write)
async def create_loan(loan: LoanInsertModel, _=Depends(build_request_context)):
    """
    Apply for loan
    :param loan:  loan details to add
    :param _: build_request_context dependency injection handles the request context
    :return:
    """
    response: GenericResponseModel = LoanService.create_loan(loan=loan)
    return build_api_response(response)


@loan_router.get("", status_code=http.HTTPStatus.OK, response_model=GenericResponseModel)
@rbac_access_checker(resource=RBACResource.loan, rbac_access_type=RBACAccessType.read)
async def get_customer_loans(_=Depends(build_request_context)):
    """
    Get customer loans
    :param _: build_request_context dependency injection handles the request context
    :return:
    """
    response: GenericResponseModel = LoanService.get_customer_loans()
    return build_api_response(response)


@loan_router.post("/{loan_uuid}/repayment/{repayment_uuid}", status_code=http.HTTPStatus.CREATED,
                  response_model=GenericResponseModel)
@rbac_access_checker(resource=RBACResource.repayment, rbac_access_type=RBACAccessType.update)
async def add_repayment_by_customer(loan_uuid: str, repayment_uuid: str, _=Depends(build_request_context)):
    """
    Add repayment by customer
    :param loan_uuid: loan uuid to add repayment
    :param repayment_uuid: repayment uuid to add
    :param _: build_request_context dependency injection handles the request context
    :return:
    """
    response: GenericResponseModel = LoanService.add_repayment_by_customer(loan_uuid=loan_uuid,
                                                                           repayment_uuid=repayment_uuid)
    return build_api_response(response)


@loan_router.post("/{loan_uuid}/approve", status_code=http.HTTPStatus.CREATED, response_model=GenericResponseModel)
@rbac_access_checker(resource=RBACResource.loan, rbac_access_type=RBACAccessType.update)
async def approve_loan(loan_uuid: str, _=Depends(build_request_context)):
    """
    Approve loan
    :param loan_uuid: loan uuid to approve
    :param _: build_request_context dependency injection handles the request context
    :return:
    """
    response: GenericResponseModel = LoanService.approve_loan(loan_uuid=loan_uuid)
    return build_api_response(response)
