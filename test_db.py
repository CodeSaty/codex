import os
import asyncio
import motor.motor_asyncio
import certifi

async def run():
  mongo_uri = os.getenv("MONGO_URI")
  if not mongo_uri:
      print("MONGO_URI environment variable is not set.")
      import sys
      sys.exit(1)
  client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri, tlsCAFile=certifi.where())
  try:
    print(await client.admin.command('ping'))
  except Exception as e:
    print(e)
    import sys
    sys.exit(1)
asyncio.run(run())
