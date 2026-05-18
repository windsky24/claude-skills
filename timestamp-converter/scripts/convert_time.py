# -*- coding: utf-8 -*-
import sys
import datetime

EPOCH = datetime.datetime(1970, 1, 1)
TW_OFFSET = 8


def ts_to_tz(timestamp, utc_offset):
    utc_dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=int(timestamp))
    local_dt = utc_dt + datetime.timedelta(hours=utc_offset)
    sign = "+" if utc_offset >= 0 else "-"
    return "{} (UTC{}{})".format(local_dt.strftime('%Y-%m-%d %H:%M:%S'), sign, abs(utc_offset))


def parse_datetime(dt_str):
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.datetime.strptime(dt_str.strip(), fmt)
        except ValueError:
            continue
    raise ValueError("Cannot parse: {}".format(dt_str))


def tz_to_ts(dt_str, utc_offset):
    local_dt = parse_datetime(dt_str)
    utc_dt = local_dt - datetime.timedelta(hours=utc_offset)
    return int((utc_dt - EPOCH).total_seconds())


def main():
    if len(sys.argv) < 3:
        print("Usage: python convert_time.py <mode> <input> [target_offset]")
        print("mode: ts2tw | tw2ts | ts2tz | tz2ts")
        sys.exit(1)

    mode = sys.argv[1]
    arg = sys.argv[2]

    if mode == "ts2tw":
        print(ts_to_tz(int(arg), TW_OFFSET))

    elif mode == "tw2ts":
        print(tz_to_ts(arg, TW_OFFSET))

    elif mode == "ts2tz":
        if len(sys.argv) < 4:
            print("ts2tz requires target_offset, e.g. 0 (UTC), 9 (UTC+9)")
            sys.exit(1)
        print(ts_to_tz(int(arg), int(sys.argv[3])))

    elif mode == "tz2ts":
        if len(sys.argv) < 4:
            print("tz2ts requires target_offset, e.g. 8 (UTC+8), 9 (UTC+9)")
            sys.exit(1)
        print(tz_to_ts(arg, int(sys.argv[3])))

    else:
        print("Unknown mode: {}".format(mode))
        print("Supported: ts2tw | tw2ts | ts2tz | tz2ts")
        sys.exit(1)


if __name__ == "__main__":
    main()
