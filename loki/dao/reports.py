from loki.models import Report
from loki import db


class ReportDAO():
    """Class to handle all database access
    required for the models.Report class.
    """
    __instance__ = None

    def __init__(self):
        if ReportDAO.__instance__ is None:
            ReportDAO.__instance__ = self
        else:
            raise Exception("You cannot create another ReportDAO class")

    @staticmethod
    def get_instance():
        if not ReportDAO.__instance__:
            ReportDAO()
        return ReportDAO.__instance__

    def add(self, report):
        db.session.add(report)
        db.session.commit()

    def get_all(self):
        return db.session.query(Report).all()

    def get_by_report_id(self, report_id):
        return db.session.query(Report).get(report_id)

    def get_by_user_id(self, user_id):
        return db.session.query(Report).filter_by(user_id).all()


report_dao = ReportDAO()
