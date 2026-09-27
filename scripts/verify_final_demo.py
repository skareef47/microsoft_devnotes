#!/usr/bin/env python3
"""
ContextIQ — Final Canonical Before/After Verification Script (Phase 5)
Demonstrates:
  Step 1: Authenticate with demo credentials
  Step 2: Memory OFF -> Generic answer, memories_used = []
  Step 3: Memory ON -> Retain statement into Hindsight
  Step 4: New Conversation -> Recall BullMQ memory, memories_used > 0, contextual response
  Step 5: Inspect recalled memory details from Hindsight
  Step 6: Another New Conversation -> Memory persists across sessions
"""

import httpx
import sys

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def run_verification():
    print("==================================================")
    print("CONTEXTIQ CANONICAL BEFORE/AFTER DEMO VERIFICATION")
    print("==================================================")

    # 1. Health Checks
    print("\n[CHECK 1] Verifying System Services...")
    try:
        fe_res = httpx.get(FRONTEND_URL, timeout=5.0)
        be_res = httpx.get(f"{BASE_URL}/api/health", timeout=5.0)
        assert fe_res.status_code == 200, f"Frontend returned {fe_res.status_code}"
        assert be_res.status_code == 200, f"Backend returned {be_res.status_code}"
        be_health = be_res.json()
        print(f"  Frontend: OK (HTTP {fe_res.status_code})")
        print(f"  Backend:  OK ({be_health})")
        assert be_health.get("hindsight") == "ok", "Hindsight memory engine must be healthy"
    except Exception as e:
        print(f"  FAILED: Could not reach services: {e}")
        sys.exit(1)

    # 2. Authentication
    print("\n[CHECK 2] Authenticating Demo Account...")
    client = httpx.Client(base_url=BASE_URL, timeout=10.0)
    auth_res = client.post("/api/auth/login", json={
        "email": "engineer@contextiq.dev",
        "password": "secure_password_123"
    })
    if auth_res.status_code != 200:
        print(f"  FAILED: Login returned {auth_res.status_code}: {auth_res.text}")
        sys.exit(1)
    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/auth/me", headers=headers)
    user_info = me_res.json()
    print(f"  Authenticated as: {user_info['email']} (Team: {user_info['team_id']})")

    # 3. BEFORE MEMORY (Memory OFF)
    print("\n[CHECK 3] BEFORE MEMORY: Query with Memory OFF")
    conv_before = "conv_canonical_before"
    prompt_q = "What queue system should I use for this new email job?"
    res_before = client.post("/api/chat", headers=headers, json={
        "message": prompt_q,
        "conversation_id": conv_before,
        "memory_enabled": False
    })
    assert res_before.status_code == 200, f"Chat failed: {res_before.text}"
    data_before = res_before.json()
    print(f"  Query:               '{prompt_q}'")
    print(f"  Memory Enabled:      {data_before['memory_enabled']}")
    print(f"  Memory Status:       {data_before['memory_status']}")
    print(f"  Memories Recalled:   {len(data_before['memories_used'])}")
    print(f"  Assistant Response:  {data_before['response'][:110]}...")
    assert data_before["memory_enabled"] is False
    assert data_before["memories_used"] == [], "Must NOT recall memories when Memory is OFF"
    assert data_before["memory_status"] == "disabled"
    print("  RESULT: Generic technical answer without team context. [PASSED]")

    # 4. RETAIN (Memory ON)
    print("\n[CHECK 4] RETAIN: Engineering statement with Memory ON")
    conv_retain = "conv_canonical_retain"
    statement = "Our team standardized on BullMQ for background jobs."
    res_retain = client.post("/api/chat", headers=headers, json={
        "message": statement,
        "conversation_id": conv_retain,
        "memory_enabled": True
    })
    assert res_retain.status_code == 200, f"Retain failed: {res_retain.text}"
    data_retain = res_retain.json()
    assert len(data_retain["memories_stored"]) > 0, "Statement must be retained"
    saved_item = data_retain["memories_stored"][0]
    print(f"  Statement:           '{statement}'")
    print(f"  Retain Status:       {saved_item.get('status')}")
    print(f"  Retained Category:   {saved_item.get('category')}")
    print(f"  Hindsight Memory ID: {saved_item.get('id')}")
    assert saved_item.get("status") == "saved"
    print("  RESULT: Statement successfully retained into Hindsight team bank. [PASSED]")

    # 5. AFTER MEMORY (New Conversation + Recall)
    print("\n[CHECK 5] AFTER MEMORY: New Conversation with Memory ON")
    conv_after = "conv_canonical_after"
    res_after = client.post("/api/chat", headers=headers, json={
        "message": prompt_q,
        "conversation_id": conv_after,
        "memory_enabled": True
    })
    assert res_after.status_code == 200, f"Recall failed: {res_after.text}"
    data_after = res_after.json()
    recalled = data_after["memories_used"]
    print(f"  New Conversation ID: {conv_after}")
    print(f"  Query:               '{prompt_q}'")
    print(f"  Memory Enabled:      {data_after['memory_enabled']}")
    print(f"  Memory Status:       {data_after['memory_status']}")
    print(f"  Memories Used:       {len(recalled)}")
    for idx, m in enumerate(recalled, 1):
        print(f"    {idx}. [{m['category'].upper()}] {m['text'][:65]}... (id: {m['id'][:8]})")
    print(f"  Assistant Response:  {data_after['response'][:110]}...")
    assert len(recalled) > 0, "memories_used must be > 0"
    assert any("bullmq" in m["text"].lower() for m in recalled), "BullMQ memory must be recalled"
    assert "bullmq" in data_after["response"].lower(), "Assistant response must use BullMQ context"
    print("  RESULT: Response contextualized using real Hindsight memory. [PASSED]")

    # 6. PERSISTENCE ACROSS CONVERSATIONS
    print("\n[CHECK 6] PERSISTENCE: Second New Conversation")
    conv_persist = "conv_canonical_persist_check"
    res_persist = client.post("/api/chat", headers=headers, json={
        "message": "What was our background job tool decision?",
        "conversation_id": conv_persist,
        "memory_enabled": True
    })
    assert res_persist.status_code == 200
    data_persist = res_persist.json()
    assert len(data_persist["memories_used"]) > 0
    assert any("bullmq" in m["text"].lower() for m in data_persist["memories_used"])
    print(f"  Second Conversation: {conv_persist}")
    print(f"  Memories Recalled:   {len(data_persist['memories_used'])}")
    print("  RESULT: Persistent memory verified across separate conversations. [PASSED]")

    # 7. TEAM MEMORY SIDEBAR / INSPECTION
    print("\n[CHECK 7] Team Memory Listing & Inspection Endpoint")
    mems_res = client.get("/api/memories", headers=headers)
    assert mems_res.status_code == 200
    mems_data = mems_res.json()
    print(f"  Bank ID:             {mems_data['bank_id']}")
    print(f"  Persistent Count:    {mems_data['count']}")
    first_mem = mems_data["memories"][0]
    print(f"  Inspected Memory:    [{first_mem['category'].upper()}] {first_mem['text']}")
    print(f"  Memory UUID:         {first_mem['id']}")
    print(f"  Created At:          {first_mem.get('created_at')}")
    print("  RESULT: Team memory sidebar and inspector data valid. [PASSED]")

    print("\n==================================================")
    print("CANONICAL DEMO PROOF COMPLETED SUCCESSFULLY!")
    print("ContextIQ is proven more useful because it remembers.")
    print("==================================================")

if __name__ == "__main__":
    run_verification()
