# Unicorn Analysis

----------

## Parameters

1. **StarDate**: Required, Type as <em> Date </em>

----------

## Data Tables

### 1 Basic Tables

#### Tables 
[Basic Data](./BasicData.md)

**Date** Table

**Year** Table

**LastRefreshed** Table

### 2 <em> Country / Region </em> Table

#### Data Source
- [Worldbank Country API](http://api.worldbank.org/v2/country/)

#### Steps
1. Pull data from [Worldbank Country API](http://api.worldbank.org/v2/country/);
1. Expand **Region**, and filter out those <em> empty </em> and <em> Aggregates </em>
1. **AdminRegion**, **IncomeLevel**, **LendingType**, **CapitalCity**, **Longitude**, **Latitude**
1. Add color columns for **IncomeLevel**, **LendingType**

#### Power Query Sample Scripts
```css
let
    Source = Xml.Tables(Web.Contents("http://api.worldbank.org/v2/country/" & "?per_page=500")),
    country = Source{0}[country],
    #"Expanded region" = Table.ExpandTableColumn(country, "region", {"Element:Text", "Attribute:id", "Attribute:iso2code"}, {"region.Element:Text", "region.Attribute:id", "region.Attribute:iso2code"}),
    #"Filtered Rows" = Table.SelectRows(#"Expanded region", each ([#"region.Element:Text"] <> null and [#"region.Element:Text"] <> "" and [#"region.Element:Text"] <> "Aggregates")),
    #"Renamed Columns" = Table.RenameColumns(#"Filtered Rows",{{"iso2Code", "Country2Code"}, {"name", "CountryName"}, {"region.Element:Text", "RegionName"}, {"region.Attribute:id", "Region3Code"}, {"region.Attribute:iso2code", "Region2Code"}, {"Attribute:id", "Country3Code"}}),
    #"Expanded adminregion" = Table.ExpandTableColumn(#"Renamed Columns", "adminregion", {"Attribute:id", "Attribute:iso2code"}, {"AdminRegion3Code", "AdminRegion2Code"}),
    #"Expanded incomeLevel" = Table.ExpandTableColumn(#"Expanded adminregion", "incomeLevel", {"Element:Text", "Attribute:id", "Attribute:iso2code"}, {"IncomeLevel", "IncomeLevel3Code", "IncomeLevel2Code"}),
    #"Expanded lendingType" = Table.ExpandTableColumn(#"Expanded incomeLevel", "lendingType", {"Element:Text", "Attribute:id", "Attribute:iso2code"}, {"LendingType", "LendingType3Code", "LendingType2Code"}),
    #"Expanded capitalCity" = Table.ExpandTableColumn(#"Expanded lendingType", "capitalCity", {"Element:Text"}, {"CapitalCity"}),
    #"Expanded longitude" = Table.ExpandTableColumn(#"Expanded capitalCity", "longitude", {"Element:Text"}, {"Longitude"}),
    #"Expanded latitude" = Table.ExpandTableColumn(#"Expanded longitude", "latitude", {"Element:Text"}, {"Latitude"}),
    #"Replaced Value" = Table.ReplaceValue(#"Expanded latitude"," income","",Replacer.ReplaceText,{"IncomeLevel"}),
    #"Added IncomeLevelColor" = Table.AddColumn(#"Replaced Value", "IncomeLevelColor", each if [IncomeLevel3Code] = "HIC" then "Light Green" else if [IncomeLevel3Code] = "UMC" then "Light Blue" else if [IncomeLevel3Code] = "LMC" then "Light Yellow" else if [IncomeLevel3Code] = "LIC" then "Light Red" else null),
    #"Added RegionColor" = Table.AddColumn(#"Added IncomeLevelColor", "RegionColor", each if Text.StartsWith([RegionName], "East Asia") then "Salmon" else if Text.StartsWith([RegionName], "Europe") then "Plum" else if Text.StartsWith([RegionName], "North America") then "SkyBlue" else if Text.StartsWith([RegionName], "Latin America") then "LemonChiffon" else if Text.StartsWith([RegionName], "Middle East") then "Tan" else if Text.StartsWith([RegionName], "South Asia") then "PaleGreen" else if Text.StartsWith([RegionName], "Sub-Saharan") then "Silver" else null),
    #"Reordered Columns" = Table.ReorderColumns(#"Added RegionColor",{"CountryName", "Country3Code", "Country2Code", "RegionName", "Region3Code", "Region2Code", "RegionColor", "AdminRegion3Code", "AdminRegion2Code", "IncomeLevel", "IncomeLevel3Code", "IncomeLevel2Code", "IncomeLevelColor", "LendingType", "LendingType3Code", "LendingType2Code", "CapitalCity", "Longitude", "Latitude"}),
    #"Sorted Rows" = Table.Sort(#"Reordered Columns",{{"RegionName", Order.Ascending}, {"CountryName", Order.Ascending}})
in
    #"Sorted Rows"
```

### 2 <em> Unicorn </em> Master Table

#### Data Source
- [CBInsights](https://www.cbinsights.com/research-unicorn-companies)

#### Steps

1. Pull data from [CBInsights](https://www.cbinsights.com/research-unicorn-companies) and extracted table from HTML;
1. Add a Index column <em> UnicornId </em>;
1. Add a merged column for City and Country
    
    >Table.AddColumn(#"Reordered Columns", "City, Country", each Text.Combine({[City], [Country]}, ", "), type text)

#### Power Query Sample Scripts
```css
let
    Source = Web.BrowserContents("https://www.cbinsights.com/research-unicorn-companies"),
    #"Extracted Table From Html" = Html.Table(Source, {{"Column1", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(1)"}, {"Column2", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(2)"}, {"Column3", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(3)"}, {"Column4", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(4)"}, {"Column5", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(5)"}, {"Column6", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(6)"}, {"Column7", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(7)"}}, [RowSelector="TABLE.sortable-theme-bootstrap > * > TR"]),
    #"Promoted Headers" = Table.PromoteHeaders(#"Extracted Table From Html", [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Company", type text}, {"Valuation ($B)", type number}, {"Date Joined", type date}, {"Country", type text}, {"City", type text}, {"Industry", type text}, {"Select Investors", type text}}),
    #"Added Index" = Table.AddIndexColumn(#"Changed Type", "UnicornId", 1, 1, Int64.Type),
    #"Inserted Merged City Country" = Table.AddColumn(#"Added Index", "City, Country", each Text.Combine({[City], ", ", [Country]}), type text),
    #"Reordered Columns" = Table.ReorderColumns(#"Inserted Merged City Country",{"UnicornId", "Company", "Valuation ($B)", "Date Joined", "Country", "City", "City, Country", "Industry", "Select Investors"})
in
    #"Reordered Columns"
```

### 3 <em> Unicorn Investor </em>

----------

## Relationship

----------

## Reports

----------

## Reference

### Power Query Reference

### The World Bank

- [Country API Queries](https://datahelpdesk.worldbank.org/knowledgebase/articles/898590-country-api-queries)
- [World Bank Country and Lending Groups](https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups)