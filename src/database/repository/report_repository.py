from datetime import datetime

from sqlalchemy import func

from src import bot
from src.database.models.models import Report


def add_report(report: Report):
    session = bot.db.session()

    try:
        session.add(report)
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()


def get_reports(guild):
    session = bot.db.session()

    sub = session.query(Report, func.count(Report.reportee_id)) \
        .filter(Report.guild_id == guild.id) \
        .group_by(Report.reportee_id) \
        .order_by(func.count(Report.reportee_id).desc()) \
        .all()

    return sub


def get_last_reports(guild, reporting):
    session = bot.db.session()

    return session.query(Report) \
        .filter(Report.guild_id == guild.id) \
        .filter(Report.reporting == reporting) \
        .order_by(Report.time.desc()) \
        .first()


def report_allowed(guild, reporting):
    report = get_last_reports(guild, reporting.name)

    if report is None:
        return None

    diff = datetime.now() - report.time
    if diff.seconds // 60 < 30:
        return 30 - diff.seconds // 60
    else:
        return None