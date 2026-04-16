# Intern Project: Flaky Test Detection System (8-Week Plan)

## Project Overview

**Goal**: Build a production-ready flaky test detection system that can be integrated into TestNeo

**Duration**: 8 weeks

**Deliverables**: 
1. Multi-dimensional flakiness scoring engine
2. Root cause classification system (8 categories)
3. Predictive flakiness model
4. Fix recommendation engine
5. Integration-ready API
6. Enhanced UI components
7. Documentation + demo

---

## Week 1: Data Analysis & Enhanced Detection Design

### Task 1.1: Data Exploration (Days 1-2)

**Deliverable**: Jupyter notebook `01_data_exploration.ipynb`

**What to analyze**:

```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load data
df = pd.read_csv('testneo_test_executions.csv')

# 1. Basic statistics
print("Total executions:", len(df))
print("Unique tests:", df['test_case_id'].nunique())
print("Date range:", df['executed_at'].min(), "to", df['executed_at'].max())

# 2. Identify flaky tests (simple method)
test_stats = df.groupby('test_case_id').agg({
    'status': ['count', lambda x: (x == 'pass').sum(), lambda x: (x == 'fail').sum()]
}).reset_index()
test_stats.columns = ['test_case_id', 'total_runs', 'passes', 'fails']
test_stats['pass_rate'] = test_stats['passes'] / test_stats['total_runs']

# Flaky = has both passes and fails
flaky_tests = test_stats[(test_stats['passes'] > 0) & (test_stats['fails'] > 0)]
print(f"\nFlaky tests: {len(flaky_tests)} out of {len(test_stats)}")

# 3. Flip counting
def count_flips(test_id):
    statuses = df[df['test_case_id'] == test_id].sort_values('executed_at')['status'].tolist()
    flips = sum(1 for i in range(1, len(statuses)) if statuses[i] != statuses[i-1])
    return flips

flaky_tests['flips'] = flaky_tests['test_case_id'].apply(count_flips)
flaky_tests['flip_rate'] = flaky_tests['flips'] / (flaky_tests['total_runs'] - 1)

# 4. Visualizations
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Pass rate distribution
axes[0, 0].hist(flaky_tests['pass_rate'], bins=20, edgecolor='black')
axes[0, 0].set_title('Pass Rate Distribution (Flaky Tests)')
axes[0, 0].set_xlabel('Pass Rate')
axes[0, 0].set_ylabel('Count')

# Flip rate distribution
axes[0, 1].hist(flaky_tests['flip_rate'], bins=20, edgecolor='black', color='orange')
axes[0, 1].set_title('Flip Rate Distribution')
axes[0, 1].set_xlabel('Flip Rate')
axes[0, 1].set_ylabel('Count')

# Temporal patterns
df['executed_at'] = pd.to_datetime(df['executed_at'])
df['hour'] = df['executed_at'].dt.hour
hourly_failures = df[df['status'] == 'fail'].groupby('hour').size()
axes[1, 0].bar(hourly_failures.index, hourly_failures.values)
axes[1, 0].set_title('Failures by Hour of Day')
axes[1, 0].set_xlabel('Hour')
axes[1, 0].set_ylabel('Failure Count')

# Environment distribution
env_stats = df.groupby(['environment', 'status']).size().unstack(fill_value=0)
env_stats.plot(kind='bar', ax=axes[1, 1], stacked=True)
axes[1, 1].set_title('Executions by Environment')
axes[1, 1].set_xlabel('Environment')
axes[1, 1].set_ylabel('Count')

plt.tight_layout()
plt.savefig('data_exploration.png')
plt.show()

# 5. Error message analysis
print("\nTop error patterns:")
error_words = df[df['status'] == 'fail']['error_message'].str.lower().str.split().explode()
print(error_words.value_counts().head(20))
```

**Expected Output**: 
- Summary statistics report
- 4 visualizations showing patterns
- List of flaky tests with flip rates
- Common error patterns

### Task 1.2: Design Multi-Dimensional Scoring (Days 3-5)

**Deliverable**: Design document `flakiness_scoring_design.md`

**Components to design**:

1. **Flip Frequency Score (30 points)**
   - Simple: flips / (total_runs - 1)
   - Normalized to 0-30 scale

2. **Flip Clustering Score (20 points)**
   - Measure variance of flip intervals
   - Random flips = high score (more flaky)
   - Clustered flips = low score (less flaky)

3. **Temporal Stability Score (20 points)**
   - Split executions into time windows
   - Calculate pass rate variance across windows
   - High variance = unstable = more flaky

4. **Environmental Sensitivity Score (15 points)**
   - Compare pass rates across environments
   - High variance = environment-dependent = more flaky

5. **Recent Trend Score (15 points)**
   - Compare recent vs historical pass rates
   - Degrading = higher score

**Pseudocode**:
```python
def calculate_flakiness_score(test_history):
    # 1. Flip frequency
    flips = count_status_changes(test_history)
    flip_score = (flips / max(len(test_history) - 1, 1)) * 30
    
    # 2. Flip clustering
    flip_intervals = get_flip_intervals(test_history)
    if len(flip_intervals) > 1:
        variance = np.var(flip_intervals)
        clustering_score = 20 * (1 - min(variance / 100, 1))
    else:
        clustering_score = 0
    
    # 3. Temporal stability
    windows = split_into_time_windows(test_history, window_size=10)
    window_pass_rates = [calculate_pass_rate(w) for w in windows]
    if len(window_pass_rates) > 1:
        stability_score = 20 * np.var(window_pass_rates)
    else:
        stability_score = 0
    
    # 4. Environmental sensitivity
    env_pass_rates = group_by_environment(test_history)
    if len(env_pass_rates) > 1:
        env_score = 15 * np.var(list(env_pass_rates.values()))
    else:
        env_score = 0
    
    # 5. Recent trend
    recent = test_history[-20:]
    older = test_history[-40:-20]
    if len(recent) >= 5 and len(older) >= 5:
        trend_score = 15 * abs(pass_rate(recent) - pass_rate(older))
    else:
        trend_score = 0
    
    total = flip_score + clustering_score + stability_score + env_score + trend_score
    
    return {
        'total_score': min(total, 100),
        'breakdown': {
            'flip_score': flip_score,
            'clustering_score': clustering_score,
            'stability_score': stability_score,
            'env_score': env_score,
            'trend_score': trend_score
        },
        'severity': classify_severity(total)
    }
```

---

## Week 2: Implement Enhanced Detection

### Task 2.1: Build Flakiness Detector (Days 1-3)

**Deliverable**: `flaky_test_detector.py`

**Implementation**:
```python
"""
Enhanced flaky test detection with multi-dimensional scoring
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    CRITICAL = "critical"  # Score > 70
    HIGH = "high"          # Score > 50
    MEDIUM = "medium"      # Score > 30
    LOW = "low"            # Score <= 30

@dataclass
class FlakinessScore:
    total_score: float
    flip_score: float
    clustering_score: float
    stability_score: float
    env_score: float
    trend_score: float
    severity: Severity
    
class FlakyTestDetector:
    """Detect flaky tests with multi-dimensional scoring"""
    
    def __init__(self, min_executions: int = 5):
        self.min_executions = min_executions
    
    def analyze_test(self, test_history: pd.DataFrame) -> FlakinessScore:
        """
        Analyze a single test for flakiness
        
        Args:
            test_history: DataFrame with columns [status, executed_at, environment]
        
        Returns:
            FlakinessScore object
        """
        if len(test_history) < self.min_executions:
            return None
        
        # Sort by time
        test_history = test_history.sort_values('executed_at')
        statuses = test_history['status'].tolist()
        
        # Calculate each component
        flip_score = self._calculate_flip_score(statuses)
        clustering_score = self._calculate_clustering_score(statuses)
        stability_score = self._calculate_stability_score(test_history)
        env_score = self._calculate_env_score(test_history)
        trend_score = self._calculate_trend_score(statuses)
        
        total = flip_score + clustering_score + stability_score + env_score + trend_score
        total = min(total, 100)
        
        severity = self._classify_severity(total)
        
        return FlakinessScore(
            total_score=total,
            flip_score=flip_score,
            clustering_score=clustering_score,
            stability_score=stability_score,
            env_score=env_score,
            trend_score=trend_score,
            severity=severity
        )
    
    def _calculate_flip_score(self, statuses: List[str]) -> float:
        """Calculate flip frequency score (0-30)"""
        flips = sum(1 for i in range(1, len(statuses)) if statuses[i] != statuses[i-1])
        return (flips / max(len(statuses) - 1, 1)) * 30
    
    def _calculate_clustering_score(self, statuses: List[str]) -> float:
        """Calculate flip clustering score (0-20)"""
        flip_indices = [i for i in range(1, len(statuses)) if statuses[i] != statuses[i-1]]
        
        if len(flip_indices) < 2:
            return 0
        
        intervals = np.diff(flip_indices)
        variance = np.var(intervals)
        
        # Lower variance = more clustered = less flaky
        # Higher variance = more random = more flaky
        return 20 * min(variance / 100, 1)
    
    def _calculate_stability_score(self, test_history: pd.DataFrame) -> float:
        """Calculate temporal stability score (0-20)"""
        window_size = 10
        statuses = test_history['status'].tolist()
        
        windows = [statuses[i:i+window_size] for i in range(0, len(statuses), window_size)]
        windows = [w for w in windows if len(w) >= 3]
        
        if len(windows) < 2:
            return 0
        
        pass_rates = [sum(1 for s in w if s == 'pass') / len(w) for w in windows]
        variance = np.var(pass_rates)
        
        return 20 * variance
    
    def _calculate_env_score(self, test_history: pd.DataFrame) -> float:
        """Calculate environmental sensitivity score (0-15)"""
        env_groups = test_history.groupby('environment')['status']
        
        if len(env_groups) < 2:
            return 0
        
        pass_rates = {}
        for env, statuses in env_groups:
            if len(statuses) >= 3:
                pass_rates[env] = (statuses == 'pass').mean()
        
        if len(pass_rates) < 2:
            return 0
        
        variance = np.var(list(pass_rates.values()))
        return 15 * variance
    
    def _calculate_trend_score(self, statuses: List[str]) -> float:
        """Calculate recent trend score (0-15)"""
        if len(statuses) < 20:
            return 0
        
        recent = statuses[-20:]
        older = statuses[-40:-20] if len(statuses) >= 40 else statuses[:-20]
        
        if len(older) < 5:
            return 0
        
        recent_pass_rate = sum(1 for s in recent if s == 'pass') / len(recent)
        older_pass_rate = sum(1 for s in older if s == 'pass') / len(older)
        
        return 15 * abs(recent_pass_rate - older_pass_rate)
    
    def _classify_severity(self, score: float) -> Severity:
        """Classify severity based on score"""
        if score > 70:
            return Severity.CRITICAL
        elif score > 50:
            return Severity.HIGH
        elif score > 30:
            return Severity.MEDIUM
        else:
            return Severity.LOW
    
    def analyze_all_tests(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze all tests in dataset
        
        Args:
            df: DataFrame with columns [test_case_id, status, executed_at, environment]
        
        Returns:
            DataFrame with flakiness scores for each test
        """
        results = []
        
        for test_id in df['test_case_id'].unique():
            test_history = df[df['test_case_id'] == test_id]
            
            # Check if test is flaky (has both passes and fails)
            has_pass = (test_history['status'] == 'pass').any()
            has_fail = (test_history['status'] == 'fail').any()
            
            if not (has_pass and has_fail):
                continue  # Not flaky
            
            score = self.analyze_test(test_history)
            
            if score:
                results.append({
                    'test_case_id': test_id,
                    'test_name': test_history['test_name'].iloc[0],
                    'total_score': score.total_score,
                    'flip_score': score.flip_score,
                    'clustering_score': score.clustering_score,
                    'stability_score': score.stability_score,
                    'env_score': score.env_score,
                    'trend_score': score.trend_score,
                    'severity': score.severity.value,
                    'total_executions': len(test_history),
                    'pass_count': (test_history['status'] == 'pass').sum(),
                    'fail_count': (test_history['status'] == 'fail').sum(),
                    'pass_rate': (test_history['status'] == 'pass').mean()
                })
        
        return pd.DataFrame(results).sort_values('total_score', ascending=False)
```

### Task 2.2: Temporal Pattern Detection (Days 4-5)

**Deliverable**: `temporal_analyzer.py`

**Implementation**: Add temporal pattern detection for hour-of-day, day-of-week, and deployment correlation patterns.

---

## Week 3: Root Cause Classification

### Task 3.1: Design Classification System (Days 1-2)

**Deliverable**: Design document `root_cause_classification_design.md`

**8 Root Cause Categories**:

1. **TIMING** - Race conditions, timeouts, slow responses
2. **ENVIRONMENT** - Network issues, database connectivity
3. **TEST_ORDER** - Shared state, test dependencies
4. **RESOURCE** - Memory, CPU, disk contention
5. **EXTERNAL_SERVICE** - 3rd party API flakiness
6. **DATA_DEPENDENT** - Test data issues, data races
7. **BROWSER_SPECIFIC** - Browser quirks (web tests only)
8. **INFRASTRUCTURE** - CI/CD infrastructure issues

**Classification Approach**: Rule-based + ML hybrid

### Task 3.2: Implement Root Cause Classifier (Days 3-5)

**Deliverable**: `root_cause_classifier.py`

**Implementation**: Rule-based classifier that analyzes error messages, timing patterns, and environmental correlations.

---

## Week 4: Fix Recommendations

### Task 4.1: Build Recommendation Engine (Days 1-3)

**Deliverable**: `fix_recommender.py`

**Features**:
- Root cause-specific recommendations
- Code examples for each fix
- Priority ordering
- Estimated time to fix

### Task 4.2: Similar Failure Finder (Days 4-5)

**Deliverable**: `similarity_finder.py`

**Features**: Find similar historical failures with known resolutions

---

## Week 5-6: Predictive Model

### Task 5.1: Feature Engineering (Week 5, Days 1-2)

**Features for prediction**:
- Test age
- Code churn
- Test complexity
- Historical stability
- External dependencies

### Task 5.2: Build Predictive Model (Week 5, Days 3-5)

**Deliverable**: `flakiness_predictor.py`

**Model**: Random Forest or Gradient Boosting

### Task 5.3: Evaluation (Week 6, Days 1-2)

**Metrics**: Precision, recall, F1-score, ROC-AUC

### Task 5.4: Integration (Week 6, Days 3-5)

**Deliverable**: Integrate all components into unified system

---

## Week 7-8: API & UI

### Task 7.1: Build API (Week 7, Days 1-3)

**Deliverable**: FastAPI endpoints

### Task 7.2: Build UI Components (Week 7, Days 4-5, Week 8, Days 1-2)

**Deliverable**: React components for dashboard

### Task 8.1: Documentation (Week 8, Days 3-4)

**Deliverable**: Integration guide, API docs

### Task 8.2: Final Demo (Week 8, Day 5)

**Deliverable**: Presentation + demo

---

## Success Criteria

- [ ] Multi-dimensional scoring implemented and tested
- [ ] Root cause classification achieves >70% accuracy
- [ ] Predictive model achieves >60% accuracy
- [ ] API endpoints functional
- [ ] UI components integrated
- [ ] Documentation complete
- [ ] Demo successful

**Let's build this! 🚀**
