// Combines all CSV files in the DailySales folder (one per period).
let
    Source = Folder.Files(ProjectPath & "DailySales"),
    CsvOnly = Table.SelectRows(Source, each [Extension] = ".csv" and [Attributes]?[Hidden]? <> true),
    Parsed = Table.AddColumn(CsvOnly, "Data", each Table.PromoteHeaders(
        Csv.Document([Content], [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]), [PromoteAllScalars=true])),
    Combined = Table.Combine(Parsed[Data]),
    Types = Table.TransformColumnTypes(Combined, {
        {"Date", type date}, {"StoreID", type text}, {"NetSales", type number}, {"COGS", type number},
        {"GrossProfit", type number}, {"Transactions", Int64.Type}, {"ItemsSold", Int64.Type},
        {"AppTransactions", Int64.Type}, {"AppSales", type number}, {"PromoSales", type number}
    }, "en-US")
in
    Types
