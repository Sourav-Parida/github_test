def summarize_results(cases):
    passed = 0
    failures = []

    for case in cases:
        if case['expected'] == case['actual']:
            passed += 1
        else:
            failures.append(case['name'])

    return {
        'passed': passed,
        'failed': len(failures),
        'failures': failures
    }