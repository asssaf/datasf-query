module Main exposing (..)

import Browser
import Html exposing (..)
import Html.Attributes exposing (..)
import Html.Events exposing (..)
import Http
import Json.Encode as Encode
import ApiClient exposing (Property, TargetLookupResult, fetchProperties, fetchTargetParcel)
import QueryBuilder exposing (QueryParams, defaultQueryParams)

-- MAIN

main : Program () Model Msg
main =
    Browser.element
        { init = init
        , update = update
        , subscriptions = subscriptions
        , view = view
        }

-- MODEL

type ViewMode
    = TableView
    | JsonView

type Status
    = Idle
    | LoadingTarget
    | LoadingResults
    | Success (List Property)
    | Failure String

type alias Model =
    { queryParams : QueryParams
    , targetParcelNumber : String
    , targetRollYear : String
    , limit : Int
    , offset : Int
    , viewMode : ViewMode
    , status : Status
    , targetPoint : Maybe (Float, Float)
    , targetArea : Maybe Float
    , targetTotalValue : Maybe Float
    , fields : List String
    , lastError : Maybe String
    }

init : () -> ( Model, Cmd Msg )
init _ =
    ( { queryParams = defaultQueryParams
      , targetParcelNumber = ""
      , targetRollYear = ""
      , limit = 100
      , offset = 0
      , viewMode = TableView
      , status = Idle
      , targetPoint = Nothing
      , targetArea = Nothing
      , targetTotalValue = Nothing
      , fields = []
      , lastError = Nothing
      }
    , Cmd.none
    )

-- UPDATE

type Msg
    = UpdateField (QueryParams -> QueryParams)
    | UpdateFields String
    | UpdateTargetParcel String
    | UpdateTargetRollYear String
    | UpdateLimit String
    | UpdateOffset String
    | SetViewMode ViewMode
    | SubmitSearch
    | GotTargetLookup (Result Http.Error (List TargetLookupResult))
    | GotResults (Result Http.Error (List Property))

update : Msg -> Model -> ( Model, Cmd Msg )
update msg model =
    case msg of
        UpdateField updater ->
            ( { model | queryParams = updater model.queryParams }, Cmd.none )

        UpdateFields val ->
            ( { model | fields = String.split "," val |> List.map String.trim |> List.filter (not << String.isEmpty) }, Cmd.none )

        UpdateTargetParcel val ->
            ( { model | targetParcelNumber = val }, Cmd.none )

        UpdateTargetRollYear val ->
            ( { model | targetRollYear = val }, Cmd.none )

        UpdateLimit val ->
            ( { model | limit = String.toInt val |> Maybe.withDefault 100 }, Cmd.none )

        UpdateOffset val ->
            ( { model | offset = String.toInt val |> Maybe.withDefault 0 }, Cmd.none )

        SetViewMode mode ->
            ( { model | viewMode = mode }, Cmd.none )

        SubmitSearch ->
            if not (String.isEmpty model.targetParcelNumber) then
                if String.isEmpty model.targetRollYear then
                    ( { model | status = Failure "When target parcel is provided, target roll year must also be specified." }, Cmd.none )
                else
                    ( { model | status = LoadingTarget }, fetchTargetParcel model.targetParcelNumber model.targetRollYear GotTargetLookup )
            else
                ( { model | status = LoadingResults, targetPoint = Nothing, targetArea = Nothing, targetTotalValue = Nothing }
                , fetchProperties Nothing Nothing Nothing model.fields model.queryParams model.limit model.offset GotResults
                )

        GotTargetLookup result ->
            case result of
                Ok [ target ] ->
                    let
                        point = target.the_geom |> Maybe.map .coordinates
                        area = case target.property_area of
                                Just a -> if a == 0 then Nothing else Just a
                                Nothing -> Nothing

                        toVal v = Maybe.withDefault 0.0 v
                        total = (toVal target.assessed_improvement_value) + (toVal target.assessed_land_value) + (toVal target.assessed_fixtures_value)
                        finalTotal = if total == 0 then Nothing else Just total
                    in
                    ( { model | status = LoadingResults, targetPoint = point, targetArea = area, targetTotalValue = finalTotal }
                    , fetchProperties point area finalTotal model.fields model.queryParams model.limit model.offset GotResults
                    )
                Ok _ ->
                    ( { model | status = Failure "Target parcel not found." }, Cmd.none )
                Err err ->
                    ( { model | status = Failure ("Failed to lookup target parcel: " ++ httpErrorToString err) }, Cmd.none )

        GotResults result ->
            case result of
                Ok properties ->
                    ( { model | status = Success properties }, Cmd.none )
                Err err ->
                    ( { model | status = Failure ("API Request failed: " ++ httpErrorToString err) }, Cmd.none )

httpErrorToString : Http.Error -> String
httpErrorToString err =
    case err of
        Http.BadUrl url -> "Bad URL: " ++ url
        Http.Timeout -> "Timeout"
        Http.NetworkError -> "Network Error"
        Http.BadStatus code -> "Bad Status: " ++ String.fromInt code
        Http.BadBody body -> "Bad Body: " ++ body

-- SUBSCRIPTIONS

subscriptions : Model -> Sub Msg
subscriptions _ =
    Sub.none

-- VIEW

view : Model -> Html Msg
view model =
    div [ class "container mt-4" ]
        [ h1 [ class "mb-4" ] [ text "SF Property Data Search" ]
        , viewForm model
        , hr [] []
        , viewStatus model
        ]

viewForm : Model -> Html Msg
viewForm model =
    div [ class "card mb-4" ]
        [ div [ class "card-body" ]
            [ Html.form [ onSubmit SubmitSearch ]
                [ div [ class "row mb-3" ]
                    [ div [ class "col-md-3" ]
                        [ label [ class "form-label", for "roll-year" ] [ text "Roll Year" ]
                        , input [ id "roll-year", class "form-control", type_ "text", value (Maybe.withDefault "" model.queryParams.roll_year), onInput (\v -> UpdateField (\q -> { q | roll_year = if v == "" then Nothing else Just v })) ] []
                        ]
                    , div [ class "col-md-3" ]
                        [ label [ class "form-label", for "bedrooms" ] [ text "Bedrooms" ]
                        , input [ id "bedrooms", class "form-control", type_ "text", value (Maybe.withDefault "" model.queryParams.bedrooms), onInput (\v -> UpdateField (\q -> { q | bedrooms = if v == "" then Nothing else Just v })) ] []
                        ]
                    , div [ class "col-md-3" ]
                        [ label [ class "form-label", for "bathrooms" ] [ text "Bathrooms" ]
                        , input [ id "bathrooms", class "form-control", type_ "text", value (Maybe.withDefault "" model.queryParams.bathrooms), onInput (\v -> UpdateField (\q -> { q | bathrooms = if v == "" then Nothing else Just v })) ] []
                        ]
                    , div [ class "col-md-3" ]
                        [ label [ class "form-label", for "parcel-number" ] [ text "Parcel Number" ]
                        , input [ id "parcel-number", class "form-control", type_ "text", value (Maybe.withDefault "" model.queryParams.parcel_number), onInput (\v -> UpdateField (\q -> { q | parcel_number = if v == "" then Nothing else Just v })) ] []
                        ]
                    ]
                , div [ class "row mb-3" ]
                    [ div [ class "col-md-3" ]
                        [ label [ class "form-label", for "area-min" ] [ text "Area Min" ]
                        , input [ id "area-min", class "form-control", type_ "text", value (Maybe.withDefault "" model.queryParams.area_min), onInput (\v -> UpdateField (\q -> { q | area_min = if v == "" then Nothing else Just v })) ] []
                        ]
                    , div [ class "col-md-3" ]
                        [ label [ class "form-label", for "area-max" ] [ text "Area Max" ]
                        , input [ id "area-max", class "form-control", type_ "text", value (Maybe.withDefault "" model.queryParams.area_max), onInput (\v -> UpdateField (\q -> { q | area_max = if v == "" then Nothing else Just v })) ] []
                        ]
                    , div [ class "col-md-3" ]
                        [ label [ class "form-label", for "date-start" ] [ text "Date Start" ]
                        , input [ id "date-start", class "form-control", type_ "date", value (Maybe.withDefault "" model.queryParams.date_start), onInput (\v -> UpdateField (\q -> { q | date_start = if v == "" then Nothing else Just v })) ] []
                        ]
                    , div [ class "col-md-3" ]
                        [ label [ class "form-label", for "date-end" ] [ text "Date End" ]
                        , input [ id "date-end", class "form-control", type_ "date", value (Maybe.withDefault "" model.queryParams.date_end), onInput (\v -> UpdateField (\q -> { q | date_end = if v == "" then Nothing else Just v })) ] []
                        ]
                    ]
                , div [ class "row mb-3" ]
                    [ div [ class "col-md-4" ]
                        [ label [ class "form-label", for "districts" ] [ text "Districts (comma separated)" ]
                        , input [ id "districts", class "form-control", type_ "text", onInput (\v -> UpdateField (\q -> { q | districts = String.split "," v |> List.map String.trim |> List.filter (not << String.isEmpty) })) ] []
                        ]
                    , div [ class "col-md-4" ]
                        [ label [ class "form-label", for "neighborhood-codes" ] [ text "Neighborhood Codes" ]
                        , input [ id "neighborhood-codes", class "form-control", type_ "text", onInput (\v -> UpdateField (\q -> { q | neighborhood_codes = String.split "," v |> List.map String.trim |> List.filter (not << String.isEmpty) })) ] []
                        ]
                    , div [ class "col-md-4" ]
                        [ label [ class "form-label", for "property-class-codes" ] [ text "Property Class Codes" ]
                        , input [ id "property-class-codes", class "form-control", type_ "text", onInput (\v -> UpdateField (\q -> { q | property_class_codes = String.split "," v |> List.map String.trim |> List.filter (not << String.isEmpty) })) ] []
                        ]
                    ]
                , div [ class "row mb-3" ]
                    [ div [ class "col-md-12" ]
                        [ label [ class "form-label", for "fields" ] [ text "Requested Fields (comma separated, leave blank for defaults)" ]
                        , input [ id "fields", class "form-control", type_ "text", value (String.join ", " model.fields), onInput UpdateFields ] []
                        ]
                    ]
                , h5 [ class "mt-4" ] [ text "Target Parcel Comparison" ]
                , div [ class "row mb-3" ]
                    [ div [ class "col-md-6" ]
                        [ label [ class "form-label", for "target-parcel" ] [ text "Target Parcel Number" ]
                        , input [ id "target-parcel", class "form-control", type_ "text", value model.targetParcelNumber, onInput UpdateTargetParcel ] []
                        ]
                    , div [ class "col-md-6" ]
                        [ label [ class "form-label", for "target-roll-year" ] [ text "Target Roll Year" ]
                        , input [ id "target-roll-year", class "form-control", type_ "text", value model.targetRollYear, onInput UpdateTargetRollYear ] []
                        ]
                    ]
                , div [ class "row mb-3" ]
                    [ div [ class "col-md-6" ]
                        [ label [ class "form-label", for "limit" ] [ text "Limit" ]
                        , input [ id "limit", class "form-control", type_ "number", value (String.fromInt model.limit), onInput UpdateLimit ] []
                        ]
                    , div [ class "col-md-6" ]
                        [ label [ class "form-label", for "offset" ] [ text "Offset" ]
                        , input [ id "offset", class "form-control", type_ "number", value (String.fromInt model.offset), onInput UpdateOffset ] []
                        ]
                    ]
                , button [ class "btn btn-primary", type_ "submit" ] [ text "Search" ]
                ]
            ]
        ]

viewStatus : Model -> Html Msg
viewStatus model =
    case model.status of
        Idle ->
            div [ class "alert alert-info" ] [ text "Enter search criteria and click Search." ]

        LoadingTarget ->
            div [ class "alert alert-warning" ] [ text "Looking up target parcel..." ]

        LoadingResults ->
            div [ class "alert alert-warning" ] [ text "Fetching results..." ]

        Failure err ->
            div [ class "alert alert-danger" ] [ text err ]

        Success results ->
            div []
                [ div [ class "mb-3" ]
                    [ button [ class (if model.viewMode == TableView then "btn btn-secondary me-2" else "btn btn-outline-secondary me-2"), onClick (SetViewMode TableView) ] [ text "Table View" ]
                    , button [ class (if model.viewMode == JsonView then "btn btn-secondary" else "btn btn-outline-secondary"), onClick (SetViewMode JsonView) ] [ text "JSON View" ]
                    ]
                , if List.isEmpty results then
                    div [ class "alert alert-warning" ] [ text "No results found." ]
                  else
                    case model.viewMode of
                        TableView -> viewTable model results
                        JsonView -> viewJson results
                ]

viewTable : Model -> List Property -> Html Msg
viewTable model results =
    let
        headers = QueryBuilder.getSelectedFields model.targetPoint model.targetArea model.targetTotalValue model.fields
    in
    div [ class "table-responsive" ]
        [ table [ class "table table-striped table-hover table-sm" ]
            [ thead []
                [ tr [] (List.map (\h -> th [] [ text h ]) headers) ]
            , tbody []
                (List.map (viewRow headers) results)
            ]
        ]

viewRow : List String -> Property -> Html Msg
viewRow headers prop =
    let
        getValue h =
            case h of
                "closed_roll_year" -> Maybe.withDefault "" prop.closed_roll_year
                "property_location" -> Maybe.withDefault "" prop.property_location
                "parcel_number" -> Maybe.withDefault "" prop.parcel_number
                "assessor_neighborhood_code" -> Maybe.withDefault "" prop.assessor_neighborhood_code
                "property_area" -> prop.property_area |> Maybe.map String.fromFloat |> Maybe.withDefault ""
                "number_of_bedrooms" -> prop.number_of_bedrooms |> Maybe.map String.fromFloat |> Maybe.withDefault ""
                "number_of_bathrooms" -> prop.number_of_bathrooms |> Maybe.map String.fromFloat |> Maybe.withDefault ""
                "current_sales_date" -> Maybe.withDefault "" prop.current_sales_date
                "property_class_code" -> Maybe.withDefault "" prop.property_class_code
                "year_property_built" -> prop.year_property_built |> Maybe.map String.fromFloat |> Maybe.withDefault ""
                "assessed_improvement_value" -> prop.assessed_improvement_value |> Maybe.map String.fromFloat |> Maybe.withDefault ""
                "assessed_land_value" -> prop.assessed_land_value |> Maybe.map String.fromFloat |> Maybe.withDefault ""
                "number_of_rooms" -> prop.number_of_rooms |> Maybe.map String.fromFloat |> Maybe.withDefault ""
                "total_assessed_value" -> prop.total_assessed_value |> Maybe.map String.fromFloat |> Maybe.withDefault ""
                "distance_from_target" -> prop.distance_from_target |> Maybe.map String.fromFloat |> Maybe.withDefault ""
                "property_area_ratio" -> prop.property_area_ratio |> Maybe.map String.fromFloat |> Maybe.withDefault ""
                "total_assessed_value_ratio" -> prop.total_assessed_value_ratio |> Maybe.map String.fromFloat |> Maybe.withDefault ""
                "the_geom" -> case prop.the_geom of
                    Just g -> String.fromFloat (Tuple.first g.coordinates) ++ ", " ++ String.fromFloat (Tuple.second g.coordinates)
                    Nothing -> ""
                _ -> ""
    in
    tr [] (List.map (\h -> td [] [ text (getValue h) ]) headers)

viewJson : List Property -> Html Msg
viewJson results =
    pre [ class "bg-light p-3 border" ]
        [ code [] [ text (Encode.encode 2 (Encode.list (\p -> p.raw_json) results)) ] ]
