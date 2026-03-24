def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02}:{s:02}"