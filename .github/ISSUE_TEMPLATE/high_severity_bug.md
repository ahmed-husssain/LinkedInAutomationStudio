name: "🚨 High Severity Bug Report"
description: "Report a critical bug, crash, security loophole, or visual degradation"
title: "[BUG]: "
labels: ["bug", "high-priority"]
body:
  - type: markdown
    attributes:
      value: |
        Thank you for reporting an issue! Please provide as much detail as possible so contributors can reproduce and fix it quickly.
  - type: textarea
    id: problem-description
    attributes:
      label: "Problem Description & Severity"
      description: "What broke, and what is the real-world impact on users?"
      placeholder: "e.g. Memory leak during Manim 60fps compilation crashes container after 3 renders..."
    validations:
      required: true
  - type: textarea
    id: reproduction-steps
    attributes:
      label: "Steps to Reproduce"
      description: "Exact sequence of actions to trigger the bug"
      placeholder: |
        1. Run `python -m streamlit run app.py`
        2. Select topic 'kafka_vs_rabbitmq'
        3. Click 'Generate'
        4. See error...
    validations:
      required: true
  - type: textarea
    id: expected-vs-actual
    attributes:
      label: "Expected vs. Actual Behavior"
      placeholder: "Expected: Generates 1080x1350 PDF without clipping. Actual: Text overflows bottom border..."
    validations:
      required: true
  - type: textarea
    id: logs-and-tracebacks
    attributes:
      label: "Logs & Tracebacks"
      placeholder: "Paste console logs or pytest failure outputs here..."
      render: shell
