from typing import List

from sqlalchemy import Column, String, Float, INTEGER, ForeignKey
from sqlalchemy.orm import Session, relationship, contains_eager

from data_adapter.db import LoanDBBase, DBBase
from data_adapter.user import User
from models.loan import LoanModel, RepaymentModel, LoanStatus


class Loan(DBBase, LoanDBBase):
    __tablename__ = 'loan'

    amount = Column(Float, nullable=False)
    status = Column(String(20), nullable=False)
    customer_id = Column(INTEGER, ForeignKey(User.id), nullable=False)
    date = Column(String(20), nullable=False)
    terms = Column(INTEGER, nullable=False)
    #  relationship one to one with user
    customer = relationship(User)

    # relationship one to many with repayment
    repayments = relationship('Repayment', backref='loan')

    def __to_model(self) -> LoanModel:
        """converts db orm object to pydantic model"""
        self.date = self.date.strftime("%Y-%m-%d") if not isinstance(self.date, str) else self.date
        repayments = [repayment.get_model() for repayment in self.repayments] if self.repayments else []
        self.repayments = []
        load_data = LoanModel.from_orm(self)
        load_data.repayments = repayments if repayments else []
        return load_data

    @classmethod
    def create_loan(cls, loan) -> LoanModel:
        from controller.context_manager import get_db_session
        db: Session = get_db_session()
        db.add(loan)
        db.flush()
        return loan.__to_model()

    @classmethod
    def get_by_id(cls, id) -> LoanModel:
        loan = super().get_by_id(id)
        return loan.__to_model() if loan else None

    @classmethod
    def get_by_uuid(cls, uuid) -> LoanModel:
        from controller.context_manager import get_db_session
        db = get_db_session()
        loan = db.query(cls).filter(cls.uuid == uuid, cls.is_deleted.is_(False)).first()
        return loan.__to_model() if loan else None

    @classmethod
    def get_active_loan_by_loan_uuid(cls, loan_uuid) -> LoanModel:
        from controller.context_manager import get_db_session
        db = get_db_session()
        loan = db.query(cls).filter(cls.uuid == loan_uuid, cls.is_deleted.is_(False)).first()
        return loan.__to_model() if loan else None

    @classmethod
    def get_all_customer_loans(cls, customer_id) -> List[LoanModel]:
        from controller.context_manager import get_db_session
        db = get_db_session()
        loans = db.query(cls).join(Repayment).filter(cls.customer_id == customer_id,cls.is_deleted.is_(False)).all()
        return [loan.__to_model() for loan in loans] if loans else []

    @classmethod
    def update_loan_by_uuid(cls, loan_uuid: str, update_dict: dict) -> int:
        from controller.context_manager import get_db_session
        db = get_db_session()
        db.query(cls).filter(cls.uuid == loan_uuid, cls.is_deleted.is_(False)).update({cls.status: LoanStatus.PAID})
        return 0


class Repayment(DBBase, LoanDBBase):
    __tablename__ = 'repayment'

    loan_id = Column(INTEGER, ForeignKey(Loan.id), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False)


    def __to_model(self) -> RepaymentModel:
        """converts db orm object to pydantic model"""
        self.date = self.date.strftime("%Y-%m-%d") if not isinstance(self.date, str) else self.date
        return RepaymentModel.from_orm(self)

    def get_model(self) -> RepaymentModel:
        """converts db orm object to pydantic model"""
        return self.__to_model()

    @classmethod
    def create_payments(cls, payments) -> List[RepaymentModel]:
        from controller.context_manager import get_db_session
        db: Session = get_db_session()
        db.add_all(payments)
        db.flush()
        return [payment.__to_model() for payment in payments] if payments else None

    @classmethod
    def update_by_uuid(cls, uuid, update_dict: dict) -> int:
        from controller.context_manager import get_db_session
        db = get_db_session()
        updates = db.query(cls).filter(cls.uuid == uuid, cls.is_deleted.is_(False)).update(update_dict)
        db.flush()
        return updates
