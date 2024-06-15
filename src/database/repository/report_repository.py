from datetime import datetime

from sqlalchemy import func

from src.database import db
from src.database.models.models import Report


def add_report(report: Report):
    session = db.session
    session.add(report)
    session.commit()
    session.refresh(report)
    return report


def get_all_reports(reportee):
    session = db.session
    return session.query(Report, func.count(Report.reporting_id)) \
        .filter(Report.reportee_id == reportee.id) \
        .group_by(Report.reporting_id) \
        .order_by(func.count(Report.reporting_id).desc()) \
        .all()


def get_reports():
    session = db.session
    return session.query(Report, func.count(Report.reporting_id)) \
        .group_by(Report.reporting_id) \
        .order_by(func.count(Report.reporting_id).desc()) \
        .all()


def get_last_reports(guild, reporting):
    session = db.session
    return session.query(Report) \
        .order_by(func.count(Report.reporting_id).desc()) \
        .all()


def report_allowed(guild, reporting):
    report = get_last_reports(guild, reporting.name)

    if report is None:
        return None

    diff = datetime.now() - report['time']
    if diff.total_seconds() // 60 < 30:
        return 30 - diff.seconds // 60
    else:
        return None
