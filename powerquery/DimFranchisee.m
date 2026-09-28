let
    Source = Csv.Document(File.Contents(ProjectPath & "Data\DimFranchisee.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"FranchiseeID", type text},
        {"JoinDate", type date},
        {"CohortYear", Int64.Type},
        {"TenureBand", type text},
        {"Tier", type text},
        {"NumberOfStores", Int64.Type},
        {"IsMultiStore", Int64.Type},
        {"HomeRegionID", type text}
    }, "en-US")
in
    Types
