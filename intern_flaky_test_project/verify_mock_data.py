"""
Verify mock test execution data quality
"""
import pandas as pd
import sys

def verify_data(filename='testneo_test_executions.csv'):
    """Verify data quality and patterns"""
    
    print("🔍 Verifying mock data...\n")
    
    # Check file exists
    try:
        df = pd.read_csv(filename)
        print(f"✅ Found {filename}")
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        print("   Run: python generate_mock_flaky_data.py")
        return False
    
    # Check row count
    print(f"✅ {len(df):,} test executions loaded")
    
    # Check unique tests
    num_tests = df['test_case_id'].nunique()
    print(f"✅ {num_tests} unique tests")
    
    # Check date range
    df['executed_at'] = pd.to_datetime(df['executed_at'])
    print(f"✅ Date range: {df['executed_at'].min().date()} to {df['executed_at'].max().date()}")
    
    # Check required columns
    required_columns = [
        'execution_id', 'test_case_id', 'test_name', 'status', 'executed_at',
        'duration_ms', 'error_message', 'error_type', 'environment', 'browser', 'build_version'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"❌ Missing columns: {missing_columns}")
        return False
    print(f"✅ All required columns present")
    
    # Check for missing values in critical columns
    critical_columns = ['execution_id', 'test_case_id', 'status', 'executed_at']
    missing_values = df[critical_columns].isnull().sum()
    if missing_values.any():
        print(f"❌ Missing values found:")
        print(missing_values[missing_values > 0])
        return False
    print(f"✅ No missing values in critical columns")
    
    # Identify flaky tests
    test_stats = df.groupby('test_case_id').agg({
        'status': ['count', lambda x: (x == 'pass').sum(), lambda x: (x == 'fail').sum()]
    }).reset_index()
    test_stats.columns = ['test_case_id', 'total', 'passes', 'fails']
    
    flaky_tests = test_stats[(test_stats['passes'] > 0) & (test_stats['fails'] > 0)]
    print(f"✅ {len(flaky_tests)} flaky tests detected (have both passes and fails)")
    
    # Check flaky patterns
    print("\n📊 Flaky Pattern Detection:")
    
    # Pattern 1: Timeout flakiness
    timeout_failures = df[df['error_type'] == 'timeout']
    print(f"  - Timeout failures: {len(timeout_failures)} ({len(timeout_failures)/len(df)*100:.1f}%)")
    
    # Pattern 2: Network flakiness
    network_failures = df[df['error_type'] == 'network']
    print(f"  - Network failures: {len(network_failures)} ({len(network_failures)/len(df)*100:.1f}%)")
    
    # Pattern 3: Auth failures
    auth_failures = df[df['error_type'] == 'auth']
    print(f"  - Auth failures: {len(auth_failures)} ({len(auth_failures)/len(df)*100:.1f}%)")
    
    # Pattern 4: Assertion failures
    assertion_failures = df[df['error_type'] == 'assertion']
    print(f"  - Assertion failures: {len(assertion_failures)} ({len(assertion_failures)/len(df)*100:.1f}%)")
    
    # Pattern 5: Weekend effect
    df['day_of_week'] = df['executed_at'].dt.dayofweek
    saturday_failures = df[(df['day_of_week'] == 5) & (df['status'] == 'fail')]
    saturday_total = df[df['day_of_week'] == 5]
    if len(saturday_total) > 0:
        saturday_fail_rate = len(saturday_failures) / len(saturday_total)
        print(f"  - Saturday failure rate: {saturday_fail_rate:.1%}")
    
    # Pattern 6: Peak hour effect
    df['hour'] = df['executed_at'].dt.hour
    peak_hours = df[(df['hour'] >= 14) & (df['hour'] <= 16)]
    peak_failures = peak_hours[peak_hours['status'] == 'fail']
    if len(peak_hours) > 0:
        peak_fail_rate = len(peak_failures) / len(peak_hours)
        print(f"  - Peak hour (2-4 PM) failure rate: {peak_fail_rate:.1%}")
    
    # Overall statistics
    print("\n📈 Overall Statistics:")
    print(f"  - Total executions: {len(df):,}")
    print(f"  - Pass rate: {(df['status'] == 'pass').mean():.1%}")
    print(f"  - Fail rate: {(df['status'] == 'fail').mean():.1%}")
    print(f"  - Avg duration (pass): {df[df['status'] == 'pass']['duration_ms'].mean():.0f}ms")
    print(f"  - Avg duration (fail): {df[df['status'] == 'fail']['duration_ms'].mean():.0f}ms")
    print(f"  - Environments: {', '.join(df['environment'].unique())}")
    print(f"  - Browsers: {', '.join(df['browser'].unique())}")
    
    # Top flaky tests
    flaky_tests['pass_rate'] = flaky_tests['passes'] / flaky_tests['total']
    flaky_tests = flaky_tests.sort_values('pass_rate')
    
    print("\n🔥 Top 5 Most Flaky Tests (lowest pass rate):")
    for idx, row in flaky_tests.head(5).iterrows():
        test_name = df[df['test_case_id'] == row['test_case_id']]['test_name'].iloc[0]
        print(f"  - Test {row['test_case_id']} ({test_name}): {row['pass_rate']:.1%} pass rate")
    
    print("\n✅ Data quality: GOOD")
    print("\n🚀 Ready to start analysis!")
    print("   Next step: jupyter notebook")
    
    return True

if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) > 1 else 'testneo_test_executions.csv'
    success = verify_data(filename)
    sys.exit(0 if success else 1)
