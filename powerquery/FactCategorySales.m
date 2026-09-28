let
    Source = Csv.Document(File.Contents(ProjectPath & "Data\FactCategorySales.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"MonthStart", type date},
        {"StoreID", type text},
        {"CategoryID", type text},
        {"NetSales", type number},
        {"GrossProfit", type number},
        {"UnitsSold", Int64.Type},
        {"WasteValue", type number},
        {"PrivateLabelSales", type number}
    }, "en-US")
in
    Types
