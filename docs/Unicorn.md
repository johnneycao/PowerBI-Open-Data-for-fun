# Unicorn Analysis

----------

[PBI Download Link](../_Asset%20Library/Source_Files/Unicorn.pbix)

## Parameters

- **StarDate**: Required, Type as <em> Date </em>

----------

## Data Tables

### 1. Basic Tables

#### Tables 

- **Date** Table

- **Year** Table

- **LastRefreshed** Table

### 2. <em> Country / Region </em> Master Table

#### Data Source
- [Worldbank Country API](http://api.worldbank.org/v2/country/)

#### Steps
1. Pull data from [Worldbank Country API](http://api.worldbank.org/v2/country/);
1. Expand **Region**, and filter out those <em> empty </em> and <em> Aggregates </em>;
1. **AdminRegion**, **IncomeLevel**, **LendingType**, **CapitalCity**, **Longitude**, **Latitude**;
1. Add color columns for **IncomeLevel**, **LendingType**

#### Power Query Sample Script
```css
let
    Source = Xml.Tables(Web.Contents("http://api.worldbank.org/v2/country/" & "?per_page=1000")),
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
    #"Sorted Rows" = Table.Sort(#"Reordered Columns",{{"CountryName", Order.Ascending}})
in
    #"Sorted Rows"
```

### 3. <em> Unicorn </em> Master Table

#### Data Source
- [CBInsights](https://www.cbinsights.com/research-unicorn-companies)

#### Steps

1. Pull data from [CBInsights](https://www.cbinsights.com/research-unicorn-companies) and extracted table from HTML;
1. Add a Index column <em> UnicornId </em>;
1. Clean country name in **Country** column;
1. Merge query from **CountryMaster** table above, and expand ISO code, Regions **IncomeLevel**, **LendingType**, **CapitalCity** columns
1. Add a merged column for City and Country, and Trim the value
    
    >Table.AddColumn(#"Expanded CountryMaster", "City, Country", each Text.Combine({[City], ", ", [Country3Code]}), type text)

#### Power Query Sample Script
```css
let
    Source = Web.BrowserContents("https://www.cbinsights.com/research-unicorn-companies"),
    #"Extracted Table From Html" = Html.Table(Source, {{"Column1", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(1)"}, {"Column2", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(2)"}, {"Column3", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(3)"}, {"Column4", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(4)"}, {"Column5", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(5)"}, {"Column6", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(6)"}, {"Column7", "TABLE.sortable-theme-bootstrap > * > TR > :nth-child(7)"}}, [RowSelector="TABLE.sortable-theme-bootstrap > * > TR"]),
    #"Promoted Headers" = Table.PromoteHeaders(#"Extracted Table From Html", [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{{"Company", type text}, {"Valuation ($B)", type number}, {"Date Joined", type date}, {"Country", type text}, {"City", type text}, {"Industry", type text}, {"Select Investors", type text}}),
    #"Added Index" = Table.AddIndexColumn(#"Changed Type", "UnicornId", 1, 1, Int64.Type),
    #"Replaced Hong Kong" = Table.ReplaceValue(#"Added Index","Hong Kong","Hong Kong SAR, China",Replacer.ReplaceText,{"Country"}),
    #"Replaced Bahama" = Table.ReplaceValue(#"Replaced Hong Kong","Bahama","Bahamas, The",Replacer.ReplaceText,{"Country"}),
    #"Replaced South Korea" = Table.ReplaceValue(#"Replaced Bahama","South Korea","Korea, Rep.",Replacer.ReplaceText,{"Country"}),
    #"Replaced Czech" = Table.ReplaceValue(#"Replaced South Korea","Czech Republic","Czechia",Replacer.ReplaceText,{"Country"}),
    #"Merged Queries" = Table.NestedJoin(#"Replaced Czech", {"Country"}, CountryMaster, {"CountryName"}, "CountryMaster", JoinKind.LeftOuter),
    #"Expanded CountryMaster" = Table.ExpandTableColumn(#"Merged Queries", "CountryMaster", {"CountryName", "Country3Code", "Country2Code", "RegionName", "RegionColor", "IncomeLevel", "IncomeLevelColor", "LendingType", "CapitalCity"}, {"CountryName", "Country3Code", "Country2Code", "RegionName", "RegionColor", "IncomeLevel", "IncomeLevelColor", "LendingType", "CapitalCity"}),
    #"Inserted Merged City Country" = Table.AddColumn(#"Expanded CountryMaster", "City, Country", each Text.Combine({[City], ", ", [Country3Code]}), type text),
    #"Trimmed Text" = Table.TransformColumns(#"Inserted Merged City Country",{{"City, Country", Text.Trim, type text}}),
    #"Reordered Columns" = Table.ReorderColumns(#"Trimmed Text",{"UnicornId", "Company", "Valuation ($B)", "Date Joined", "Country", "City", "Industry", "Select Investors"}),
    #"Sorted Rows" = Table.Sort(#"Reordered Columns",{{"Date Joined", Order.Descending}, {"UnicornId", Order.Descending}})
in
    #"Sorted Rows"
```

### 4. <em> Unicorn Investor </em> Table

#### Dependency
- **Unicorn Master** Table

#### Steps
1. Reference from **Unicorn Master** Table;
1. Keep only **UnicornId**, **Company** and **Select Investors**
1. Split **Select Investors** into new rows and Trimmed the value


#### Power Query Sample Script
```css
let
    Source = #"Unicorn Master",
    #"Removed Columns" = Table.RemoveColumns(Source,{"Valuation ($B)", "Date Joined", "Country", "City", "Industry", "City, Country"}),
    #"Split Column by Delimiter" = Table.ExpandListColumn(Table.TransformColumns(#"Removed Columns", {{"Select Investors", Splitter.SplitTextByDelimiter(",", QuoteStyle.Csv), let itemType = (type nullable text) meta [Serialized.Text = true] in type {itemType}}}), "Select Investors"),
    #"Changed Type" = Table.TransformColumnTypes(#"Split Column by Delimiter",{{"Select Investors", type text}}),
    #"Trimmed Text" = Table.TransformColumns(#"Changed Type",{{"Select Investors", Text.Trim, type text}})
in
    #"Trimmed Text"
```

----------

## Relationship
- Unicorn Master / CountryMaster Table: Many to 1
- Unicorn Investor / Unicorn Master: Many to 1

----------

## Reports

### 1. <em> Unicorn Analysis </em> Page
![Screenshot](../_Asset%20Library/Unicorn_Screenshot.png)

- Cards - Total Valuation ($B), Count of Company and Count of Investors
- Map - Geo Graphic view by Count of company per city / country
- Scatter Chart - Count of company per industry by Year
- Stacked Bar Chart - Company Valuation
- Funnel - Count of company by Year
- Ribbon chart - Count of company by Country
- Line and stacked column chart - Valuation vs Count of company by Country and Income Level
- Stacked Bar Chart - Count of Company by Investor

### 2. <em> Unicorn Card </em> tooltips Page
![Screenshot](../_Asset%20Library/Unicorn_Card.png)
----------

## Reference

### The World Bank

- [Country API Queries](https://datahelpdesk.worldbank.org/knowledgebase/articles/898590-country-api-queries)
- [World Bank Country and Lending Groups](https://datahelpdesk.worldbank.org/knowledgebase/articles/906519-world-bank-country-and-lending-groups)