# Chrome DevTools Testing Guide - Flow Scanner

## Setup

1. **Open Dashboard in Chrome:**
   - Navigate to: http://localhost:8501
   - Press `F12` or `Cmd+Option+I` to open DevTools

2. **Recommended DevTools Layout:**
   - Dock DevTools to right side
   - Open these tabs: Console, Network, Elements

---

## Test 1: Page Load & Initial Errors

### Chrome DevTools - Console Tab

**What to check:**
- [ ] No red errors on page load
- [ ] No warnings about missing modules
- [ ] WebSocket connection established (look for "WebSocket opened")

**Expected output:**
```
Streamlit is connected
WebSocket opened: ws://localhost:8501/_stcore/stream
```

**Red flags:**
- ❌ `ReferenceError: X is not defined`
- ❌ `Failed to load resource: net::ERR_CONNECTION_REFUSED`
- ❌ CORS errors
- ❌ 404 errors for missing resources

---

## Test 2: Navigate to Flow Scanner Tab

### Actions:
1. Navigate to "📊 Advanced Analytics" page (left sidebar)
2. Click on "⚡ Real-Time Flow" tab

### Chrome DevTools - Console Tab

**What to check:**
- [ ] No errors when tab loads
- [ ] No Python exceptions displayed in red error boxes

**Expected behavior:**
- Tab loads smoothly
- UI elements render correctly
- No error messages in Streamlit

**Red flags:**
- ❌ `RuntimeError: There is no current event loop`
- ❌ `ModuleNotFoundError: No module named 'ib_insync'`
- ❌ `AttributeError` or `TypeError` exceptions

---

## Test 3: IB Connection

### Actions:
1. Scroll to sidebar
2. Expand "Connect to IB Gateway/TWS"
3. Verify settings:
   - Host: 127.0.0.1
   - Port: 4001
   - Client ID: 3
4. Click "Connect"

### Chrome DevTools - Console Tab

**What to check:**
- [ ] No JavaScript errors during connection attempt
- [ ] Streamlit rerun triggered (page refreshes)

### Chrome DevTools - Network Tab

**What to check:**
- [ ] XHR requests to `/_stcore/stream` show status 200
- [ ] WebSocket frames show data being sent/received
- [ ] No 500 Internal Server Error responses

**Expected Streamlit output:**
```
✅ Connected to IB (Live)
```

**Red flags:**
- ❌ "Connection failed" error message
- ❌ Network requests timing out
- ❌ 500 errors in Network tab

---

## Test 4: Run Flow Scanner

### Actions:
1. Enter ticker: **SPY**
2. Click "🔍 Scan SPY Flow Now"

### Chrome DevTools - Console Tab

**What to monitor in real-time:**
- [ ] Spinner shows: "Scanning SPY options flow..."
- [ ] No red error messages appear
- [ ] No uncaught exceptions

### Chrome DevTools - Network Tab

**What to check:**
- [ ] Continuous XHR requests to `/_stcore/stream`
- [ ] Response times < 500ms for most requests
- [ ] Status codes all 200 (no 500/502/503)

### Server-Side Progress (see terminal)

**Expected console output:**
```
============================================================
🔍 Scanning Options Flow for SPY
============================================================

💰 Using close price: $671.76 (market closed)
📊 Found 34 expirations on NASDAQOM

📅 Scanning expiration 1/2: 20251027
   Analyzing 25 strikes near ATM (~50 total options)
   ⏱️  Progress: 10/50 options (20%) - ETA: 45s
   ⏱️  Progress: 20/50 options (40%) - ETA: 28s
   ⏱️  Progress: 30/50 options (60%) - ETA: 15s
   🎯 BLOCK: C 645.0 - 150 contracts
   ⏱️  Progress: 40/50 options (80%) - ETA: 8s

📅 Scanning expiration 2/2: 20251028
   Analyzing 25 strikes near ATM (~50 total options)
   ⏱️  Progress: 50/100 options (50%) - ETA: 30s

⏱️  Scan completed in 62.3 seconds (98 options scanned)

============================================================
📊 FLOW ANALYSIS SUMMARY: SPY
============================================================
```

### Streamlit UI - Expected Results

After scan completes:

**Success message:**
```
✅ Scan complete!
```

**Results displayed:**
- Flow alerts (if any)
- Block trades count
- Sweeps count
- Aggressive buys count
- Premium flow statistics

**Red flags:**
- ❌ Spinner runs > 3 minutes without progress
- ❌ Error message: "⚠️ IB connection required"
- ❌ Red error box with Python traceback
- ❌ Page becomes unresponsive
- ❌ Console shows: `sqlite3.OperationalError`

---

## Test 5: Background Monitor (Optional)

### Actions:
1. Scroll down to "Background Monitor Control Panel"
2. Enter watchlist: **SPY AAPL TSLA**
3. Set scan interval: **300** seconds
4. Click "Start Monitoring"

### Chrome DevTools - Console Tab

**What to check:**
- [ ] Status changes to: "🟢 Monitoring active"
- [ ] No errors about threading or asyncio

### Chrome DevTools - Network Tab

**What to monitor:**
- [ ] Periodic updates every 5 seconds (Streamlit auto-refresh)
- [ ] No memory leaks (check Performance tab if concerned)

**Expected behavior:**
- Background thread starts
- Status widget updates
- Scanner runs every 5 minutes

**Red flags:**
- ❌ "Failed to start monitor" error
- ❌ Status stuck on "Starting..."
- ❌ Memory usage climbing rapidly (Performance tab)

---

## Common Issues & Solutions

### Issue: Event Loop Error
**Console shows:**
```
RuntimeError: There is no current event loop in thread 'ScriptRunner.scriptThread'
```

**Solution:** Already fixed in latest code. If you see this:
1. Refresh page (Cmd+R)
2. Check Streamlit server was restarted after code changes

---

### Issue: IB Connection Fails
**UI shows:**
```
❌ Connection failed: Connection refused
```

**Checks:**
1. IB Gateway running? (Check Activity Monitor for "ibgateway")
2. Port correct? (4001 for live, 7497 for paper TWS)
3. API enabled in IB Gateway settings?

---

### Issue: Scan Takes Too Long
**Spinner runs > 5 minutes**

**Checks in Chrome DevTools Console:**
- Look for: "⏱️ Progress: X/Y options"
- If no progress updates: Server may be hung
- Check Network tab for stalled requests

**Solutions:**
1. Cancel scan (refresh page)
2. Check terminal for rate limit messages
3. Try ticker with fewer options (e.g., "KO" instead of "SPY")

---

## Performance Metrics

### Good Performance:
- ✅ Page load: < 2 seconds
- ✅ Tab switch: < 1 second
- ✅ IB connection: < 3 seconds
- ✅ Flow scan: 60-120 seconds (after hours)
- ✅ Flow scan: 30-60 seconds (market hours)

### Poor Performance:
- ⚠️ Page load: > 5 seconds → Check Network tab for slow resources
- ⚠️ Flow scan: > 3 minutes → IB rate limiting or network issues

---

## Success Criteria

**All tests pass if:**
- ✅ No red errors in Console
- ✅ All Network requests return 200
- ✅ IB connection succeeds
- ✅ Flow scan completes with results
- ✅ UI remains responsive throughout

---

## Report Template

If you find issues, report them with:

1. **Console errors** (copy full stack trace)
2. **Network tab** (screenshot of failed request)
3. **Streamlit error message** (screenshot of red error box)
4. **Server terminal output** (last 50 lines)

---

## Live Monitoring

**I'm currently monitoring:** `/tmp/streamlit.log`

**To test:**
1. Open http://localhost:8501 in Chrome
2. Open DevTools (F12)
3. Follow tests 1-4 above
4. Report any errors you see

I'll watch the server logs and provide real-time feedback!
