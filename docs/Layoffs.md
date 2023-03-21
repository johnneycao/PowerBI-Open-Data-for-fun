---
title: tech layoff analysis
author: Johnney Cao
date updated: 2023-2-3
keyword: [tech layoffs, parameter, csv, conditional column, conditional formatting, append queries, multiple sources, web URL]
---

# Analysis of Tech Layoffs Data

----------

[PBI Download Link](../_Asset%20Library/Source_Files/Layoffs.pbit)

## Parameters

- **StarDate**: Required, Type as *Date*
- **FileFolder**: Required, Type as *Text*

----------

## Data Tables

### 1. Basic Tables

#### Tables 

- **Date** Table

- **Year** Table

- **LastRefreshed** Table

### 2. *Layoffs* Master Tables

#### Data Source
 [Download link 1 (Kaggle)](https://www.kaggle.com/datasets/swaptr/layoffs-2022), License: *[Open Database, Contents: © Original Authors](http://opendatacommons.org/licenses/odbl/1.0/)*

 [Download link 2 (Kaggle)](https://www.kaggle.com/datasets/theakhilb/layoffs-data-2022), License: *[Open Database, Contents: © Original Authors](http://opendatacommons.org/licenses/odbl/1.0/)*

*Some data such as the sources, list of employees laid off and date of addition has been omitted here and the complete data can be found on [Layoffs.fyi](https://layoffs.fyi/). Credits: Roger Lee*

#### Steps

1. Manual download the csv files from  [Source 1 (Kaggle)](https://www.kaggle.com/datasets/swaptr/layoffs-2022) and [Source 2 (Kaggle)](https://www.kaggle.com/datasets/theakhilb/layoffs-data-2022) to a local folder (same as **FileFolder** parameter), e.g *c:\Downloads*;
1. Retrieve the data from downloaded csv file; 
1. Promote first line as header;
1. Clean up empty Company from list;
1. Change **percentage_laid_off** to *Percentage* type and **date** or **date_added** to *Date* type;
1. Trim and clean all the text fields;
1. Replace empty value in **industry** to *Other*;
1. Add a **location** column from **city** and **country**;
1. Add a **Stage Ranking** column from **stage**;
    1. *Subsidiary* as 20,
    1. *Merged* as 30,
    1. *Seed* as 40,
    1. *Series A-C* as 50,
    1. *Series D* and above as 60,
    1. *Post IPO* as 90,
    1. else as 0 
1. Combine **Company** and **date** to a Primary **Key**;
    > =Text.Combine({[Company], "|", Date.ToText([Date], "yyyy"),Date.ToText([Date], "MM"), Date.ToText([Date], "dd")})
1. Remove the duplicate record from table;
1. Append two tables into a new table, and *disable load* for two source tables;
1. Remove duplicate records base on **Key**
1. Changed **source** field to *Web URL* in *Data Catagory*


#### Power Query Sample Script

##### Source 1
```css
let
    Source = Csv.Document(File.Contents(FileFolder & "\layoffs.csv"),[Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Filtered Rows" = Table.SelectRows(#"Promoted Headers", each true),
    #"Remove Empty Company" = Table.SelectRows(#"Filtered Rows", each ([company] <> null and [company] <> "" and [company] <> "#Paid" and [company] <> "&Open")),
    #"Changed Type" = Table.TransformColumnTypes(#"Remove Empty Company",{{"company", type text}, {"location", type text}, {"industry", type text}, {"total_laid_off", Int64.Type}, {"percentage_laid_off", Percentage.Type}, {"date", type date}, {"stage", type text}, {"country", type text}, {"funds_raised", Int64.Type}}),
    #"Replaced Other Industry" = Table.ReplaceValue(#"Changed Type","","Other",Replacer.ReplaceValue,{"industry"}),
    #"Replaced Unknown stage" = Table.ReplaceValue(#"Replaced Other Industry","","Unknown",Replacer.ReplaceValue,{"stage"}),
    #"Trimmed Text" = Table.TransformColumns(#"Replaced Unknown stage",{{"company", Text.Trim, type text}, {"location", Text.Trim, type text}, {"industry", Text.Trim, type text}, {"country", Text.Trim, type text}, {"stage", Text.Trim, type text}}),
    #"Cleaned Text" = Table.TransformColumns(#"Trimmed Text",{{"company", Text.Clean, type text}, {"location", Text.Clean, type text}, {"industry", Text.Clean, type text}, {"country", Text.Clean, type text}, {"stage", Text.Clean, type text}}),
    #"Renamed Columns" = Table.RenameColumns(#"Cleaned Text",{{"location", "city"}}),
    #"Inserted Merged Column" = Table.AddColumn(#"Renamed Columns", "location", each Text.Combine({[city], ", ", [country]}), type text),
    #"Removed Duplicates" = Table.Distinct(#"Inserted Merged Column", {"company", "total_laid_off", "percentage_laid_off", "date", "location"}),
    #"Added Stage Ranking" = Table.AddColumn(#"Removed Duplicates", "Stage Ranking", each if Text.Contains([stage], "IPO") then 90 else if Text.Contains([stage], "Private") then 80 else if Text.Contains([stage], "Subsidiary") then 20 else if Text.Contains([stage], "Acquired") then 30 else if Text.Contains([stage], "Merged") then 30 else if [stage] = "Seed" then 40 else if [stage] = "Series A" then 50 else if [stage] = "Series B" then 50 else if [stage] = "Series C" then 50 else if Text.StartsWith([stage], "Series") then 60 else 0),
    #"Filtered empty lines" = Table.SelectRows(#"Added Stage Ranking", each [total_laid_off] > 1)
in
    #"Filtered empty lines"
```
##### Source 2
```css
let
    Source = Csv.Document(File.Contents(FileFolder & "\layoffs_data.csv"),[Delimiter=",", Columns=11, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Filtered Rows" = Table.SelectRows(#"Promoted Headers", each true),
    #"Remove Empty Company" = Table.SelectRows(#"Filtered Rows", each ([Company] <> null and [Company] <> "" and [Company] <> "#Paid" and [Company] <> "&Open")),
    #"Replaced Other Industry" = Table.ReplaceValue(#"Remove Empty Company","","Other",Replacer.ReplaceValue,{"Industry"}),
    #"Replaced Unknown stage" = Table.ReplaceValue(#"Replaced Other Industry","","Unknown",Replacer.ReplaceValue,{"Stage"}),
    #"Trimmed Text" = Table.TransformColumns(#"Replaced Unknown stage",{{"Company", Text.Trim, type text}, {"Location_HQ", Text.Trim, type text}, {"Industry", Text.Trim, type text}, {"Country", Text.Trim, type text}, {"Stage", Text.Trim, type text}, {"Source", Text.Trim, type text}}),
    #"Cleaned Text" = Table.TransformColumns(#"Trimmed Text",{{"Company", Text.Clean, type text}, {"Location_HQ", Text.Clean, type text}, {"Industry", Text.Clean, type text}, {"Country", Text.Clean, type text}, {"Stage", Text.Clean, type text}, {"Source", Text.Clean, type text}}),
    #"Renamed Columns" = Table.RenameColumns(#"Cleaned Text",{{"Location_HQ", "city"}}),
    #"Inserted Merged Column" = Table.AddColumn(#"Renamed Columns", "Location", each Text.Combine({[city], ", ", [Country]}), type text),
    #"Removed Duplicates" = Table.Distinct(#"Inserted Merged Column", {"Company", "Laid_Off_Count", "Percentage", "Date", "Location"}),
    #"Added Stage Ranking" = Table.AddColumn(#"Removed Duplicates", "Stage Ranking", each if Text.Contains([Stage], "IPO") then 90 else if Text.Contains([Stage], "Private") then 80 else if Text.Contains([Stage], "Subsidiary") then 20 else if Text.Contains([Stage], "Acquired") then 30 else if Text.Contains([Stage], "Merged") then 30 else if [Stage] = "Seed" then 40 else if [Stage] = "Series A" then 50 else if [Stage] = "Series B" then 50 else if [Stage] = "Series C" then 50 else if Text.StartsWith([Stage], "Series") then 60 else 0),
    #"Changed Type" = Table.TransformColumnTypes(#"Added Stage Ranking",{{"Company", type text}, {"city", type text}, {"Industry", type text}, {"Laid_Off_Count", Int64.Type}, {"Date", type datetime}, {"Source", type text}, {"Funds_Raised", Int64.Type}, {"Stage", type text}, {"Date_Added", type datetime}, {"Country", type text}, {"Percentage", Percentage.Type}, {"Location", type text}, {"Stage Ranking", Int64.Type}}),
    #"Changed Date" = Table.TransformColumnTypes(#"Changed Type",{{"Date", type date}, {"Date_Added", type date}}),
    #"Added Index Key" = Table.AddColumn(#"Changed Date", "Key", each Text.Combine({[Company], "|", Date.ToText([Date], "yyyy"),Date.ToText([Date], "MM"), Date.ToText([Date], "dd")})),
    #"Renamed Columns1" = Table.RenameColumns(#"Added Index Key",{{"Company", "company"}, {"Industry", "industry"}, {"Laid_Off_Count", "total_laid_off"}, {"Date", "date"}, {"Source", "source"}, {"Funds_Raised", "funds_raised"}, {"Stage", "stage"}, {"Date_Added", "date_added"}, {"Country", "country"}, {"Percentage", "percentage_laid_off"}, {"Location", "location"}})
in
    #"Renamed Columns1"
```

##### Merged table
```css
let
    Source = Table.Combine({layoffs_source2, layoffs_source1}),
    #"Reordered Columns" = Table.ReorderColumns(Source,{"Key", "company", "city", "industry", "total_laid_off", "date", "source", "funds_raised", "stage", "date_added", "country", "percentage_laid_off", "location", "Stage Ranking"}),
    #"Removed Duplicates" = Table.Distinct(#"Reordered Columns", {"Key"})
in
    #"Removed Duplicates"
```

## Relationship
Tables | Relationship
---- | -----
**Layoffs** / **DateTable** | Many to 1

----------

## Reports

### 1. *Layoffs Analysis* Page
![Screenshot](../_Asset%20Library/Layoffs_Screenshot.png)

- Map - Geo Graphic view by layoff number per city / country
- Ribbon chart - Count of company by Country
- Ribbon chart - number of Layoffs by Country
- Line and Stacked Column Chart - Count of company and number of Layoffs by Company Stage and country
- Scatter Chart - Count of company and number of layoffs by Industry
- Stacked Bar Chart - number of Layoffs by company and country

### 2. *Layoffs Analysis* Mobile View
![Screenshot](../_Asset%20Library/Layoffs_MobileView.png)

### 3. *Unicorn Card* tooltips Page
![Screenshot](../_Asset%20Library/Layoffs_Card.png)
----------

## Reference

### Power BI/Query Reference

- [Text/csv Connector Reference](https://learn.microsoft.com/en-us/power-query/connectors/text-csv)
- [Create tooltips based on report pages](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-tooltips?tabs=powerbi-desktop)
