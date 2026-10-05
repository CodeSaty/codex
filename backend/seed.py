"""
Codex 3.0 data seeder.

Floods MongoDB Atlas (db `codex`) with mock attendees and 5,000 ZoneLogs spread
across the 5 Codex arenas. It also plants a crowd surge in one zone during the
last 10 minutes so Task 4's bottleneck detection (>150 scans / 10 min) can be demoed.

Run from the repo root:
    .\\venv\\Scripts\\python.exe -m backend.seed             # replace the previous seed batch
    .\\venv\\Scripts\\python.exe -m backend.seed --append    # keep previous batch, add more
    .\\venv\\Scripts\\python.exe -m backend.seed --hotspot none
Options: --attendees N  --logs N  --hours H  --hotspot ZONE|none  --hotspot-scans N  --seed N

Safety: every document written here carries `seeded: True`. Re-seeding deletes ONLY
documents with that flag; real registrations and scans are never touched.

NOTE: timestamps are relative to "now". The planted surge ages out of the 10-minute
window, so re-run this right before demoing the bottleneck alert.
"""
import argparse
import os
import random
import sys
import time
import uuid
from collections import Counter
from datetime import timedelta

# Allow both `python -m backend.seed` and `python backend/seed.py`; keep cwd at the
# repo root so importing backend.main doesn't create a stray static/ folder.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO_ROOT)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import certifi
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING

from backend.main import (
    MONGO_URI, DB_NAME, ZONES, SCAN_ENGAGEMENT_POINTS, Attendee, ZoneLog, utcnow,
)

SEED_FILTER = {"seeded": True}
BOTTLENECK_THRESHOLD = 150  # mirrors the Task 4 rule; used only for the summary printout
BATCH = 1000

# ─────────────── Realistic distributions ───────────────

ROLE_MIX = {"General": 0.60, "Early Bird": 0.25, "Organizer": 0.10, "VIP": 0.05}

TICKETS = {
    "General": ["Standard", "Student", "Last Minute"],
    "Early Bird": ["Early Bird Std", "Early Bird Student"],
    "VIP": ["Platinum", "Investor", "Speaker"],
    "Organizer": ["Staff", "Volunteer"],
}

# Relative zone preference per role -> gives the NLP endpoint (Task 5) meaningful answers
ZONE_AFFINITY = {
    "General":    {"Main Stage": 2, "Food Court": 2, "Artisan Market": 2, "Cultural Pavilion": 5, "VIP Lounge": 1},
    "Early Bird": {"Main Stage": 2, "Food Court": 2, "Artisan Market": 2, "Cultural Pavilion": 5, "VIP Lounge": 1},
    "VIP":       {"Main Stage": 4, "Food Court": 3, "Artisan Market": 1, "Cultural Pavilion": 1, "VIP Lounge": 5},
    "Organizer": {"Main Stage": 1, "Food Court": 1, "Artisan Market": 1, "Cultural Pavilion": 1, "VIP Lounge": 1},
}
for _role, _aff in ZONE_AFFINITY.items():
    assert set(_aff) == set(ZONES), f"ZONE_AFFINITY[{_role}] out of sync with main.ZONES"

FIRST = ["Aarav", "Vivaan", "Aditya", "Arjun", "Sai", "Reyansh", "Krishna", "Ishaan", "Rohan", "Kabir",
         "Ananya", "Diya", "Saanvi", "Aadhya", "Priya", "Isha", "Meera", "Riya", "Sneha", "Kavya",
         "Rahul", "Neha", "Vikram", "Pooja", "Karan", "Tanvi", "Dev", "Nisha", "Sameer", "Aisha"]
LAST = ["Sharma", "Verma", "Gupta", "Patel", "Reddy", "Iyer", "Nair", "Singh", "Kumar", "Das",
        "Mehta", "Joshi", "Rao", "Chopra", "Bose", "Malhotra", "Kapoor", "Menon", "Pillai", "Agarwal"]


# ─────────────── Builders ───────────────

def build_attendees(rng: random.Random, n: int, now) -> list[dict]:
    roles = rng.choices(list(ROLE_MIX), weights=list(ROLE_MIX.values()), k=n)
    docs = []
    for role in roles:
        attendee = Attendee(
            name=f"{rng.choice(FIRST)} {rng.choice(LAST)}",
            role=role,
            ticket_type=rng.choice(TICKETS[role]),
            qr_code_hash=uuid.uuid4().hex,  # uuid4 (not rng) so --append never collides on the unique index
            registered_at=now - timedelta(hours=rng.uniform(6, 72)),
        )
        doc = attendee.model_dump()
        doc["_id"] = ObjectId()
        doc.update(SEED_FILTER)
        docs.append(doc)
    return docs


def make_log(attendee: dict, zone: str, ts) -> dict:
    doc = ZoneLog(
        attendee_id=str(attendee["_id"]),
        qr_code_hash=attendee["qr_code_hash"],
        role=attendee["role"],
        zone_name=zone,
        timestamp=ts,
    ).model_dump()
    doc.update(SEED_FILTER)
    return doc


def build_logs(rng, attendees, n_logs, now, hours, hotspot, hotspot_scans) -> list[dict]:
    # Some attendees roam a lot, most move a little (exponential activity)
    activity = [rng.expovariate(1.0) for _ in attendees]
    n_background = n_logs - hotspot_scans
    window_s = hours * 3600

    logs = []
    for a in rng.choices(attendees, weights=activity, k=n_background):
        aff = ZONE_AFFINITY[a["role"]]
        zone = rng.choices(ZONES, weights=[aff[z] for z in ZONES])[0]
        ts = now - timedelta(seconds=rng.uniform(0, window_s))
        logs.append(make_log(a, zone, ts))

    # Planted surge: kept inside [now-9.5min, now-5s] so it sits safely in the 10-min window
    if hotspot:
        for a in rng.choices(attendees, k=hotspot_scans):
            ts = now - timedelta(seconds=rng.uniform(5, 570))
            logs.append(make_log(a, hotspot, ts))

    logs.sort(key=lambda d: d["timestamp"])  # chronological insert -> natural _id order
    return logs


def insert_batched(coll, docs):
    for i in range(0, len(docs), BATCH):
        coll.insert_many(docs[i:i + BATCH], ordered=False)


# ─────────────── Main ───────────────

def main():
    p = argparse.ArgumentParser(description="Seed Codex 3.0 mock data into MongoDB Atlas.")
    p.add_argument("--attendees", type=int, default=5000, help="mock attendees (default 5000)")
    p.add_argument("--logs", type=int, default=5000, help="total mock ZoneLogs (default 5000)")
    p.add_argument("--hours", type=float, default=4.0, help="history window for background scans")
    p.add_argument("--hotspot", default="Cultural Pavilion", choices=[*ZONES, "none"],
                   help="zone to surge in the last 10 min (or 'none')")
    p.add_argument("--hotspot-scans", type=int, default=180, help="surge size (default 180 > 150 threshold)")
    p.add_argument("--seed", type=int, default=None, help="RNG seed for reproducible distributions")
    p.add_argument("--append", action="store_true", help="keep the previous seed batch instead of replacing it")
    args = p.parse_args()

    hotspot = None if args.hotspot == "none" else args.hotspot
    hotspot_scans = args.hotspot_scans if hotspot else 0
    if args.attendees < 1 or args.logs < 1:
        p.error("--attendees and --logs must be >= 1")
    if hotspot_scans > args.logs:
        p.error("--hotspot-scans cannot exceed --logs")

    rng = random.Random(args.seed)
    t0 = time.perf_counter()

    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    client.admin.command("ping")
    db = client[DB_NAME]
    print(f"[OK] Connected to MongoDB Atlas - {DB_NAME}")

    # Same indexes main.py creates on startup (idempotent) so seeding works before first boot
    db.attendees.create_index("qr_code_hash", unique=True)
    db.zone_logs.create_index([("zone_name", ASCENDING), ("timestamp", DESCENDING)])
    db.zone_logs.create_index([("timestamp", DESCENDING)])

    if not args.append:
        da = db.attendees.delete_many(SEED_FILTER).deleted_count
        dl = db.zone_logs.delete_many(SEED_FILTER).deleted_count
        print(f"[--] Removed previous seed batch: {da} attendees, {dl} zone_logs (real data untouched)")

    now = utcnow()
    attendees = build_attendees(rng, args.attendees, now)
    logs = build_logs(rng, attendees, args.logs, now, args.hours, hotspot, hotspot_scans)

    # engagement_score must agree with what POST /scan would have produced
    scans_per_attendee = Counter(l["attendee_id"] for l in logs)
    for a in attendees:
        a["engagement_score"] = scans_per_attendee[str(a["_id"])] * SCAN_ENGAGEMENT_POINTS

    insert_batched(db.attendees, attendees)
    insert_batched(db.zone_logs, logs)
    print(f"[OK] Inserted {len(attendees)} attendees and {len(logs)} zone_logs "
          f"in {time.perf_counter() - t0:.1f}s")

    # ── Summary, read back from Atlas (proves the round trip) ──
    roles = Counter(a["role"] for a in attendees)
    print("\nRoles: " + ", ".join(f"{r}={roles[r]}" for r in ROLE_MIX))

    totals = {d["_id"]: d["n"] for d in db.zone_logs.aggregate([
        {"$match": SEED_FILTER}, {"$group": {"_id": "$zone_name", "n": {"$sum": 1}}}])}
    recent = {d["_id"]: d["n"] for d in db.zone_logs.aggregate([
        {"$match": {"timestamp": {"$gte": utcnow() - timedelta(minutes=10)}}},
        {"$group": {"_id": "$zone_name", "n": {"$sum": 1}}}])}

    print(f"\n{'Zone':<18}{'seeded total':>13}{'last 10 min':>13}")
    for z in ZONES:
        flag = "  <-- BOTTLENECK" if recent.get(z, 0) > BOTTLENECK_THRESHOLD else ""
        print(f"{z:<18}{totals.get(z, 0):>13}{recent.get(z, 0):>13}{flag}")

    vip_hack = db.zone_logs.count_documents({**SEED_FILTER, "role": "VIP", "zone_name": "Cultural Pavilion"})
    print(f"\nSample NLP answer - VIP scans in Cultural Pavilion: {vip_hack}")
    client.close()


if __name__ == "__main__":
    main()
