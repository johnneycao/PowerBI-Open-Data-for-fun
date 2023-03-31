---
title: Basic Data
author: Johnney Cao
date updated: 2023-2-3
keyword: [Date Table, Parameter, LastRefresh Date]
---

# Basic Data

----------

[PBI Download Link](../_Asset%20Library/Source_Files/Baseline.pbit)

## Parameters

1. **StartDate**: Required, Type as *Date*

----------

## Data Tables

### 1. *Date* Table

#### Depedency

##### Parameter

- **StartDate**, set value *'1/1/1990'*

#### Steps
1. Create a parameter **StartDate** for the *Start Date*;
1. Convert parameter to table and add **EndDate**;
1. Create a list of date between **StartDate** and **EndDate** , and then delete **StartDate** and **EndDate** columns;
1. Add Columns for Year, Quarter, Month, Week and Day Columns;
1. Set the table as Date Table (**Table tools** -> **Mark as data table**).

#### Power Query Sample Script
```css
let
    Source = if (StartDate = null) then #date(1990,1,1) else StartDate,
    #"Converted Parameter to Table" = #table(1, {{Source}}),
    #"Renamed StartDate" = Table.RenameColumns(#"Converted Parameter to Table",{{"Column1", "StartDate"}}),
    #"Added EndDate" = Table.AddColumn(#"Renamed StartDate", "EndDate", each Date.From(Date.EndOfYear(DateTime.LocalNow()))),
    #"Changed fields to Date Type" = Table.TransformColumnTypes(#"Added EndDate",{{"StartDate", type date}, {"EndDate", type date}}),
    #"Added Date List" = Table.AddColumn(#"Changed fields to Date Type", "Date", each {Number.From([StartDate])..Number.From([EndDate])}),
    #"Expanded Dates" = Table.ExpandListColumn(#"Added Date List", "Date"),
    #"Changed Date to Date Type" = Table.TransformColumnTypes(#"Expanded Dates",{{"Date", type date}}),
    #"Removed Start End Date" = Table.RemoveColumns(#"Changed Date to Date Type",{"StartDate", "EndDate"}),
    #"Added Year" = Table.AddColumn(#"Removed Start End Date", "Year", each Date.Year([Date]), Int64.Type),
    #"Added MonthNum" = Table.AddColumn(#"Added Year", "MonthNum", each Date.Month([Date]), Int64.Type),
    #"Added MonthFullName" = Table.AddColumn(#"Added MonthNum", "MonthFullName", each Date.MonthName([Date])),
    #"Added MonthShortName" = Table.AddColumn(#"Added MonthFullName", "MonthShortName", each Text.Start([MonthFullName],3)),
    #"Added Month" = Table.AddColumn(#"Added MonthShortName", "Mon", each Text.Combine({Text.From([Year], "en-US"), "-", Text.PadStart(Text.From([MonthNum], "en-US"), 2, "0")}), type text),
    #"Added QuarterNum" = Table.AddColumn(#"Added Month", "QuarterNum", each Date.QuarterOfYear([Date]), Int64.Type),
    #"Added Quarter" = Table.AddColumn(#"Added QuarterNum", "Qty", each Text.Combine({Text.From([Year], "en-US"), "-Q", Text.From([QuarterNum], "en-US")}), type text),
    #"Added WeekNum" = Table.AddColumn(#"Added Quarter", "WeekNum", each Date.WeekOfYear([Date])),
    #"Added WeekName" = Table.AddColumn(#"Added WeekNum", "WeekName", each Text.Combine({"W", Text.PadStart(Text.From([WeekNum], "en-US"), 2, "0")}), type text),
    #"Added Week" = Table.AddColumn(#"Added WeekName", "Week", each Text.Combine({Text.From([Year], "en-US"), "-", [WeekName]}), type text),
    #"Added Day" = Table.AddColumn(#"Added Week", "Day", each Date.Day([Date]), Int64.Type)
in
    #"Added Day"
```

### 2. *Calendar* Table - Alternative Approach using DAX
1. Use [CALENDAR](https://learn.microsoft.com/en-us/dax/calendar-function-dax) or [CALENDARAUTO](https://learn.microsoft.com/en-us/dax/calendarauto-function-dax) DAX functions to [Create date tables in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/guidance/model-date-tables);
1. Add Columns for Year, Quarter, Month, Week and Day Columns;
1. Set the table as Date Table (**Table tools** -> **Mark as data table**).

### 3. *Year* Table

#### Dependency

- **Date** Table

#### Steps
1. Reference from **Date** Table above;
1. Keep **Year** column only, and remove duplicate records.

#### Power Query Sample Script
```css
let
    Source = DateTable,
    #"Removed Other Columns" = Table.SelectColumns(Source,{"Year"}),
    #"Removed Duplicates" = Table.Distinct(#"Removed Other Columns")
in
    #"Removed Duplicates"
```

### 3. *Last Refreshed* Table

#### Steps
1. Create a table using *LocalNow()*.

#### Power Query Sample Script
```css
let
    Source = #table(type table[LastRefresh=datetime], {{DateTime.LocalNow()}})
in
    Source
```
----------

## Relationship
Tables | Relationship
---- | -----
**DateTable** / **YearTable** | Many to 1
**LastRefresh** / **DateTable** | 1 to 1

----------

## Reference

### Power Query Reference

1. [Understanding Power Query M functions](https://learn.microsoft.com/en-us/powerquery-m/understanding-power-query-m-functions)
1. [Using parameters](https://learn.microsoft.com/en-us/power-query/power-query-query-parameters)
1. [Auto date/time guidance in Power BI Desktop](https://learn.microsoft.com/en-us/power-bi/guidance/auto-date-time)