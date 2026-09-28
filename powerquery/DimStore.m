let
    Source = Csv.Document(File.Contents(ProjectPath & "Data\DimStore.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"StoreID", type text},
        {"StoreName", type text},
        {"FranchiseeID", type text},
        {"Format", type text},
        {"LocationType", type text},
        {"City", type text},
        {"Voivodeship", type text},
        {"RegionID", type text},
        {"Region", type text},
        {"Latitude", type number},
        {"Longitude", type number},
        {"SalesAreaSqm", Int64.Type},
        {"OpeningDate", type date},
        {"OpeningYear", Int64.Type},
        {"ClosingDate", type date},
        {"Status", type text},
        {"StoreCohort", type text},
        {"IsSeasideCity", Int64.Type},
        {"OperatingModel", type text}
    }, "en-US")
in
    Types
