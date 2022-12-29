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
    
    `Table.AddColumn(#"Reordered Columns", "City, Country", each Text.Combine({[City], [Country]}, ", "), type text)` 

### 3 <em> Unicorn Investor </em>

----------

## Relationship

----------

## Reports

----------

## Reference

### Power Query Reference