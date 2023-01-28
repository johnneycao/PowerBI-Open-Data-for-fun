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

- **StarDate**: Required, Type as <em> Date </em>

----------

## Data Tables

### 1. Basic Tables

#### Tables 

- **Date** Table

- **Year** Table

- **LastRefreshed** Table

### 2. <em> Layoffs </em> Master Table

#### Data Source
 [Download link (Kaggle)](https://www.kaggle.com/datasets/swaptr/layoffs-2022)

<em>Some data such as the sources, list of employees laid off and date of addition has been omitted here and the complete data can be found on [Layoffs.fyi](https://layoffs.fyi/). Credits: Roger Lee </em>

#### Steps

1. Manual download the csv file from [Kaggle](https://www.kaggle.com/datasets/swaptr/layoffs-2022) to local folder, e.g <em> c:\Downloads\ </em>;
1. Retrieve the data from downloaded csv file; 
1. Promote first line as header;
1. Change **percentage_laid_off** to <em> Percentage </em> type;
1. Trim and clean the text fields;
1. Remove the duplicate record from table;
1. Replace empty value in **industry** to <em> Other </em>

#### Power Query Sample Script
```css
let
    Source = Csv.Document(File.Contents("C:\Downloads\layoffs.csv"),[Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Filtered Rows" = Table.SelectRows(#"Promoted Headers", each true),
    #"Changed Type" = Table.TransformColumnTypes(#"Filtered Rows",{{"company", type text}, {"location", type text}, {"industry", type text}, {"total_laid_off", Int64.Type}, {"percentage_laid_off", Percentage.Type}, {"date", type date}, {"stage", type text}, {"country", type text}, {"funds_raised", Int64.Type}}),
    #"Trimmed Text" = Table.TransformColumns(#"Changed Type",{{"location", Text.Trim, type text}, {"industry", Text.Trim, type text}, {"country", Text.Trim, type text}, {"stage", Text.Trim, type text}}),
    #"Cleaned Text" = Table.TransformColumns(#"Trimmed Text",{{"location", Text.Clean, type text}, {"industry", Text.Clean, type text}, {"country", Text.Clean, type text}, {"stage", Text.Clean, type text}}),
    #"Removed Duplicates" = Table.Distinct(#"Cleaned Text", {"company", "date", "total_laid_off","country"}),
    #"Replaced Value" = Table.ReplaceValue(#"Removed Duplicates","","Other",Replacer.ReplaceValue,{"industry"})
in
    #"Replaced Value"
```

## Relationship
- Layoffs Master / Date Table: Many to 1

----------

## Reports

### 1. <em> Layoffs Analysis </em> Page
![Screenshot](../_Asset%20Library/Layoffs_Screenshot.png)

- Map - Geo Graphic view by layoff number per city / country
- Ribbon chart - Count of company by Country
- Ribbon chart - number of Layoffs by Country
- Line and Stacked Column Chart - Count of company and number of Layoffs by Company Stage and country
- Stacked Bar Chart - number of Layoffs by company and country

### 2. <em> Layoffs Analysis </em> Mobile View
![Screenshot](../_Asset%20Library/Layoffs_MobileView.png)

### 3. <em> Unicorn Card </em> tooltips Page
![Screenshot](../_Asset%20Library/Layoffs_Card.png)
----------

## Reference

### Power BI/Query Reference

- [Text/csv Connector Reference](https://learn.microsoft.com/en-us/power-query/connectors/text-csv)
- [Create tooltips based on report pages](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-tooltips?tabs=powerbi-desktop)
