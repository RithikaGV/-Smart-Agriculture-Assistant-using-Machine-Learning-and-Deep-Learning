#!/usr/bin/env python3
"""Export POLY HOUSE sensor data from the cloud server's MySQL to CSV.

Usage (run from any machine that can reach the server's MySQL):

  py -m pip install pymysql

  # 1) See what the payload looks like (do this first)
  py export_data.py --host 192.168.29.106 --inspect

  # 2) Export everything to CSV
  py export_data.py --host 192.168.29.106 --out polyhouse_data.csv

  # Only latest snapshot via the HTTP API (no MySQL access needed)
  py export_data.py --host 192.168.29.106 --latest-http

Options:
  --host      server IP (default: from mysql_config.json, else 127.0.0.1)
  --config    path to mysql_config.json (default: next to this script)
  --limit     max rows (newest first, then re-sorted oldest->newest)
  --since     only rows created on/after this date, e.g. 2026-09-28
  --device    only this device_id (e.g. PH-1)
"""
import os
import sys
import csv
import json
import argparse
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))


def load_cfg(path):
    cfg = {"host": "127.0.0.1", "port": 3306, "user": "root",
           "password": "", "database": "polyhouse", "http_port": 50503}
    if os.path.exists(path):
        with open(path) as f:
            cfg.update(json.load(f))
    return cfg


def flat(obj):
    """Cleaner recursive flatten with explicit key paths."""
    res = {}

    def rec(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                rec(v, f"{path}.{k}" if path else str(k))
        elif isinstance(o, list):
            for i, item in enumerate(o):
                label = item.get("name") if isinstance(item, dict) and item.get("name") else i
                rec(item, f"{path}.{label}" if path else str(label))
        else:
            res[path] = o

    rec(obj, "")
    return res


def parse_payload(raw):
    if raw is None:
        return {}
    if isinstance(raw, (dict, list)):
        return raw
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", "replace")
    try:
        return json.loads(raw)
    except Exception:
        return {"raw": str(raw)}


def fetch_rows(args, cfg):
    import pymysql
    conn = pymysql.connect(host=args.host or cfg["host"], port=int(cfg["port"]),
                           user=cfg["user"], password=cfg["password"],
                           database=cfg["database"], charset="utf8mb4",
                           connect_timeout=8)
    where, params = [], []
    if args.since:
        where.append("created_at >= %s"); params.append(args.since)
    if args.device:
        where.append("device_id = %s"); params.append(args.device)
    sql = "SELECT id, device_id, customer_id, ts, created_at, payload FROM device_data"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY id DESC"
    if args.limit:
        sql += f" LIMIT {int(args.limit)}"
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()
    return list(reversed(rows))  # oldest -> newest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host")
    ap.add_argument("--config", default=os.path.join(BASE, "mysql_config.json"))
    ap.add_argument("--out", default="polyhouse_data.csv")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--since")
    ap.add_argument("--device")
    ap.add_argument("--inspect", action="store_true", help="print latest payload and exit")
    ap.add_argument("--latest-http", action="store_true", help="fetch latest via /api/status")
    args = ap.parse_args()
    cfg = load_cfg(args.config)

    if args.latest_http:
        url = f"http://{args.host or cfg['host']}:{cfg['http_port']}/api/status"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.load(r).get("latest") or {}
        print(json.dumps(data, indent=2))
        f = flat(data)
        with open(args.out, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=list(f.keys()))
            w.writeheader(); w.writerow(f)
        print(f"\nSaved 1 row -> {args.out}")
        return

    if args.inspect:
        args.limit = 1
    try:
        rows = fetch_rows(args, cfg)
    except ImportError:
        sys.exit("pymysql missing. Run:  py -m pip install pymysql")
    except Exception as e:
        sys.exit(f"MySQL error: {e}\n"
                 "-> Check host/password, that MySQL80 is running, and that the\n"
                 "   MySQL user is allowed to connect from your machine (see notes).")

    if not rows:
        sys.exit("No rows in device_data (device may not have uploaded yet).")

    if args.inspect:
        _id, dev, cust, ts, created, raw = rows[0]
        print(f"id={_id} device={dev} customer={cust} ts={ts} created_at={created}")
        print(json.dumps(parse_payload(raw), indent=2, default=str))
        print("\nFlattened columns:")
        for k in flat(parse_payload(raw)):
            print("  ", k)
        return

    records, cols = [], []
    for _id, dev, cust, ts, created, raw in rows:
        rec = {"id": _id, "device_id": dev, "customer_id": cust,
               "ts": ts, "created_at": created}
        rec.update(flat(parse_payload(raw)))
        records.append(rec)
        for k in rec:
            if k not in cols:
                cols.append(k)

    with open(args.out, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(records)
    print(f"Saved {len(records)} rows, {len(cols)} columns -> {args.out}")


if __name__ == "__main__":
    main()
