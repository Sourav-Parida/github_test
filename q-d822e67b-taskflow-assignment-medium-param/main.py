def summarize_results(cases):
    passed = 0
    failures = []

    for case in cases:
        if case['expected'] == case['actual']:
            passed += 1
        else:
            failures.append(case['name'])

    total = len(cases)
    failed = total - passed

    return {
        'total': total,
        'passed': passed,
        'failed': failed,
        'failures': failures
    }