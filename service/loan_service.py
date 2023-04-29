import http
from datetime import timedelta, datetime

from controller.context_manager import context_log_meta, context_actor_user_data
from data_adapter.loan import Loan, Repayment
from data_adapter.user import User
from logger import logger
from models.base import GenericResponseModel
from models.loan import LoanInsertModel, LoanModel, RepaymentInsertModel, RepaymentStatus, LoanStatus
from models.user import UserInsertModel, UserLoginModel, UserModel, UserTokenResponseModel
from utils.jwt_token_handler import JWTHandler
from utils.password_hasher import PasswordHasher


class LoanService:
    MSG_LOAN_CREATED_SUCCESS = "Loan created successfully"

    @staticmethod
    def create_loan(loan: LoanInsertModel) -> GenericResponseModel:
        """
        Create loan
        :param loan: loan details to add
        :return: GenericResponseModel
        """
        customer_data = User.get_by_uuid(context_actor_user_data.get().uuid)
        if not customer_data:
            logger.error(extra=context_log_meta.get(), msg="Customer not found")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, message="Customer not found")
        loan_to_create = loan.create_db_entity(customer_id=customer_data.id)
        loan_data = Loan.create_loan(loan_to_create)
        # create repayments
        response = LoanService.create_repayments(loan_data)
        if response.error:
            logger.error(extra=context_log_meta.get(),
                         msg="Error while creating repayments for loan {}".format(loan_to_create.uuid))
            return response
        loan_data.repayments = response.data
        logger.info(extra=context_log_meta.get(),
                    msg="Loan created successfully with uuid {}".format(loan_to_create.uuid))
        return GenericResponseModel(status_code=http.HTTPStatus.CREATED, message=LoanService.MSG_LOAN_CREATED_SUCCESS,
                                    data=loan_data)

    @staticmethod
    def create_repayments(loan: LoanModel) -> GenericResponseModel:
        """
        Create repayments
        :param loan: loan details to add
        :return: GenericResponseModel
        """
        # for loan terms create weekly dates of repayments and create repayment entities
        repayments_to_add = []
        # create repayments
        for i in range(1, loan.terms + 1):
            repayments_to_add.append(RepaymentInsertModel(loan_id=loan.id, amount=loan.amount / loan.terms,
                                                          date=(datetime.strptime(loan.date, '%Y-%m-%d') + timedelta(
                                                              weeks=i)).strftime(
                                                              "%Y-%m-%d"),
                                                          status=RepaymentStatus.PENDING))
            # add repayments
        repayments_to_add = [repayment.create_db_entity() for repayment in repayments_to_add]
        created_repayments = Repayment.create_payments(repayments_to_add)
        return GenericResponseModel(status_code=http.HTTPStatus.CREATED, message=LoanService.MSG_LOAN_CREATED_SUCCESS,
                                    data=created_repayments)

    @staticmethod
    def approve_loan(loan_uuid: str) -> GenericResponseModel:
        """
        Approve loan
        :param loan_uuid: loan uuid to approve
        :return: GenericResponseModel
        """
        loan_data = Loan.get_by_uuid(loan_uuid)
        if not loan_data:
            logger.error(extra=context_log_meta.get(), msg="Loan not found")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND,
                                        message="Loan not found")
        Loan.update_loan_by_uuid(loan_uuid, {Loan.status: LoanStatus.APPROVED})
        loan_data.status = LoanStatus.APPROVED
        return GenericResponseModel(status_code=http.HTTPStatus.CREATED, message=LoanService.MSG_LOAN_CREATED_SUCCESS,
                                    data=loan_data)

    @staticmethod
    def get_customer_loans() -> GenericResponseModel:
        """
        Get customer loans
        :return: GenericResponseModel
        """
        customer_data = User.get_by_uuid(context_actor_user_data.get().uuid)
        if not customer_data:
            logger.error(extra=context_log_meta.get(), msg="Customer not found")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, message="Customer not found")
        loans = Loan.get_all_customer_loans(customer_data.id)
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message="Customer loans fetched successfully",
                                    data=loans)

    @staticmethod
    def add_repayment_by_customer(loan_uuid: str, repayment_uuid: str) -> GenericResponseModel:
        """
        Add repayment by customer
        :param loan_uuid:  loan uuid to add
        :param repayment_uuid: repayment uuid to add
        :return: GenericResponseModel
        """
        loan_data = Loan.get_by_uuid(loan_uuid)
        if not loan_data:
            logger.error(extra=context_log_meta.get(), msg="Loan not found")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, message="Loan not found")
        if loan_data.status == LoanStatus.PAID:
            logger.error(extra=context_log_meta.get(), msg="Loan already paid")
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, message="Loan already paid")
        customer_data = User.get_by_uuid(context_actor_user_data.get().uuid)
        if not customer_data:
            logger.error(extra=context_log_meta.get(), msg="Customer not found")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, message="Customer not found")
        if loan_data.customer_id != customer_data.id:
            logger.error(extra=context_log_meta.get(), msg="Loan does not belong to customer")
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST,
                                        message="Loan does not belong to customer")

        repayment_data = None
        number_of_unpaid_loans = 0
        for repayment in loan_data.repayments:
            if repayment.uuid == repayment_uuid:
                repayment_data = repayment
            if repayment.status == RepaymentStatus.PENDING:
                number_of_unpaid_loans += 1
        if not repayment_data:
            logger.error(extra=context_log_meta.get(), msg="Repayment not found")
            return GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, message="Repayment not found")
        if repayment_data.status == RepaymentStatus.PAID:
            logger.error(extra=context_log_meta.get(), msg="Repayment already paid")
            return GenericResponseModel(status_code=http.HTTPStatus.BAD_REQUEST, message="Repayment already paid")
        # update repayment status
        repayment_data = Repayment.update_by_uuid(repayment_uuid, {"status": RepaymentStatus.PAID})
        # update loan status
        if number_of_unpaid_loans == 1:
            Loan.update_loan_by_uuid(loan_uuid, {"status": LoanStatus.PAID})
        return GenericResponseModel(status_code=http.HTTPStatus.OK, message="Repayment updated successfully",
                                    data=repayment_data)
