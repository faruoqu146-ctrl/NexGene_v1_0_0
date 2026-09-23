#!/usr/bin/env python3
"""Concurrent live stress against a running NexGene API."""
from __future__ import annotations

import argparse
import statistics
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx


def wait_for(base: str, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = httpx.get(f"{base}/api/v1/health", timeout=1.5)
            if r.status_code == 200:
                return
        except Exception:
            time.sleep(0.2)
    raise SystemExit(f"API not reachable at {base}")


def timed_get(client: httpx.Client, path: str) -> tuple[int, float]:
    t0 = time.perf_counter()
    r = client.get(path)
    return r.status_code, (time.perf_counter() - t0) * 1000


def user_journey(base: str, idx: int) -> dict:
    email = f"stress-{idx}@example.com"
    password = "A_secure_password!9"
    with httpx.Client(base_url=base, timeout=20.0) as c:
        t0 = time.perf_counter()
        statuses = []
        r = c.post("/api/v1/auth/register", json={"email": email, "password": password})
        statuses.append(("register", r.status_code))
        csrf = r.cookies.get("nexgene_csrf")
        if not csrf:
            r = c.post("/api/v1/auth/login", json={"email": email, "password": password})
            statuses.append(("login", r.status_code))
            csrf = r.cookies.get("nexgene_csrf")
        headers = {"X-CSRF-Token": csrf} if csrf else {}
        r = c.put(
            "/api/v1/profile",
            json={"country": "Nigeria", "occupation": "Engineer", "student": False},
            headers=headers,
        )
        statuses.append(("profile", r.status_code))
        for i in range(6):
            r = c.post(
                "/api/v1/checkins/morning",
                json={"values": {"energy": 5 + (i % 5), "sleep_duration": 7.0}},
                headers=headers,
            )
            statuses.append(("checkin", r.status_code))
        for path in ("/api/v1/reports/weekly", "/api/v1/signals", "/api/v1/patterns", "/api/v1/auth/me"):
            r = c.get(path)
            statuses.append((path.rsplit("/", 1)[-1], r.status_code))
        return {
            "idx": idx,
            "ms": (time.perf_counter() - t0) * 1000,
            "ok": all(code in (200, 409) for _, code in statuses),
            "statuses": statuses,
        }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base", default="http://127.0.0.1:8000")
    p.add_argument("--users", type=int, default=20)
    p.add_argument("--gets", type=int, default=80)
    args = p.parse_args()
    wait_for(args.base)
    print(f"target {args.base}")
    with httpx.Client(base_url=args.base, timeout=10.0) as c:
        latencies, codes = [], []
        for _ in range(args.gets):
            code, ms = timed_get(c, "/")
            codes.append(code)
            latencies.append(ms)
        print("GET / x%d  codes=%s  min=%.1fms p50=%.1fms p95=%.1fms max=%.1fms" % (args.gets, dict(Counter(codes)), min(latencies), statistics.median(latencies), sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)], max(latencies)))
    results = []
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=min(args.users, 16)) as pool:
        futs = [pool.submit(user_journey, args.base, i) for i in range(args.users)]
        for fut in as_completed(futs):
            results.append(fut.result())
    wall = time.perf_counter() - t0
    ok = sum(1 for r in results if r["ok"])
    times = [r["ms"] for r in results]
    print("journeys %d/%d ok in %.2fs  min=%.0fms p50=%.0fms max=%.0fms" % (ok, len(results), wall, min(times), statistics.median(times), max(times)))
    fails = [r for r in results if not r["ok"]]
    if fails:
        print("failures:")
        for r in fails[:8]:
            print(" ", r["idx"], r["statuses"])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
