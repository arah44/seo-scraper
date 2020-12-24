import datetime

class TimerWrapper(f):
    start = datetime.datetime.now()
    print(f"Timing {f}")
    r = f(*args, **kwargs)
    end = datetime.datetime.now()
    print(f"Finished in {end-start}")
    return r