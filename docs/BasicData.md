# Basic Data

## 1. <em>Date</em> Table

### Parameters
<em>Start Date</em>: Required, Type as Date

### Steps:
1. Create a parameter for the <em>Start Date</em>
1. Convert parameter to table and add <em>End Date</em>
1. Create a list of date between <em>Start Date</em> and <em>End Date</em> using [<strong>each</strong>](https://learn.microsoft.com/en-us/powerquery-m/understanding-power-query-m-functions) keyword
1. Add Columns for Year, Quarter, Month and Day

### Power Query Script:
```fsharp
let
    Source = StartDate,
    #"Converted Parameter to Table" = #table(1, {{Source}}),
    #"Renamed StartDate" = Table.RenameColumns(#"Converted Parameter to Table",{{"Column1", "StartDate"}}),
    #"Added EndDate" = Table.AddColumn(#"Renamed StartDate", "EndDate", each Date.From(Date.EndOfYear(DateTime.LocalNow()))),
    #"Changed to Date Type" = Table.TransformColumnTypes(#"Added EndDate",{{"StartDate", type date}, {"EndDate", type date}}),
    #"Added Date List" = Table.AddColumn(#"Changed to Date Type", "Date", each {Number.From([StartDate])..Number.From([EndDate])}),
    #"Expanded Dates" = Table.ExpandListColumn(#"Added Date List", "Date"),
    #"Changed List to Data Type" = Table.TransformColumnTypes(#"Expanded Dates",{{"Date", type date}}),
    #"Keep Date List only" = Table.RemoveColumns(#"Changed List to Data Type",{"StartDate", "EndDate"}),
    #"Added Year" = Table.AddColumn(#"Keep Date List only", "Year", each Date.Year([Date]), Int64.Type),
    #"Added Month" = Table.AddColumn(#"Added Year", "Month", each Date.Month([Date]), Int64.Type),
    #"Added MonthName" = Table.AddColumn(#"Added Month", "MonthName", each Date.MonthName([Date])),
    #"Added ShortMonthName" = Table.AddColumn(#"Added MonthName", "ShortMonthName", each Text.Start([MonthName],3)),
    #"Added Day" = Table.AddColumn(#"Added ShortMonthName", "Day", each Date.Day([Date]), Int64.Type),
    #"Added Quarter" = Table.AddColumn(#"Added Day", "Quarter", each Date.QuarterOfYear([Date]), Int64.Type),
    #"Added QuarterName" = Table.AddColumn(#"Added Quarter", "Qty", each Text.Combine({Text.From([Year], "en-US"), "-Q", Text.From([Quarter], "en-US")}), type text)
 in
    #"Added QuarterName"'
```

### Alternative Way
- [Create date tables in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/guidance/model-date-tables)

## 2. <em>Year</em> Table

### Steps:
1. Reference from **Date** Table above
1. Keep <em>Year</em> column only, and remove duplicate records

### Power Query Script:
```xml
let
    Source = DateTable,
    #"Removed Other Columns" = Table.SelectColumns(Source,{"Year"}),
    #"Removed Duplicates" = Table.Distinct(#"Removed Other Columns")
in
    #"Removed Duplicates"
```

## 3. <em> Last Refreshed Date</em> Table

### Steps:
1. Create a table using <em>LocalNow()</em> 

### Power Query Script:
```dax
let
    Source = #table(type table[Last Refreshed Date=datetime], {{DateTime.LocalNow()}})
in
    Source
```