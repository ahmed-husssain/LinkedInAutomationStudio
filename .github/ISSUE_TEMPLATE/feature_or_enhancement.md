name: "✨ Feature or Architectural Enhancement"
description: "Suggest an improvement to visual quality, performance, or deployment"
title: "[FEAT]: "
labels: ["enhancement", "help wanted"]
body:
  - type: textarea
    id: feature-summary
    attributes:
      label: "Feature Summary & User Value"
      description: "What capability should be added, and who benefits?"
      placeholder: "e.g. Add packages.txt for 1-click zero-cost Hugging Face Spaces deployment..."
    validations:
      required: true
  - type: textarea
    id: proposed-solution
    attributes:
      label: "Proposed Technical Implementation"
      description: "How should this be built within our existing architecture?"
      placeholder: "Describe modules, classes, and tests to add..."
    validations:
      required: true
  - type: checkboxes
    id: compliance
    attributes:
      label: "Architectural Compliance"
      options:
        - label: "This enhancement adheres to SPEC.md quality gates and does not add redundant dependencies."
          required: true
        - label: "This change maintains backward compatibility with the existing 93-test test suite."
          required: true
