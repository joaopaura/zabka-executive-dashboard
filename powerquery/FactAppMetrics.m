let
    Source = Csv.Document(File.Contents(ProjectPath & "Data\FactAppMetrics.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"MonthStart", type date},
        {"RegionID", type text},
        {"RegisteredUsers", Int64.Type},
        {"MonthlyActiveUsers", Int64.Type},
        {"NewRegistrations", Int64.Type},
        {"CouponsRedeemed", Int64.Type},
        {"AppRating", type number}
    }, "en-US")
in
    Types
