from loki.dao.reports import report_dao, Report, db
import datetime


class ReportService():
    __instance__ = None

    def __init__(self):
        if ReportService.__instance__ is None:
            ReportService.__instance__ = self
        else:
            raise Exception("You cannot create another ReportService class")

    @staticmethod
    def get_instance():
        if not ReportService.__instance__:
            ReportService()
        return ReportService.__instance__

    def create_report(self, pretrained_classifier,
                      data, model=None,
                      date=datetime.datetime.now):
        if (pretrained_classifier is None) and (data is None):
            return None

        report = Report(pretrained_classifier=pretrained_classifier,
                        data=data, model=model,
                        date=date)
        report_dao.add(report)
        return report

    def update_report(self, report_id,
                      pretrained_classifier=None,
                      data=None, model=None,
                      date=None):
        if (report_id is None):
            return False

        if (pretrained_classifier is None) and \
           (data is None) and (model is None) and (date is None):
            return False

        try:
            report = report_dao.get_by_report_id(report_id=report_id)

            if pretrained_classifier:
                report.pretrained_classifier = pretrained_classifier
            if data:
                report.data = data
            if model:
                report.model = model
            if date:
                report.date = date

            db.session.commit()

            return True

        except Exception:
            return False

    def delete_report(self, report_id):
        if report_id is None:
            return False

        try:
            report = report_dao.get_by_report_id(report_id)

            report.delete()
            db.session.commit()

            return True

        except Exception:
            return False


report_service = ReportService()
