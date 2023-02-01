---
title: GDP per capita analysis
author: Johnney Cao
date updated: 2023-1-17
keyword: [Worldbank API, GDP, GNI, parameter, web connector, xml, expand table, expand table columns, html color, table reference, DAX, related table]
---

# Analysis of GDP/GNI per capita in Countries Using Wordbank Data

----------

[PBI Download Link](../_Asset%20Library/Source_Files/WorldBank.pbix)

## Parameters

- **StarDate**: Required, Type as <em> Date </em>

----------

## Data Tables

### 1. Basic Tables

#### Tables 

- **Date** Table

- **Year** Table

- **LastRefreshed** Table

### 2.  <em> Country WorldBank </em> Table

#### Data Source
> [http://api.worldbank.org/v2/country/](http://api.worldbank.org/v2/country/)

#### Steps
1. Retrieve data from [Worldbank Country API](http://api.worldbank.org/v2/country/) in XML format;
1. Expand **Region** column

#### Power Query Sample Script
```css
let
    Source = Xml.Tables(Web.Contents("http://api.worldbank.org/v2/country/" & "?per_page=500")),
    country = Source{0}[country],
    #"Sorted Rows" = Table.Sort(country,{{"iso2Code", Order.Ascending}}),
    #"Expanded region" = Table.ExpandTableColumn(#"Sorted Rows", "region", {"Element:Text", "Attribute:id", "Attribute:iso2code"}, {"region.Element:Text", "region.Attribute:id", "region.Attribute:iso2code"})
in
    #"Expanded region"
```

### 3. <em> Country Master </em> Table

#### Dependency
- **Country WorldBank** Table

#### Steps
1. Load data from **Country WorldBank** Table, and filter out those **region.Element:Text** is <em> empty </em> or <em> Aggregates</em>;
1. **AdminRegion**, **IncomeLevel**, **LendingType**, **CapitalCity**, **Longitude**, **Latitude**;
1. Add color columns for **IncomeLevel**, **LendingType**

    Note: [Color Name](https://htmlcolorcodes.com/color-names/)

#### Power Query Sample Script
```css
let
    Source = Country_WorldBank,
    #"Filtered Rows" = Table.SelectRows(Source, each ([#"region.Element:Text"] <> null and [#"region.Element:Text"] <> "" and [#"region.Element:Text"] <> "Aggregates")),
    #"Renamed Columns" = Table.RenameColumns(#"Filtered Rows",{{"iso2Code", "Country2Code"}, {"name", "CountryName"}, {"region.Element:Text", "RegionName"}, {"region.Attribute:id", "Region3Code"}, {"region.Attribute:iso2code", "Region2Code"}, {"Attribute:id", "Country3Code"}}),
    #"Expanded adminregion" = Table.ExpandTableColumn(#"Renamed Columns", "adminregion", {"Attribute:id", "Attribute:iso2code"}, {"AdminRegion3Code", "AdminRegion2Code"}),
    #"Expanded incomeLevel" = Table.ExpandTableColumn(#"Expanded adminregion", "incomeLevel", {"Element:Text", "Attribute:id", "Attribute:iso2code"}, {"IncomeLevel", "IncomeLevel3Code", "IncomeLevel2Code"}),
    #"Expanded lendingType" = Table.ExpandTableColumn(#"Expanded incomeLevel", "lendingType", {"Element:Text", "Attribute:id", "Attribute:iso2code"}, {"LendingType", "LendingType3Code", "LendingType2Code"}),
    #"Expanded capitalCity" = Table.ExpandTableColumn(#"Expanded lendingType", "capitalCity", {"Element:Text"}, {"CapitalCity"}),
    #"Expanded longitude" = Table.ExpandTableColumn(#"Expanded capitalCity", "longitude", {"Element:Text"}, {"Longitude"}),
    #"Expanded latitude" = Table.ExpandTableColumn(#"Expanded longitude", "latitude", {"Element:Text"}, {"Latitude"}),
    #"Replaced Value" = Table.ReplaceValue(#"Expanded latitude"," income","",Replacer.ReplaceText,{"IncomeLevel"}),
    #"Added IncomeLevelColor" = Table.AddColumn(#"Replaced Value", "IncomeLevelColor", each if [IncomeLevel3Code] = "HIC" then "Light Green" else if [IncomeLevel3Code] = "UMC" then "Light Yellow" else if [IncomeLevel3Code] = "LMC" then "Peach Puff" else if [IncomeLevel3Code] = "LIC" then "Light Salmon" else null),
    #"Added RegionColor" = Table.AddColumn(#"Added IncomeLevelColor", "RegionColor", each if Text.StartsWith([RegionName], "East Asia") then "Salmon" else if Text.StartsWith([RegionName], "Europe") then "Plum" else if Text.StartsWith([RegionName], "North America") then "SkyBlue" else if Text.StartsWith([RegionName], "Latin America") then "LemonChiffon" else if Text.StartsWith([RegionName], "Middle East") then "Tan" else if Text.StartsWith([RegionName], "South Asia") then "PaleGreen" else if Text.StartsWith([RegionName], "Sub-Saharan") then "Silver" else null),
    #"Reordered Columns" = Table.ReorderColumns(#"Added RegionColor",{"CountryName", "Country3Code", "Country2Code", "RegionName", "Region3Code", "Region2Code", "RegionColor", "AdminRegion3Code", "AdminRegion2Code", "IncomeLevel", "IncomeLevel3Code", "IncomeLevel2Code", "IncomeLevelColor", "LendingType", "LendingType3Code", "LendingType2Code", "CapitalCity", "Longitude", "Latitude"}),
    #"Sorted Rows" = Table.Sort(#"Reordered Columns",{{"CountryName", Order.Ascending}})
in
    #"Sorted Rows"
```

#### Extra column / measure
- GDP (Billion US$) PY:
    > = CALCULATE(AVERAGE('CountryDetail'[GDP (Billion US$)]),'CountryDetail'[Year]=MAX('CountryDetail'[Year]))
- GNI (Billion US$) PY:
    > = CALCULATE(AVERAGE('CountryDetail'[GNI (Billion US$)]),'CountryDetail'[Year]=MAX('CountryDetail'[Year]))
- Population PY:
    > = CALCULATE(AVERAGE('CountryDetail'[Population]),'CountryDetail'[Year]=MAX('CountryDetail'[Year]))
- GDP per capita PY:
    > = CALCULATE(AVERAGE('CountryDetail'[GDP per capita]),'CountryDetail'[Year]=MAX('CountryDetail'[Year]))

### 4. <em> Region Master </em> Table

#### Dependency
- **Country WorldBank** Table

#### Steps
1. Load data from **Country WorldBank** Table, and filter on **region.Element:Text** is <em> Aggregates </em>;
1. Remove other columns

#### Power Query Sample Script
```css
let
    Source = Country_WorldBank,
    #"Filtered Rows" = Table.SelectRows(Source, each ([#"region.Element:Text"] = "Aggregates")),
    #"Removed Columns" = Table.RemoveColumns(#"Filtered Rows",{"region.Element:Text", "region.Attribute:id", "region.Attribute:iso2code", "adminregion", "incomeLevel", "lendingType", "capitalCity", "longitude", "latitude"}),
    #"Renamed Columns" = Table.RenameColumns(#"Removed Columns",{{"iso2Code", "Region2Code"}, {"name", "RegionName"}, {"Attribute:id", "Region3Code"}}),
    #"Reordered Columns" = Table.ReorderColumns(#"Renamed Columns",{"RegionName", "Region2Code", "Region3Code"})
in
    #"Reordered Columns"
```

### 5. WorldBank <em> Country GDP </em> Table

#### Data Source
> [http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD](http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD)

#### Dependency
- **Year** Table

#### Steps
1. Calculate the <em> startYear </em> and <em> endYear </em> from **Year** Table use 'List.Min' and 'List.Max' functions;
1. Retrieve the data from [Worldbank GDP Data API](http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD) in XML format;
1. Expand <em> country </em> columns;
1. Convert <em> GDP US$ </em> column to <em> GDP Billion US$ </em>


#### Power Query Sample Script
```css
let
    startYear=Text.From(List.Min(YearTable[Year])),
    endYear=Text.From(List.Max(YearTable[Year])),
    Source = Xml.Tables(Web.Contents("http://api.worldbank.org/v2/country/all/indicator/" & "NY.GDP.MKTP.CD" & "?date=" & startYear & ":" & endYear & "&format=xml" & "&per_page=20000")),
    data = Source{0}[data],
    #"Expanded country" = Table.ExpandTableColumn(data, "country", {"Element:Text", "Attribute:id"}, {"Country Name", "country Code"}),
    #"Renamed GDP" = Table.RenameColumns(#"Expanded country",{{"countryiso3code", "Country ISO"}, {"date", "Year"}, {"value", "GDP (current US$)"}}),
    #"Removed Columns" = Table.RemoveColumns(#"Renamed GDP",{"unit", "obs_status", "decimal", "indicator"}),
    #"Changed Type" = Table.TransformColumnTypes(#"Removed Columns",{{"GDP (current US$)", Int64.Type}, {"Year", Int64.Type}}),
    #"Divided GDP Column" = Table.TransformColumns(#"Changed Type", {{"GDP (current US$)", each _ / 1000000000, type number}}),
    #"Renamed GDP 1" = Table.RenameColumns(#"Divided GDP Column",{{"GDP (current US$)", "GDP (Billion US$)"}})
in
    #"Renamed GDP 1"
```

### 6. WorldBank <em> Country GNI </em> Table

#### Data Source
> [http://api.worldbank.org/v2/country/all/indicator/NY.GNP.MKTP.CD](http://api.worldbank.org/v2/country/all/indicator/NY.GNP.MKTP.CD)

#### Dependency
- **Year** Table

#### Steps
1. Calculate the <em> startYear </em> and <em> endYear </em> from **Year** Table use 'List.Min' and 'List.Max' functions;
1. Retrieve the data from [Worldbank GNI Data API](http://api.worldbank.org/v2/country/all/indicator/NY.GNP.MKTP.CD) in XML format;
1. Expand <em> country </em> columns;
1. Convert <em> GNI US$ </em> column to <em> GDP Billion US$ </em>

#### Power Query Sample Script
```css
let
    startYear=Text.From(List.Min(YearTable[Year])),
    endYear=Text.From(List.Max(YearTable[Year])),
    Source = Xml.Tables(Web.Contents("http://api.worldbank.org/v2/country/all/indicator/" & "NY.GNP.MKTP.CD" & "?date=" & startYear & ":" & endYear & "&format=xml" & "&per_page=20000")),
    data = Source{0}[data],
    #"Expanded country" = Table.ExpandTableColumn(data, "country", {"Element:Text", "Attribute:id"}, {"Country Name", "country Code"}),
    #"Renamed GNI" = Table.RenameColumns(#"Expanded country",{{"countryiso3code", "Country ISO"}, {"date", "Year"}, {"value", "GNI (current US$)"}}),
    #"Removed Columns" = Table.RemoveColumns(#"Renamed GNI",{"unit", "obs_status", "decimal", "indicator"}),
    #"Changed Type" = Table.TransformColumnTypes(#"Removed Columns",{{"GNI (current US$)", Int64.Type}, {"Year", Int64.Type}}),
    #"Divided GNI Column" = Table.TransformColumns(#"Changed Type", {{"GNI (current US$)", each _ / 1000000000, type number}}),
    #"Renamed GNI 1" = Table.RenameColumns(#"Divided GNI Column",{{"GNI (current US$)", "GNI (Billion US$)"}})
in
    #"Renamed GNI 1"
```

### 7. WorldBank <em> Country Population </em> Table

#### Data Source
> [http://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL](http://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL)

#### Dependency
- **Year** Table

#### Steps
1. Calculate the <em> startYear </em> and <em> endYear </em> from **Year** Table use 'List.Min' and 'List.Max' functions;
1. Retrieve the data from [Worldbank Population Data API](http://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL) in XML format;
1. Expand <em> indicator </em> and <em> country </em> 


#### Power Query Sample Script
```css
let
    startYear=Text.From(List.Min(YearTable[Year])),
    endYear=Text.From(List.Max(YearTable[Year])),
    Source = Xml.Tables(Web.Contents("http://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?date=" & startYear & ":" & endYear & "&format=xml&per_page=20000")),
    data = Source{0}[data],
    #"Expanded country" = Table.ExpandTableColumn(data, "country", {"Element:Text", "Attribute:id"}, {"Country Name", "country Code"}),
    #"Renamed Columns" = Table.RenameColumns(#"Expanded country",{{"countryiso3code", "Country ISO"}, {"date", "Year"}, {"value", "Population"}}),
    #"Removed Columns" = Table.RemoveColumns(#"Renamed Columns",{"unit", "obs_status", "decimal", "indicator"}),
    #"Changed Type" = Table.TransformColumnTypes(#"Removed Columns",{{"Population", Int64.Type}, {"Year", Int64.Type}}),
    #"Filtered Rows" = Table.SelectRows(#"Changed Type", each [Country ISO] <> null and [Country ISO] <> "")
in
    #"Filtered Rows"
```

### 8. WorldBank <em> Country Detail </em> Table

#### Dependency
- **Country GDP** Table
- **Country GNI** Table
- **Country Population** Table

#### Steps
1. Merge three table using **country code", "Country ISO" and "Year" columns;
1. Expand "GNI Billion US$" and "Population" Column;
1. Filter out empty **Country ISO" records;
1. Add *GDP per capita" using formula

    > [#"GDP (Billion US$)"]* 1000000000 /[Population]
1. Merge with **Country WorldBank** Table, and filter out <em> Aggregates </em> records

#### Power Query Sample Script
```css
let
    Source = Table.NestedJoin(CountryGDP, {"country Code", "Country ISO", "Year"}, CountryGNI, {"country Code", "Country ISO", "Year"}, "CountryGNI", JoinKind.FullOuter),
    #"Merged Population" = Table.NestedJoin(Source, {"country Code", "Country ISO", "Year"}, CountryPopulation, {"country Code", "Country ISO", "Year"}, "CountryPopulation", JoinKind.FullOuter),
    #"Expanded CountryGNI" = Table.ExpandTableColumn(#"Merged Population", "CountryGNI", {"GNI (Billion US$)"}, {"GNI (Billion US$)"}),
    #"Expanded CountryPopulation" = Table.ExpandTableColumn(#"Expanded CountryGNI", "CountryPopulation", {"Population"}, {"Population"}),
    #"Filtered Rows" = Table.SelectRows(#"Expanded CountryPopulation", each [Country ISO] <> null and [Country ISO] <> ""),
    #"Added Custom" = Table.AddColumn(#"Filtered Rows", "GDP per capita", each [#"GDP (Billion US$)"]* 1000000000 /[Population]),
    #"Merged CountryList" = Table.NestedJoin(#"Added Custom", {"country Code", "Country ISO"}, Country_WorldBank, {"iso2Code", "Attribute:id"}, "Country_WorldBank", JoinKind.LeftOuter),
    #"Expanded Country_WorldBank" = Table.ExpandTableColumn(#"Merged CountryList", "Country_WorldBank", {"region.Element:Text"}, {"Regions"}),
    #"Filter Out Aggregates" = Table.SelectRows(#"Expanded Country_WorldBank", each ([Regions] <> "Aggregates")),
    #"Changed Type" = Table.TransformColumnTypes(#"Filter Out Aggregates",{{"GDP per capita", type number}, {"Year", type number}, {"GDP (Billion US$)", type number}, {"GNI (Billion US$)", type number}, {"Population", type number}})
in
    #"Changed Type"
```
#### Extra column / measure
- Income Level
    > = RELATED(CountryMaster[IncomeLevel]) 

----------

## Relationship
### Dependency Map
![Screenshot](../_Asset%20Library/WorldBank_Dependencies.png)
Tables | Relationship
---- | -----
**CountryDetail** / **CountryMaster** |Many to 1
**CountryMaster** / **RegionMaster** | Many to 1
**CountryMaster** / **Year** | Many to 1

----------

## Reports

### 1. **World** Page
![Screenshot](../_Asset%20Library/WorldBank_WorldMap_Screenshot.png)

- Cards - Total Countries, Population, GDP and GNI as of last update
- Map - Geo Graphic view by country GDP value and income level
- Donut - GDP by income level
- Stacked Bar Chart - Count of countries by lending type
- Sankey - flow between regions and income type

### 2. **GDP** Page
![Screenshot](../_Asset%20Library/WorldBank_GDP_Screenshot.png)
- Scatter chart - YoY GDP per Capita vs Population changes for Top 25 Countires
- Table - List of all countries with ISO3code, Income Level, GDP, GNI, Population, GDP per capita, and sparklines for GDP and Population

----------

## Reference

### HTML Color Name
- [Color Name](https://htmlcolorcodes.com/color-names/)

### The World Bank

- [Country API Queries](https://datahelpdesk.worldbank.org/knowledgebase/articles/898590-country-api-queries)
- [How does the World Bank classify countries?](https://datahelpdesk.worldbank.org/knowledgebase/articles/378834-how-does-the-world-bank-classify-countries)
- [World Bank Indicators API Documentation](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-getting-started-with-the-world-bank-data-api)
