let
    Source = Csv.Document(File.Contents(ProjectPath & "Data\FactStoreOpex.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"MonthStart", type date},
        {"StoreID", type text},
        {"OpenDays", Int64.Type},
        {"RentCost", type number},
        {"EnergyCost", type number},
        {"FranchiseeCommission", type number},
        {"MarketingCost", type number},
        {"TechnologyCost", type number},
        {"OtherOpex", type number}
    }, "en-US")
in
    Types
