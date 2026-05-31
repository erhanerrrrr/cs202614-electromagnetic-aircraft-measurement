' CST Level 1 standard-source macro template
' Generated from outputs/cst_macro_templates/level1_macro_parameters.csv
' This template fixes the CS-202614 naming contract. CST API calls can vary by version,
' so keep the CSV contract and adapt the CST-specific geometry/export procedures once.

Option Explicit

Const PARAM_CSV = "outputs\cst_macro_templates\level1_macro_parameters.csv"
Const SENSOR_CSV = "outputs\cst_templates\sensor_layout_hemisphere_for_cst.csv"

Sub Main()
    MsgBox "Use " & PARAM_CSV & " as the authoritative Level 1 case table." & vbCrLf & _
           "Run required rows first: L1_short_dipole_z_1p2G and L1_halfwave_dipole_z_1p2G." & vbCrLf & _
           "Keep all export names exactly as listed."
End Sub

Sub BuildLevel1Case(ByVal sampleId, ByVal freqHz, ByVal startX, ByVal startY, ByVal startZ, _
                   ByVal endX, ByVal endY, ByVal endZ, ByVal nearExport, ByVal farExport)
    ' Suggested CST workflow:
    ' 1. Clear or clone project.
    ' 2. Set units to meters and frequency to Hz/GHz consistently.
    ' 3. Create dipole or discrete port from start/end coordinates.
    ' 4. Set excitation amplitude=1.0 and phase=0 deg unless the CSV says otherwise.
    ' 5. Add 2pi upper-hemisphere near-field point/probe export using SENSOR_CSV.
    ' 6. Add far-field monitor at freqHz.
    ' 7. Solve, export nearExport and farExport, then save CST project.
    AddToHistory "CS202614_Level1_Metadata", "' sample_id=" & sampleId & ", frequency_hz=" & CStr(freqHz)
End Sub
