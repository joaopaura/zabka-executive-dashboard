let
    Source = Csv.Document(File.Contents(ProjectPath & "Data\DimCategory.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"CategoryID", type text},
        {"Category", type text},
        {"CategoryGroup", type text},
        {"TargetGrossMargin", type number},
        {"IsFresh", Int64.Type},
        {"IsStrategicGrowth", Int64.Type},
        {"SortOrder", Int64.Type}
    }, "en-US")
in
    Types
