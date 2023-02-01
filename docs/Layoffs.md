---
title: tech layoff analysis
author: Johnney Cao
date updated: 2023-1-27
keyword: [tech layoffs, parameter, csv]
---

# Analysis of Tech Layoffs Data

----------

[PBI Download Link](../_Asset%20Library/Source_Files/Layoffs.pbix)

## Parameters

- **StarDate**: Required, Type as *Date*

----------

## Data Tables

### 1. Basic Tables

#### Tables 

- **Date** Table

- **Year** Table

- **LastRefreshed** Table

### 2. *Layoffs* Master Table

#### Data Source
 [Download link (Kaggle)](https://www.kaggle.com/datasets/swaptr/layoffs-2022)

*Some data such as the sources, list of employees laid off and date of addition has been omitted here and the complete data can be found on [Layoffs.fyi](https://layoffs.fyi/). Credits: Roger Lee*

#### Steps

1. Manual download the csv file from [Kaggle](https://www.kaggle.com/datasets/swaptr/layoffs-2022) to local folder, e.g *c:\Downloads*;
1. Retrieve the data from downloaded csv file; 
1. Promote first line as header;
1. Change **percentage_laid_off** to *Percentage* type;
1. Trim and clean all the text fields;
1. Replace empty value in **industry** to *Other*;
1. Add a **location** column from *city* and *country*
1. Remove the duplicate record from table.


#### Power Query Sample Script
```css
let
    Source = Csv.Document(File.Contents("C:\Downloads\layoffs.csv"),[Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Filtered Rows" = Table.SelectRows(#"Promoted Headers", each true),
    #"Changed Type" = Table.TransformColumnTypes(#"Filtered Rows",{{"company", type text}, {"location", type text}, {"industry", type text}, {"total_laid_off", Int64.Type}, {"percentage_laid_off", Percentage.Type}, {"date", type date}, {"stage", type text}, {"country", type text}, {"funds_raised", Int64.Type}}),
    #"Replaced Other Industry" = Table.ReplaceValue(#"Changed Type","","Other",Replacer.ReplaceValue,{"industry"}),
    #"Replaced Unknown stage" = Table.ReplaceValue(#"Replaced Other Industry","","Unknown",Replacer.ReplaceValue,{"stage"}),
    #"Trimmed Text" = Table.TransformColumns(#"Replaced Unknown stage",{{"company", Text.Trim, type text}, {"location", Text.Trim, type text}, {"industry", Text.Trim, type text}, {"country", Text.Trim, type text}, {"stage", Text.Trim, type text}}),
    #"Cleaned Text" = Table.TransformColumns(#"Trimmed Text",{{"company", Text.Clean, type text}, {"location", Text.Clean, type text}, {"industry", Text.Clean, type text}, {"country", Text.Clean, type text}, {"stage", Text.Clean, type text}}),
    #"Renamed Columns" = Table.RenameColumns(#"Cleaned Text",{{"location", "city"}}),
    #"Inserted Merged Column" = Table.AddColumn(#"Renamed Columns", "location", each Text.Combine({[city], ", ", [country]}), type text),
    #"Removed Duplicates" = Table.Distinct(#"Inserted Merged Column", {"company", "total_laid_off", "percentage_laid_off", "date", "location"}),
    #"Added Stage Ranking" = Table.AddColumn(#"Removed Duplicates", "Stage Ranking", each if [stage] = "IPO" then 90 else if [stage] = "Private Equity" then 80 else if [stage] = "Seed" then 40 else if [stage] = "Acquired" then 30 else if [stage] = "Merged" then 30 else if [stage] = "Subsidiary" then 20 else if [stage] = "Series A" then 50 else if [stage] = "Series B" then 50 else if [stage] = "Series C" then 50 else if Text.StartsWith([stage], "Series") then 60 else 0)
in
    #"Added Stage Ranking"
```

## Relationship
Tables | Relationship
---- | -----
Layoffs Master / Date Table | Many to 1

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
