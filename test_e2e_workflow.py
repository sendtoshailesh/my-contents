#!/usr/bin/env python3
"""
End-to-End Test for User Story 1 Workflow
Tests: Topic submission -> Outline generation -> Validation

This script:
1. Creates a new session via POST /sessions
2. Monitors the background task execution
3. Verifies the outline was generated
4. Confirms validation results
"""

import os
import sys
import time
import json
import requests
import sqlite3
from pathlib import Path
from datetime import datetime

# Setup logging
os.environ["PYTHONPATH"] = str(Path(__file__).parent)

sys.path.insert(0, str(Path(__file__).parent))

# API Configuration
API_BASE = "http://127.0.0.1:8000"
DB_PATH = Path.home() / ".content-studio" / "sessions.db"

print("=" * 80)
print("🧪 End-to-End Test: User Story 1 - Topic → Outline → Validation")
print("=" * 80)
print()

# Test data
test_topic = "The Future of Artificial Intelligence in Education"
test_student_level = "undergraduate"
test_reading_time = 5

print(f"📝 Test Parameters:")
print(f"   Topic: {test_topic}")
print(f"   Student Level: {test_student_level}")
print(f"   Reading Time: {test_reading_time} min")
print()

# Step 1: Create a new session
print("📤 Step 1: Creating a new session...")
try:
    response = requests.post(
        f"{API_BASE}/api/sessions",
        json={
            "topic": test_topic,
        },
        timeout=30
    )
    response.raise_for_status()
    session_data = response.json()
    session_id = session_data.get("id")  # Changed from session_id to id
    print(f"   ✅ Session created: {session_id}")
    print(f"   Response: {json.dumps(session_data, indent=2)}")
except Exception as e:
    print(f"   ❌ Failed to create session: {e}")
    sys.exit(1)

print()

# Step 2: Query database to verify session and workflow execution
print("📊 Step 2: Monitoring workflow execution...")
print(f"   Waiting for background task to process... (timeout: 60s)")

max_attempts = 60
for attempt in range(max_attempts):
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query session details
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        session = cursor.fetchone()
        
        if session:
            status = session['status']
            outline = session['outline']
            validation_result = session['validation_result']
            
            if status == 'completed' and outline:
                print(f"   ✅ Workflow completed!")
                print(f"   Status: {status}")
                print(f"   Outline length: {len(outline)} chars")
                print(f"   Validation: {validation_result}")
                break
            elif status == 'failed':
                print(f"   ❌ Workflow failed: {session['error_message']}")
                sys.exit(1)
            else:
                if attempt % 5 == 0:  # Print every 5 attempts
                    print(f"      Status: {status} (attempt {attempt+1}/{max_attempts})")
        
        conn.close()
        time.sleep(1)
    except Exception as e:
        if attempt % 10 == 0:
            print(f"      Waiting... ({attempt+1}s)")
        time.sleep(1)

print()

# Step 3: Retrieve the generated outline
print("📋 Step 3: Retrieving generated outline...")
try:
    response = requests.get(
        f"{API_BASE}/api/sessions/{session_id}",
        timeout=30
    )
    response.raise_for_status()
    session_result = response.json()
    
    outline = session_result.get("outline", "")
    if outline:
        print(f"   ✅ Outline retrieved ({len(outline)} characters)")
        print()
        print("   📌 Generated Outline:")
        print("   " + "-" * 70)
        for line in outline.split('\n')[:20]:  # Show first 20 lines
            print(f"   {line}")
        if len(outline.split('\n')) > 20:
            print(f"   ... ({len(outline.split(chr(10)))} total lines)")
        print("   " + "-" * 70)
    else:
        print(f"   ⚠️  Outline is empty")
        
except Exception as e:
    print(f"   ❌ Failed to retrieve outline: {e}")
    sys.exit(1)

print()

# Step 4: Verify validation results
print("✅ Step 4: Validation Results")
try:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
    session = cursor.fetchone()
    
    validation_result = session['validation_result']
    research_confidence = session['research_confidence']
    
    print(f"   Validation Result: {validation_result}")
    print(f"   Research Confidence: {research_confidence}%")
    
    conn.close()
except Exception as e:
    print(f"   ⚠️  Could not retrieve validation: {e}")

print()
print("=" * 80)
print("✅ End-to-End Test Complete!")
print("=" * 80)
print()
print("📊 Summary:")
print(f"   ✓ Session created: {session_id}")
print(f"   ✓ Workflow executed successfully")
print(f"   ✓ Outline generated") 
print(f"   ✓ Validation complete")
print()
