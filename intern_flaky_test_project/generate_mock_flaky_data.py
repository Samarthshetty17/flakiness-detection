"""
Generate realistic mock test execution data with embedded flaky patterns
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import argparse

class FlakyDataGenerator:
    """Generate mock test execution data with realistic flaky patterns"""
    
    def __init__(self, num_tests=50, num_executions=5000, start_date='2026-01-01'):
        self.num_tests = num_tests
        self.num_executions = num_executions
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime('2026-03-25')
        
        # Flaky pattern assignments
        self.timeout_tests = list(range(1, 11))  # 10 tests
        self.network_tests = list(range(11, 19))  # 8 tests
        self.auth_tests = list(range(19, 24))  # 5 tests
        self.race_tests = list(range(24, 30))  # 6 tests
        self.weekend_tests = list(range(30, 34))  # 4 tests
        self.peak_hour_tests = list(range(34, 39))  # 5 tests
        self.browser_tests = list(range(39, 46))  # 7 tests
        self.order_tests = list(range(46, 51))  # 5 tests
        
    def generate(self):
        """Generate full dataset"""
        executions = []
        execution_id = 1
        
        # Generate executions for each test
        for test_id in range(1, self.num_tests + 1):
            test_executions = self.num_executions // self.num_tests
            
            for _ in range(test_executions):
                execution = self._generate_execution(execution_id, test_id)
                executions.append(execution)
                execution_id += 1
        
        df = pd.DataFrame(executions)
        return df
    
    def _generate_execution(self, execution_id, test_id):
        """Generate a single test execution"""
        # Random timestamp within date range
        days_diff = (self.end_date - self.start_date).days
        random_days = random.randint(0, days_diff)
        random_hours = random.randint(0, 23)
        random_minutes = random.randint(0, 59)
        random_seconds = random.randint(0, 59)
        
        executed_at = self.start_date + timedelta(
            days=random_days,
            hours=random_hours,
            minutes=random_minutes,
            seconds=random_seconds
        )
        
        # Determine status based on flaky pattern
        status, error_message, error_type = self._determine_status(test_id, executed_at)
        
        # Duration (longer if failed)
        if status == 'pass':
            duration_ms = random.randint(500, 2000)
        else:
            duration_ms = random.randint(2000, 5000)
        
        # Environment
        environment = random.choice(['staging', 'staging', 'staging', 'production', 'production'])
        
        # Browser (for web tests)
        browser = random.choice(['chrome', 'chrome', 'firefox', 'safari'])
        
        # Build version
        build_version = f"v1.{random.randint(1, 5)}.{random.randint(0, 20)}"
        
        return {
            'execution_id': execution_id,
            'test_case_id': test_id,
            'test_name': f'test_{self._get_test_name(test_id)}',
            'status': status,
            'executed_at': executed_at,
            'duration_ms': duration_ms,
            'error_message': error_message if status == 'fail' else '',
            'error_type': error_type if status == 'fail' else '',
            'environment': environment,
            'browser': browser,
            'build_version': build_version
        }
    
    def _determine_status(self, test_id, executed_at):
        """Determine execution status based on flaky patterns"""
        
        # Pattern 1: Timeout flakiness (20% failure rate)
        if test_id in self.timeout_tests:
            if random.random() < 0.20:
                return 'fail', 'Timeout after 3000ms', 'timeout'
            return 'pass', '', ''
        
        # Pattern 2: Network flakiness (15% failure rate)
        if test_id in self.network_tests:
            if random.random() < 0.15:
                error = random.choice(['Connection refused', 'Network error', 'DNS resolution failed'])
                return 'fail', error, 'network'
            return 'pass', '', ''
        
        # Pattern 3: Auth token expiry (fails after 1 hour)
        if test_id in self.auth_tests:
            # Simulate token expiry every hour
            if executed_at.minute > 50:  # Last 10 minutes of each hour
                error = random.choice(['401 Unauthorized', 'Token expired', '403 Forbidden'])
                return 'fail', error, 'auth'
            return 'pass', '', ''
        
        # Pattern 4: Race condition (25% failure rate)
        if test_id in self.race_tests:
            if random.random() < 0.25:
                error = random.choice(['Element not found', 'State mismatch', 'Unexpected value'])
                return 'fail', error, 'assertion'
            return 'pass', '', ''
        
        # Pattern 5: Weekend effect (50% failure on Saturday)
        if test_id in self.weekend_tests:
            if executed_at.dayofweek == 5:  # Saturday
                if random.random() < 0.50:
                    return 'fail', 'Service unavailable', 'network'
            elif random.random() < 0.05:  # 5% other days
                return 'fail', 'Service unavailable', 'network'
            return 'pass', '', ''
        
        # Pattern 6: Peak hour flakiness (2-4 PM)
        if test_id in self.peak_hour_tests:
            if 14 <= executed_at.hour <= 16:  # 2-4 PM
                if random.random() < 0.40:
                    error = random.choice(['Timeout after 3000ms', 'Slow response time'])
                    return 'fail', error, 'timeout'
            elif random.random() < 0.10:  # 10% off-peak
                return 'fail', 'Timeout after 3000ms', 'timeout'
            return 'pass', '', ''
        
        # Pattern 7: Browser-specific (fails in Safari)
        if test_id in self.browser_tests:
            # Need to check browser from execution context
            # For now, use random with 30% failure rate
            if random.random() < 0.30:
                error = random.choice(['Element not clickable', 'Selector not found', 'Browser compatibility issue'])
                return 'fail', error, 'browser'
            return 'pass', '', ''
        
        # Pattern 8: Test order dependency
        if test_id in self.order_tests:
            # Simulate 20% failure rate (would be higher if run after specific test)
            if random.random() < 0.20:
                return 'fail', 'Assertion failed: expected X, got Y', 'assertion'
            return 'pass', '', ''
        
        # Default: stable test (5% failure rate)
        if random.random() < 0.05:
            return 'fail', 'Unexpected error', 'unknown'
        return 'pass', '', ''
    
    def _get_test_name(self, test_id):
        """Generate test name based on test ID"""
        names = [
            'checkout_payment', 'user_login', 'product_search', 'cart_update',
            'order_history', 'profile_update', 'password_reset', 'email_verification',
            'shipping_calculator', 'tax_calculation', 'discount_code', 'inventory_check',
            'payment_gateway', 'refund_process', 'subscription_renewal', 'notification_send',
            'api_health_check', 'database_connection', 'cache_invalidation', 'session_management',
            'file_upload', 'image_processing', 'pdf_generation', 'email_delivery',
            'webhook_handler', 'batch_processing', 'data_export', 'report_generation',
            'analytics_tracking', 'search_indexing', 'recommendation_engine', 'fraud_detection',
            'rate_limiting', 'authentication_flow', 'authorization_check', 'audit_logging',
            'backup_restore', 'data_migration', 'schema_validation', 'api_versioning',
            'load_balancing', 'circuit_breaker', 'retry_mechanism', 'timeout_handling',
            'error_recovery', 'graceful_degradation', 'feature_toggle', 'ab_testing',
            'performance_monitoring', 'security_scan'
        ]
        return names[(test_id - 1) % len(names)]

def main():
    parser = argparse.ArgumentParser(description='Generate mock flaky test data')
    parser.add_argument('--num_tests', type=int, default=50, help='Number of unique tests')
    parser.add_argument('--num_executions', type=int, default=5000, help='Total number of executions')
    parser.add_argument('--output', type=str, default='testneo_test_executions.csv', help='Output CSV file')
    
    args = parser.parse_args()
    
    print(f"Generating {args.num_executions} test executions for {args.num_tests} tests...")
    
    generator = FlakyDataGenerator(
        num_tests=args.num_tests,
        num_executions=args.num_executions
    )
    
    df = generator.generate()
    
    # Save to CSV
    df.to_csv(args.output, index=False)
    
    print(f"✅ Generated {len(df)} executions")
    print(f"✅ Saved to {args.output}")
    print(f"\nDataset statistics:")
    print(f"  - Unique tests: {df['test_case_id'].nunique()}")
    print(f"  - Date range: {df['executed_at'].min()} to {df['executed_at'].max()}")
    print(f"  - Pass rate: {(df['status'] == 'pass').mean():.1%}")
    print(f"  - Fail rate: {(df['status'] == 'fail').mean():.1%}")
    print(f"  - Environments: {df['environment'].unique().tolist()}")
    print(f"  - Browsers: {df['browser'].unique().tolist()}")

if __name__ == '__main__':
    main()
