# Mock Test Execution Data - Documentation

## Overview

This folder contains **5,000 test executions** across **50 unique tests** with **8 embedded flaky patterns**.

The data is realistic and representative of what you'd see in a production test suite.

## File: `testneo_test_executions.csv`

### Schema

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `execution_id` | int | Unique execution ID | 1, 2, 3... |
| `test_case_id` | int | Test case ID (1-50) | 15 |
| `test_name` | string | Human-readable test name | `test_checkout_payment` |
| `status` | string | Execution result | `pass` or `fail` |
| `executed_at` | datetime | Execution timestamp | `2026-01-15 14:23:45` |
| `duration_ms` | int | Test duration in milliseconds | 1250 |
| `error_message` | string | Error message (if failed) | `Timeout after 3000ms` |
| `error_type` | string | Error category | `timeout`, `network`, `assertion` |
| `environment` | string | Test environment | `staging`, `production` |
| `browser` | string | Browser (web tests only) | `chrome`, `firefox`, `safari` |
| `build_version` | string | Build/release version | `v1.2.3` |

### Sample Row

```csv
execution_id,test_case_id,test_name,status,executed_at,duration_ms,error_message,error_type,environment,browser,build_version
1,15,test_checkout_payment,fail,2026-01-15 14:23:45,3200,Timeout after 3000ms,timeout,staging,chrome,v1.2.3
```

## Embedded Flaky Patterns

The dataset contains **8 realistic flaky test patterns**:

### 1. Timeout Flakiness (10 tests)
- **Pattern**: Random timeouts (20% failure rate)
- **Test IDs**: 1-10
- **Error**: "Timeout after 3000ms"
- **Root Cause**: TIMING
- **Fix**: Increase timeout threshold

### 2. Network Flakiness (8 tests)
- **Pattern**: Connection issues (15% failure rate)
- **Test IDs**: 11-18
- **Error**: "Connection refused" or "Network error"
- **Root Cause**: ENVIRONMENT
- **Fix**: Add retry logic, check network stability

### 3. Auth Token Expiry (5 tests)
- **Pattern**: Fails after 1 hour of token generation
- **Test IDs**: 19-23
- **Error**: "401 Unauthorized" or "Token expired"
- **Root Cause**: TIMING (auth-related)
- **Fix**: Refresh token before test

### 4. Race Condition (6 tests)
- **Pattern**: Timing-dependent (25% failure rate)
- **Test IDs**: 24-29
- **Error**: "Element not found" or "State mismatch"
- **Root Cause**: TIMING
- **Fix**: Add explicit waits

### 5. Weekend Effect (4 tests)
- **Pattern**: Fails on Saturdays (50% failure rate on Sat, 5% other days)
- **Test IDs**: 30-33
- **Error**: "Service unavailable"
- **Root Cause**: INFRASTRUCTURE (scheduled maintenance)
- **Fix**: Skip tests on weekends or check service health

### 6. Peak Hour Flakiness (5 tests)
- **Pattern**: Fails during 2-4 PM (40% failure rate during peak, 10% off-peak)
- **Test IDs**: 34-38
- **Error**: "Timeout" or "Slow response"
- **Root Cause**: RESOURCE (contention)
- **Fix**: Increase timeout during peak hours

### 7. Browser-Specific (7 tests)
- **Pattern**: Fails in Safari (30% failure rate), passes in Chrome/Firefox
- **Test IDs**: 39-45
- **Error**: "Element not clickable" or "Selector not found"
- **Root Cause**: BROWSER_SPECIFIC
- **Fix**: Use browser-specific selectors or waits

### 8. Test Order Dependency (5 tests)
- **Pattern**: Fails when run after test_id=50 (shared state issue)
- **Test IDs**: 46-50
- **Error**: "Assertion failed: expected X, got Y"
- **Root Cause**: TEST_ORDER
- **Fix**: Ensure test isolation, add proper teardown

## Statistics

### Overall Stats
- **Total Executions**: 5,000
- **Unique Tests**: 50
- **Flaky Tests**: 50 (all tests have some flakiness)
- **Overall Pass Rate**: ~75%
- **Date Range**: 2026-01-01 to 2026-03-25 (12 weeks)

### Execution Distribution
- **Per Test**: ~100 executions each
- **Per Day**: ~60 executions
- **Per Hour**: ~2-3 executions

### Environment Distribution
- **Staging**: 60% of executions
- **Production**: 40% of executions

### Browser Distribution (Web Tests)
- **Chrome**: 50%
- **Firefox**: 30%
- **Safari**: 20%

### Error Type Distribution
- **Timeout**: 30%
- **Network**: 20%
- **Auth**: 15%
- **Assertion**: 20%
- **Element Not Found**: 15%

## How to Use This Data

### 1. Load Data

```python
import pandas as pd

df = pd.read_csv('testneo_test_executions.csv')
df['executed_at'] = pd.to_datetime(df['executed_at'])

print(f"Loaded {len(df)} executions")
print(f"Unique tests: {df['test_case_id'].nunique()}")
```

### 2. Identify Flaky Tests

```python
# Group by test
test_stats = df.groupby('test_case_id').agg({
    'status': ['count', lambda x: (x == 'pass').sum(), lambda x: (x == 'fail').sum()]
}).reset_index()

test_stats.columns = ['test_case_id', 'total', 'passes', 'fails']
test_stats['pass_rate'] = test_stats['passes'] / test_stats['total']

# Flaky = has both passes and fails
flaky = test_stats[(test_stats['passes'] > 0) & (test_stats['fails'] > 0)]
print(f"Flaky tests: {len(flaky)}")
```

### 3. Analyze Patterns

```python
# Temporal patterns
df['hour'] = df['executed_at'].dt.hour
df['day_of_week'] = df['executed_at'].dt.dayofweek

# Failures by hour
hourly_failures = df[df['status'] == 'fail'].groupby('hour').size()
print("Failures by hour:")
print(hourly_failures)

# Failures by day of week
daily_failures = df[df['status'] == 'fail'].groupby('day_of_week').size()
print("\nFailures by day of week:")
print(daily_failures)
```

### 4. Analyze Error Messages

```python
# Most common errors
error_counts = df[df['status'] == 'fail']['error_message'].value_counts()
print("Top 10 errors:")
print(error_counts.head(10))
```

## Data Quality

### Validation Checks

Run `verify_mock_data.py` to validate:

```bash
python verify_mock_data.py
```

Expected output:
```
✅ Found testneo_test_executions.csv
✅ 5,000 test executions loaded
✅ 50 unique tests
✅ Date range: 2026-01-01 to 2026-03-25
✅ All required columns present
✅ No missing values in critical columns
✅ 8 flaky patterns detected
✅ Data quality: GOOD
```

### Known Limitations

1. **Simplified Error Messages**: Real error messages are more complex
2. **No Step-Level Data**: Real tests have multiple steps
3. **No Resource Metrics**: Real data includes CPU, memory usage
4. **No Code Changes**: Real data tracks commits affecting tests
5. **Deterministic Patterns**: Real flakiness is more random

These limitations are intentional to keep the dataset manageable for learning.

## Generating More Data

If you need more data, use `generate_mock_flaky_data.py`:

```bash
python generate_mock_flaky_data.py --num_executions 10000 --num_tests 100
```

This will generate a new CSV with your specified parameters.

## Questions?

If you have questions about the data:
1. Check this README first
2. Run `verify_mock_data.py` to validate
3. Ask your mentor

**Happy analyzing! 📊**
