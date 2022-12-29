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

### 2 <em> Unicorn </em> Master Table

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