import os
import uuid
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager
from typing import Literal, get_args

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
import asyncio
import motor.motor_asyncio
import certifi
from bson.objectid import ObjectId
from pymongo import ASCENDING, DESCENDING, ReturnDocument, UpdateOne

# ─────────────────────── Security ───────────────────────

ADMIN_ACCESS_KEY = os.getenv("ADMIN_KEY")
if not ADMIN_ACCESS_KEY:
    raise RuntimeError("ADMIN_KEY environment variable must be set")

async def verify_admin(x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_ACCESS_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized Access")


# ─────────────────────── Domain Constants ───────────────────────

# The 5 demo zones for the universal command center product
ZoneName = Literal["Main Stage", "Food Court", "Artisan Market", "Cultural Pavilion", "VIP Lounge"]
ZONES: tuple[str, ...] = get_args(ZoneName)

Role = Literal["General", "Early Bird", "VIP", "Organizer", "Sponsor"]

SCAN_ENGAGEMENT_POINTS = 10


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ─────────────────────── Pydantic Models ───────────────────────

class Attendee(BaseModel):
    """Document shape of the `attendees` collection."""
    name: str
    role: Role
    ticket_type: str
    engagement_score: int = 0
    qr_code_hash: str
    registered_at: datetime


class ZoneLog(BaseModel):
    """Document shape of the `zone_logs` collection (one per checkpoint scan)."""
    attendee_id: str
    qr_code_hash: str
    role: Role  # denormalised so zone/role aggregates need no $lookup
    zone_name: ZoneName
    timestamp: datetime  # stored as BSON Date for time-window queries


class NLPQueryRequest(BaseModel):
    query: str


class RegisterAttendeeRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    role: Role
    ticket_type: str = Field(min_length=1, max_length=50)


class ScanRequest(BaseModel):
    qr_code_hash: str = Field(min_length=1)
    zone_name: ZoneName


def serialize(doc: dict) -> dict:
    """Make a Mongo document JSON-safe."""
    doc["_id"] = str(doc["_id"])
    return doc


# ─────────────────────── MongoDB Lifespan ───────────────────────

# Shared with backend/seed.py.
MONGO_URI = os.environ.get("MONGO_URI", "")
DB_NAME = "codex"

db_client: motor.motor_asyncio.AsyncIOMotorClient = None
db = None

def require_db():
    if db is None:
        raise HTTPException(status_code=503, detail="Database not configured")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_client, db
    if MONGO_URI:
        try:
            db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=2000)
            db = db_client[DB_NAME]
            # Verify connection asynchronously so it doesn't block startup if failing
            asyncio.create_task(db_client.admin.command("ping"))
        except Exception as e:
            print(f"Failed to initialize MongoDB client: {e}")
    yield
    if db_client:
        db_client.close()
        print("[--] MongoDB connection closed")


# ─────────────────────── FastAPI App ───────────────────────

app = FastAPI(title="Codex Intelligent Event Command Center", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────── Endpoints ───────────────────────

@app.get("/zones")
async def list_zones():
    """Canonical Codex arena names (used by the field scanner's zone picker)."""
    return {"zones": list(ZONES)}


@app.post("/register_attendee", status_code=201)
async def register_attendee(req: RegisterAttendeeRequest):
    require_db()
    attendee = Attendee(
        name=req.name.strip(),
        role=req.role,
        ticket_type=req.ticket_type.strip(),
        qr_code_hash=uuid.uuid4().hex,
        registered_at=utcnow(),
    )
    doc = attendee.model_dump()
    result = await db.attendees.insert_one(doc)
    doc["_id"] = result.inserted_id

    return {
        "message": "Attendee registered successfully",
        "qr_code_hash": attendee.qr_code_hash,
        "attendee": serialize(doc),
    }


@app.get("/attendee/{qr_code_hash}")
async def get_attendee(qr_code_hash: str):
    require_db()
    attendee = await db.attendees.find_one({"qr_code_hash": qr_code_hash})
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return serialize(attendee)


@app.post("/scan", status_code=201)
async def scan_attendee(req: ScanRequest):
    """Log an attendee checkpoint movement into a Codex zone."""
    # Atomic lookup + engagement bump in a single round trip
    attendee = await db.attendees.find_one_and_update(
        {"qr_code_hash": req.qr_code_hash},
        {"$inc": {"engagement_score": SCAN_ENGAGEMENT_POINTS}},
        return_document=ReturnDocument.AFTER,
    )
    if not attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")

    log = ZoneLog(
        attendee_id=str(attendee["_id"]),
        qr_code_hash=req.qr_code_hash,
        role=attendee["role"],
        zone_name=req.zone_name,
        timestamp=utcnow(),
    )
    log_doc = log.model_dump()
    result = await db.zone_logs.insert_one(log_doc)
    log_doc["_id"] = result.inserted_id

    return {
        "message": f"Scan logged at {req.zone_name}!",
        "attendee": serialize(attendee),
        "zone_log": serialize(log_doc),
    }


# ─────────────────────── Admin endpoints (Protected) ───────────────────────

@app.get("/api/admin/stats", dependencies=[Depends(verify_admin)])
async def admin_get_stats():
    """Returns aggregated zone stats for the HTML dashboard with bottleneck detection."""
    require_db()
    total_attendees = await db.attendees.count_documents({})
    
    eng_cursor = db.attendees.aggregate([{"$group": {"_id": None, "total": {"$sum": "$engagement_score"}}}])
    eng_doc = await eng_cursor.to_list(length=1)
    total_engagement = eng_doc[0]["total"] if eng_doc else 0

    ten_mins_ago = utcnow() - timedelta(minutes=10)
    
    # 1. Get recent scans (last 10 minutes) per zone for Bottleneck Detection
    recent_counts = {}
    async for doc in db.zone_logs.aggregate([
        {"$match": {"timestamp": {"$gte": ten_mins_ago}}},
        {"$group": {"_id": "$zone_name", "count": {"$sum": 1}}}
    ]):
        recent_counts[doc["_id"]] = doc["count"]

    # 2. Get total scans per zone (for overall stats)
    total_counts = {}
    async for doc in db.zone_logs.aggregate([
        {"$group": {"_id": "$zone_name", "count": {"$sum": 1}}}
    ]):
        total_counts[doc["_id"]] = doc["count"]
        
    zones_stats = []
    for zone in ZONES:
        recent = recent_counts.get(zone, 0)
        total = total_counts.get(zone, 0)
        
        # Bottleneck detection: >150 scans in 10 minutes
        capacity_warning = recent > 150
        
        zones_stats.append({
            "zone_name": zone,
            "total_scans": total,
            "recent_scans": recent,
            "capacity_warning": capacity_warning
        })

    # Fetch 20 latest logs for the activity feed, joined with attendee name
    logs = []
    async for log in db.zone_logs.aggregate([
        {"$sort": {"timestamp": DESCENDING}},
        {"$limit": 20},
        {"$addFields": {"aid": {"$toObjectId": "$attendee_id"}}},
        {"$lookup": {"from": "attendees", "localField": "aid", "foreignField": "_id", "as": "a"}},
        {"$unwind": {"path": "$a", "preserveNullAndEmptyArrays": True}}
    ]):
        logs.append({
            "id": str(log["_id"]),
            "zone_name": log.get("zone_name"),
            "timestamp": log.get("timestamp").isoformat() if log.get("timestamp") else None,
            "attendee_name": log.get("a", {}).get("name", "Unknown"),
            "role": log.get("role")
        })
        
    return {
        "zones": zones_stats,
        "recent_logs": logs,
        "total_attendees": total_attendees,
        "total_engagement": total_engagement,
    }


from typing import Optional

class ThrottleZoneRequest(BaseModel):
    zone_name: ZoneName
    target_zone: Optional[ZoneName] = None

    @model_validator(mode='after')
    def check_differ(self):
        if self.target_zone == self.zone_name:
            raise ValueError("target_zone must differ from zone_name")
        return self

@app.post("/api/admin/throttle_zone", dependencies=[Depends(verify_admin)])
async def admin_throttle_zone(req: ThrottleZoneRequest):
    """Simulates diverting crowd flow for a zone by reassigning recent scans to other zones."""
    require_db()
    import random
    
    # 1. Select only recent scans and sort newest-first
    ten_mins_ago = utcnow() - timedelta(minutes=10)
    cursor = db.zone_logs.find(
        {"zone_name": req.zone_name, "timestamp": {"$gte": ten_mins_ago}}
    ).sort("timestamp", DESCENDING).limit(150)
    
    logs_to_move = await cursor.to_list(length=150)
    if not logs_to_move:
        return {"message": f"No active attendees found in {req.zone_name}."}
        
    other_zones = [z for z in ZONES if z != req.zone_name]
    
    # 2. Use bulk_write with UpdateOne
    operations = []
    for log in logs_to_move:
        target_zone = req.target_zone if req.target_zone in ZONES else random.choice(other_zones)
        operations.append(UpdateOne({"_id": log["_id"]}, {"$set": {"zone_name": target_zone}}))
        
    result = await db.zone_logs.bulk_write(operations)
    updates_made = result.modified_count
        
    dest_str = req.target_zone if req.target_zone in ZONES else "other zones"
    return {"message": f"SUCCESS! Diverted {updates_made} attendees from {req.zone_name} to {dest_str}."}


@app.delete("/api/admin/delete_attendee/{attendee_id}", dependencies=[Depends(verify_admin)])
async def admin_delete_attendee(attendee_id: str):
    """Permanently delete an attendee."""
    require_db()
    if not ObjectId.is_valid(attendee_id):
        raise HTTPException(status_code=400, detail="Invalid attendee ID format")
    result = await db.attendees.delete_one({"_id": ObjectId(attendee_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return {"message": "Attendee deleted permanently."}


@app.get("/api/admin/attendees", dependencies=[Depends(verify_admin)])
async def admin_get_attendees():
    """Returns a list of all registered attendees."""
    require_db()
    attendees = []
    async for doc in db.attendees.find().sort("registered_at", DESCENDING):
        attendees.append(serialize(doc))
    return {"attendees": attendees}



@app.post("/api/admin/nlp_query", dependencies=[Depends(verify_admin)])
async def admin_nlp_query(req: NLPQueryRequest):
    """Translates a natural language string into a MongoDB aggregate query."""
    require_db()
    import re
    q = req.query.lower()

    # 1. Extract Roles using simple NLP matching
    roles = []
    for r in get_args(Role):
        # Match word boundaries to prevent "VIP" matching inside a word, etc.
        # Plurals like VIPs or Hackers are handled by optional 's?'
        if re.search(r"\b" + r.lower() + r"s?\b", q):
            roles.append(r)

    # 2. Extract Zones
    zones = []
    for z in ZONES:
        if z.lower() in q:
            zones.append(z)

    # Build the match stage
    match_stage = {}
    if roles:
        match_stage["role"] = {"$in": roles} if len(roles) > 1 else roles[0]
    if zones:
        match_stage["zone_name"] = {"$in": zones} if len(zones) > 1 else zones[0]

    # Assume we're looking for a count of scans if terms match
    # Could expand to look for attendees vs scans based on keywords (e.g. "scans" vs "attendees")
    collection_name = "zone_logs"
    pipeline = []
    if match_stage:
        pipeline.append({"$match": match_stage})

    # Differentiate between unique attendees and total scans
    if "unique" in q or "attendee" in q or "person" in q or "people" in q:
        pipeline.append({"$group": {"_id": "$attendee_id"}})
        pipeline.append({"$count": "result"})
        target = "unique attendees"
    else:
        pipeline.append({"$count": "result"})
        target = "scans"

    cursor = db[collection_name].aggregate(pipeline)
    docs = await cursor.to_list(length=1)
    result_count = docs[0]["result"] if docs else 0

    role_str = " or ".join(roles) if roles else "All roles"
    zone_str = " or ".join(zones) if zones else "All zones"
    answer = f"Found {result_count:,} {target} matching ({role_str} in {zone_str})."

    return {
        "query": req.query,
        "pipeline": pipeline,
        "response": answer,
        "result_count": result_count
    }


@app.post("/api/admin/config", dependencies=[Depends(verify_admin)])
async def admin_config(req: dict):
    global db_client, db
    uri = req.get("mongo_uri")
    if uri:
        from urllib.parse import urlparse
        parsed_uri = urlparse(uri)
        if parsed_uri.hostname != "cluster0.shnt6yi.mongodb.net":
            raise HTTPException(status_code=400, detail="Database connection failed: Host not in allow-list.")
            
        try:
            client = motor.motor_asyncio.AsyncIOMotorClient(uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=2000)
            await client.admin.command("ping")
            old_client = db_client
            db_client = client
            db = db_client[DB_NAME]
            if old_client:
                old_client.close()
            return {"message": "Connected to MongoDB successfully."}
        except Exception:
            raise HTTPException(status_code=400, detail="Database connection failed.")
    return {"message": "No URI provided."}

# ─────────────────────── Static Files (must be last) ───────────────────────

os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
