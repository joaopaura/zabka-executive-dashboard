let
    Source = Csv.Document(File.Contents(ProjectPath & "Data\FactBudget.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"MonthStart", type date},
        {"RegionID", type text},
        {"CategoryID", type text},
        {"BudgetNetSales", type number},
        {"BudgetGrossProfit", type number}
    }, "en-US")
in
    Types
