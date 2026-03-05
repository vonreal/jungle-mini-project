from datetime import datetime, timezone, timedelta

# 한국 타임라인 설정
KST = timezone(timedelta(hours=9))

def display_time(target):
    result = ""
    now = get_now()
    diff = now - target

    if (seconds := diff.total_seconds()) < 60:
        result = '방금 전'
    elif (minutes := round(seconds/60)) < 60:
        result = f'{minutes}분 전'
    elif (hours := round(minutes/60)) < 24:
        result = f'{hours}시간 전'
    elif diff.days < 7:
        result = f'{diff.days}일 전'
    else:
        result = target.strftime('%Y-%m-%d')

    return result

def get_now():
    return datetime.now(KST).replace(tzinfo=None)

def convert_datetime(date):
    return datetime.fromisoformat(date)