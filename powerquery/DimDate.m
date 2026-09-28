let
    Source = Csv.Document(File.Contents(ProjectPath & "Data\DimDate.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Headers, {
        {"Date", type date},
        {"DateKey", Int64.Type},
        {"Year", Int64.Type},
        {"Quarter", Int64.Type},
        {"QuarterLabel", type text},
        {"YearQuarter", type text},
        {"MonthNumber", Int64.Type},
        {"MonthName", type text},
        {"MonthShort", type text},
        {"YearMonth", type text},
        {"YearMonthNumber", Int64.Type},
        {"MonthStart", type date},
        {"ISOWeek", Int64.Type},
        {"ISOYear", Int64.Type},
        {"DayOfMonth", Int64.Type},
        {"DayOfWeekNumber", Int64.Type},
        {"DayName", type text},
        {"DayShort", type text},
        {"IsWeekend", Int64.Type},
        {"IsHoliday", Int64.Type},
        {"HolidayName", type text},
        {"IsSunday", Int64.Type},
        {"IsTradingSunday", Int64.Type},
        {"IsNonTradingSunday", Int64.Type},
        {"Season", type text},
        {"IsActualPeriod", Int64.Type}
    }, "en-US")
in
    Types
