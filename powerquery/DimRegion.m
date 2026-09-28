let
    Source = Csv.Document(File.Contents(ProjectPath & "Data\DimRegion.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"RegionID", type text},
        {"Region", type text},
        {"RegionalDirector", type text},
        {"RegionalHQ", type text}
    }, "en-US")
in
    Types
