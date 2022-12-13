# Basic Data

## 1. Date Table

### Parameters
<em>Start Date</em>: Required, Type as Date

### Steps:
1. Create a parameter for the <em>Start Date</em>
2. Convert parameter to table and add <em>End Date</em>
3. Create a list of date between <em>Start Date</em> and <em>End Date</em> using [<strong>each</strong>](https://learn.microsoft.com/en-us/powerquery-m/understanding-power-query-m-functions) keyword
4. Add Columns for Year, Quarter, Month and Day

### Power Query Script
>let
>>    <p>Source = StartDate,
>>    <p>#"Converted Parameter to Table" = #table(1, {{Source}}),
>>    <p>#"Renamed StartDate" = Table.RenameColumns(#"Converted Parameter to Table",{{"Column1", "StartDate"}}),
>>    <p>#"Added EndDate" = Table.AddColumn(#"Renamed StartDate", "EndDate", each Date.From(Date.EndOfYear(DateTime.LocalNow()))),
>>    <p>#"Changed to Date Type" = Table.TransformColumnTypes(#"Added EndDate",{{"StartDate", type date}, {"EndDate", type date}}),
>>    <p>#"Added Date List" = Table.AddColumn(#"Changed to Date Type", "Date", each {Number.From([StartDate])..Number.From([EndDate])}),
>>    <p>#"Expanded Dates" = Table.ExpandListColumn(#"Added Date List", "Date"),
>>    <p>#"Changed List to Data Type" = Table.TransformColumnTypes(#"Expanded Dates",{{"Date", type date}}),
>>    <p>#"Keep Date List only" = Table.RemoveColumns(#"Changed List to Data Type",{"StartDate", "EndDate"}),
>>    <p>#"Added Year" = Table.AddColumn(#"Keep Date List only", "Year", each Date.Year([Date]), Int64.Type),
>>    <p>#"Added Month" = Table.AddColumn(#"Added Year", "Month", each Date.Month([Date]), Int64.Type),
>>    <p>#"Added MonthName" = Table.AddColumn(#"Added Month", "MonthName", each Date.MonthName([Date])),
>>    <p>#"Added ShortMonthName" = Table.AddColumn(#"Added MonthName", "ShortMonthName", each Text.Start([MonthName],3)),
>>    <p>#"Added Day" = Table.AddColumn(#"Added ShortMonthName", "Day", each Date.Day([Date]), Int64.Type),
>>    <p>#"Added Quarter" = Table.AddColumn(#"Added Day", "Quarter", each Date.QuarterOfYear([Date]), Int64.Type),
>>    <p>#"Added QuarterName" = Table.AddColumn(#"Added Quarter", "Qty", each Text.Combine({Text.From([Year], "en-US"), "-Q", Text.From([Quarter], "en-US")}), type text)
>
>in
>>    <p>#"Added QuarterName"

### Alternative Way
- [Create date tables in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/guidance/model-date-tables)

## 2. Refreshed Date