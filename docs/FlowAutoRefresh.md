---
title: Auto refresh and publish report to default workspace using Power Automate Desktop
author: Johnney Cao
date updated: 2023-3-31
keyword: [Power Automate Desktop, Flow, Power BI]
---

# Auto refresh and publish report to default workspace using Power Automate Desktop

----------

## Variables

### Input / output variables

1. **FileFolder**: Required, Data Type as *text*
1. **FileName**: Required, Data Type as *text*

### Flow variables
1. **AppProcessId**, used in UI elements, Elements.Ordinal = %AppProcessId%
    
    ![Screenshot](../_Asset%20Library/AutoRefreshWindowUIElement.png)

1. **FullName**, Combine **FileFolder** and **FileName** above


----------

## Flows

### 1. Refresh Power BI Report and Publsih to Cloud

#### Steps
1. Set variable **FullName**;

    >FullName =  %FileFolder%%FileName%.PBIX
1. Run the Power BI report use default application
1. Wait for the report to open, and **Refresh** button is *Enabled*, and then click on **Refresh** button to refresh data;
1. Wait **Refresh** popup is closed, and then click on **Save** button to save the changes;
1. Wait **Publish** button is *Enabled*, and then click on **Publish** button to start publishing report; 
1. Wait **Publish to Power BI** form is popup, and click on **Select** button to use the default workspace;
1. Wait **Replace this dataset** form is popup, and click on **Replace** button to replace the exiting dataset. On error, skip the step and continue next action;
1. Wait **Publishing to Power BI** form is popup, and then click on the URI to open the report from Power BI Service;
1. Close Power BI Desktop.

    ![Screenshot](../_Asset%20Library/AutoRefreshFlow.png)


----------

## Reference

### Power Automate Reference

1. [Power Automate Desktop](https://aka.ms/pad)