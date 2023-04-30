from datetime import datetime
from enum import Enum
from typing import List, Optional, Any

from pydantic import BaseModel

from models.base import DBBaseModel


class LoanStatus(str, Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PAID = 'paid'


class RepaymentStatus(str, Enum):
    PENDING = 'pending'
    PAID = 'paid'


class RepaymentInsertModel(BaseModel):
    """Repayment model for insert"""
    amount: float
    status: RepaymentStatus = RepaymentStatus.PENDING
    loan_id: int
    date: Any

    def create_db_entity(self):
        from data_adapter.loan import Repayment
        return Repayment(**self.dict())


class RepaymentModel(DBBaseModel, RepaymentInsertModel):
    """Repayment model for insert"""
    pass


class LoanInsertModel(BaseModel):
    """Loan model for insert"""
    amount: float
    terms: int
    status: LoanStatus = LoanStatus.PENDING
    date: str

    def create_db_entity(self, customer_id):
        from data_adapter.loan import Loan
        res_dict = self.dict()
        res_dict['customer_id'] = customer_id
        return Loan(**res_dict)


class LoanModel(DBBaseModel, LoanInsertModel):
    """Loan model for insert"""
    customer_id: int
    repayments: Optional[List[RepaymentModel]] = []
