# PBIP Diff
  A: test\report_a\MyReport.Report
  B: test\report_b\MyReport.Report
  7 change(s) detected

## Pages
  - PAGE REMOVED: Old Page
  + PAGE ADDED:   New Page

## Visuals
  ~ [Overview] VISUAL TYPE CHANGED: barChart -> lineChart (guid=vis-001)
  ~ [Overview] VISUAL MOVED: card (420,0 200x100) -> (500,50 200x100)

## Measures
  - MEASURE REMOVED: Sales.Old Measure
  + MEASURE ADDED: Sales.YTD Revenue
  ~ MEASURE CHANGED: Sales.Total Revenue
      WAS: SUM(Sales[Revenue])
      NOW: SUMX(Sales, Sales[Qty] * Sales[Price])

## Settings
  (no changes)