' CST Level 2 multisource macro template
' Generated from outputs/cst_macro_templates/level2_macro_sample_parameters.csv
' and outputs/cst_macro_templates/level2_macro_source_parameters.csv.

Option Explicit

Const SAMPLE_CSV = "outputs\cst_macro_templates\level2_macro_sample_parameters.csv"
Const SOURCE_CSV = "outputs\cst_macro_templates\level2_macro_source_parameters.csv"
Const SENSOR_CSV = "outputs\cst_templates\sensor_layout_hemisphere_for_cst.csv"

Sub Main()
    MsgBox "Run pilot cases in level2_pilot_cases.csv before the full 48-sample Level 2 batch." & vbCrLf & _
           "Each sample keeps one CST project and exports all listed frequencies to the sample-level CSV names."
End Sub

Sub BuildLevel2Sample(ByVal sampleId, ByVal frequencyList, ByVal nearExport, ByVal farExport)
    ' Suggested CST workflow:
    ' 1. Create all sources from SOURCE_CSV rows with matching sample_id.
    ' 2. Preserve relative amplitude and phase from the excitation table.
    ' 3. Add one far-field monitor per frequency in frequencyList.
    ' 4. Export all near-field rows with sample_id, frequency_hz, sensor_id, x/y/z, Ex/Ey/Ez.
    ' 5. Export all far-field rows with sample_id, frequency_hz, theta_deg, phi_deg, Etheta/Ephi or gain.
    AddToHistory "CS202614_Level2_Metadata", "' sample_id=" & sampleId & ", frequencies=" & frequencyList
End Sub
