export interface QueryParams {
  roll_year?: string;
  bedrooms?: number | string;
  bathrooms?: number | string;
  parcel_number?: string;
  area_min?: number | string;
  area_max?: number | string;
  date_start?: string;
  date_end?: string;
  district?: string | string[];
  neighborhood_code?: string | string[];
  property_class_code?: string | string[];
}

export function getSelectedFields(
  targetPoint: [number, number] | null = null,
  targetArea: number | null = null,
  targetTotalAssessedValue: number | null = null,
  requestedFields: string[] | null = null
): string[] {
  const defaultFields = [
    "closed_roll_year",
    "property_location",
    "parcel_number",
    "assessor_neighborhood_code",
    "property_area",
    "number_of_bedrooms",
    "number_of_bathrooms",
    "current_sales_date",
    "property_class_code",
    "year_property_built",
    "assessed_improvement_value",
    "assessed_land_value",
    "the_geom",
    "number_of_rooms",
    "total_assessed_value"
  ];

  let fieldsToUse: string[];

  if (requestedFields && requestedFields.length > 0) {
    fieldsToUse = [];
    for (const f of requestedFields) {
      if (f === "distance_from_target" && targetPoint === null) continue;
      if (f === "property_area_ratio" && targetArea === null) continue;
      if (f === "total_assessed_value_ratio" && targetTotalAssessedValue === null) continue;
      fieldsToUse.push(f);
    }
  } else {
    fieldsToUse = [...defaultFields];
    if (targetPoint) fieldsToUse.push("distance_from_target");
    if (targetArea !== null) fieldsToUse.push("property_area_ratio");
    if (targetTotalAssessedValue !== null) fieldsToUse.push("total_assessed_value_ratio");
    fieldsToUse.sort();
  }

  return fieldsToUse;
}

export function buildSelectClause(
  targetPoint: [number, number] | null = null,
  targetArea: number | null = null,
  targetTotalAssessedValue: number | null = null,
  requestedFields: string[] | null = null
): string {
  const fieldsToUse = getSelectedFields(targetPoint, targetArea, targetTotalAssessedValue, requestedFields);

  const selectParts: string[] = [];
  for (const field of fieldsToUse) {
    if (field === "distance_from_target") {
      if (targetPoint) {
        const [lon, lat] = targetPoint;
        selectParts.push(`distance_in_meters(\`the_geom\`, 'POINT (${lon} ${lat})') AS distance_from_target`);
      }
    } else if (field === "property_area_ratio") {
      if (targetArea !== null) {
        selectParts.push(`property_area / ${targetArea} AS property_area_ratio`);
      }
    } else if (field === "total_assessed_value_ratio") {
      if (targetTotalAssessedValue !== null) {
        const totalExpr = "(coalesce(assessed_improvement_value, 0) + coalesce(assessed_land_value, 0) + coalesce(assessed_fixtures_value, 0))";
        selectParts.push(`${totalExpr} / ${targetTotalAssessedValue} AS total_assessed_value_ratio`);
      }
    } else if (field === "total_assessed_value") {
      selectParts.push("coalesce(assessed_improvement_value, 0) + coalesce(assessed_land_value, 0) + coalesce(assessed_fixtures_value, 0) AS total_assessed_value");
    } else {
      selectParts.push(field);
    }
  }

  return selectParts.join(", ");
}

export function buildOrderByClause(
  targetPoint: [number, number] | null = null,
  targetArea: number | null = null
): string | null {
  const orderParts: string[] = [];
  if (targetPoint) {
    const [lon, lat] = targetPoint;
    orderParts.push(`distance_in_meters(\`the_geom\`, 'POINT (${lon} ${lat})')`);
  }

  if (targetArea !== null) {
    orderParts.push(`property_area / ${targetArea}`);
  }

  return orderParts.length > 0 ? orderParts.join(", ") : null;
}

export function buildWhereClause(params: QueryParams): string {
  const filters: string[] = [];

  if (params.bedrooms !== undefined) {
    filters.push(`number_of_bedrooms = '${params.bedrooms}'`);
  }

  if (params.bathrooms !== undefined) {
    filters.push(`number_of_bathrooms = '${params.bathrooms}'`);
  }

  if (params.parcel_number) {
    filters.push(`parcel_number = '${params.parcel_number}'`);
  }

  const { area_min, area_max } = params;
  if (area_min && area_max) {
    filters.push(`property_area BETWEEN ${area_min} AND ${area_max}`);
  } else if (area_min) {
    filters.push(`property_area >= ${area_min}`);
  } else if (area_max) {
    filters.push(`property_area <= ${area_max}`);
  }

  const { date_start, date_end } = params;
  if (date_start && date_end) {
    filters.push(`current_sales_date BETWEEN '${date_start}'::floating_timestamp AND '${date_end}'::floating_timestamp`);
  } else if (date_start) {
    filters.push(`current_sales_date >= '${date_start}'::floating_timestamp`);
  } else if (date_end) {
    filters.push(`current_sales_date <= '${date_end}'::floating_timestamp`);
  }

  if (params.district) {
    const districts = Array.isArray(params.district) ? params.district : [params.district];
    const quotedDistricts = districts.map(d => `'${d}'`).join(", ");
    filters.push(`caseless_one_of(assessor_neighborhood_district, ${quotedDistricts})`);
  }

  if (params.property_class_code) {
    const codes = Array.isArray(params.property_class_code) ? params.property_class_code : [params.property_class_code];
    const quotedCodes = codes.map(c => `'${c}'`).join(", ");
    filters.push(`caseless_one_of(property_class_code, ${quotedCodes})`);
  }

  if (params.neighborhood_code) {
    const codes = Array.isArray(params.neighborhood_code) ? params.neighborhood_code : [params.neighborhood_code];
    const quotedCodes = codes.map(c => `'${c}'`).join(", ");
    filters.push(`caseless_one_of(assessor_neighborhood_code, ${quotedCodes})`);
  }

  if (params.roll_year) {
    filters.push(`closed_roll_year = '${params.roll_year}'`);
  }

  return filters.join(" AND ");
}
