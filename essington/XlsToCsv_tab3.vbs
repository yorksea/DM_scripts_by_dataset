if WScript.Arguments.Count < 2 Then
    WScript.Echo "Error! Please specify the source path and the destination. Usage: XlsToCsv SourcePath.xls Destination.csv"
    Wscript.Quit
End If
Dim oExcel
Set oExcel = CreateObject("Excel.Application")
Dim oBook
Set oBook = oExcel.Workbooks.Open(Wscript.Arguments.Item(0))
If oBook.Worksheets.Count > 2 Then
	oBook.Worksheets(3).Activate
	oBook.SaveAs WScript.Arguments.Item(1), 6
End If
oBook.Close False

oExcel.Quit