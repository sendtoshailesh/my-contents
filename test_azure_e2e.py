#!/usr/bin/env python3
"""
End-to-end test for Azure OpenAI integration.
Tests the full workflow: session → outline → approve → framework → content
"""

import json
import time
import urllib.request
import sys

BASE_URL = "http://127.0.0.1:8000"


def post_request(path, payload):
    """Make POST request to API."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_request(path):
    """Make GET request to API."""
    with urllib.request.urlopen(f"{BASE_URL}{path}", timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    """Run end-to-end test."""
    print("=" * 70)
    print("E2E TEST: Azure OpenAI Content Generation")
    print("=" * 70)
    
    # Step 1: Create session
    print("\n[1/5] Creating session...")
    session = post_request("/api/sessions", {
        "topic": "End-to-end Azure OpenAI integration test"
    })
    session_id = session["id"]
    print(f"✓ Session created: {session_id}")
    
    # Step 2: Wait for outline generation (background task)
    print("\n[2/5] Waiting for outline generation...")
    outline = None
    for attempt in range(15):
        time.sleep(2)
        try:
            outline = get_request(f"/api/sessions/{session_id}/outline")
            if outline:
                print(f"✓ Outline generated: {len(outline.get('sections', []))} sections")
                break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"  Attempt {attempt + 1}/15: waiting...")
            else:
                raise
    
    if not outline:
        print("✗ Outline not generated in time")
        sys.exit(1)
    
    # Step 3: Approve outline
    print("\n[3/5] Approving outline...")
    post_request(f"/api/sessions/{session_id}/approve", {"approved": True})
    print("✓ Outline approved")
    
    # Step 4: Select framework
    print("\n[4/5] Selecting framework...")
    framework_result = post_request(
        f"/api/sessions/{session_id}/framework",
        {"visual_opt_in": True}
    )
    framework_choice = framework_result.get("framework_choice")
    print(f"✓ Framework selected: {framework_choice}")
    
    # Step 5: Generate content
    print("\n[5/5] Generating content...")
    content = post_request(
        f"/api/sessions/{session_id}/content",
        {
            "framework_choice": framework_choice,
            "include_code": False
        }
    )
    content_length = len(content.get("body_text", ""))
    print(f"✓ Content generated: {content_length} characters")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ E2E TEST PASSED")
    print("=" * 70)
    print(f"\nSession ID: {session_id}")
    print(f"Outline: {outline['id']}")
    print(f"Content: {content['id']}")
    print(f"Framework: {framework_choice}")
    print(f"Content length: {content_length} chars")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n✗ E2E TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
