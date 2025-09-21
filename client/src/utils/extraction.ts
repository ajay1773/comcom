type ParseResult<T> =
  | {
      success: true;
      data: T;
    }
  | {
      success: false;
      error: string;
    };

type CardWidget = {
  template: string;
  payload: unknown;
};

// Pure function to safely parse JSON
const safeJsonParse = <T = unknown>(jsonString: string): ParseResult<T> => {
  try {
    const parsed = JSON.parse(jsonString);
    return { success: true, data: parsed };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Invalid JSON",
    };
  }
};

// Pure function to recursively find card_widget in object
const findCardWidgetInObject = (obj: unknown): ParseResult<CardWidget> => {
  if (typeof obj !== "object" || obj === null)
    return { success: false, error: "Object is null or not an object" };

  // Direct card_widget property - check if it exists in the current object
  if ("workflow_widget_json" in obj) {
    if (typeof obj.workflow_widget_json === "string")
      return safeJsonParse<CardWidget>(obj.workflow_widget_json);
    else return { success: true, data: obj.workflow_widget_json as CardWidget };
  }

  // Recursively search in object properties
  for (const key in obj) {
    let value = obj[key];

    // If value is a string, check if it might contain card_widget data
    if (typeof value === "string") {
      // Check if the string contains card_widget or custom_card
      if (value.includes("workflow_widget_json")) {
        // First check if we have exactly 2 occurrences (likely duplicates)
        // if (hasCardWidgetMoreThenTwice(value)) {
        //   // Handle the case where we have duplicate complete JSON objects
        //   const result = extractCardWidgetFromDuplicates(value);
        //   if (result.success) {
        //     return result;
        //   } else {
        //     // If extracting from duplicates fails, try normal JSON parsing
        //     const parseResult = safeJsonParse(value);
        //     if (parseResult.success) value = parseResult.data;
        //   }
        // } else {
        //   // Single occurrence or different pattern - try normal JSON parsing
        //   const parseResult = safeJsonParse(value);
        //   if (parseResult.success) value = parseResult.data;
        //   else continue; // Skip if not valid JSON
        // }

        // Single occurrence or different pattern - try normal JSON parsing
        const parseResult = safeJsonParse(value);
        if (parseResult.success) value = parseResult.data;
        else continue; // Skip if not valid JSON
      } else {
        // String doesn't contain workflow_widget_json, try parsing it anyway
        const parseResult = safeJsonParse(value);
        if (parseResult.success) value = parseResult.data;
        else continue; // Skip if not valid JSON
      }
    }

    // Recursively search in the parsed value (now an object)
    if (typeof value === "object" && value !== null) {
      const found = findCardWidgetInObject(value);
      if (found.success) return found;
    }
  }

  return { success: false, error: "workflow_widget_json not found in object" };
};

// Main extraction function with better error handling
export const extractTemplatePayload = (
  jsonString: string
): { template: string; payload: unknown } | null => {
  // Validate input - must be a non-empty string
  if (!jsonString || typeof jsonString !== "string") return null;

  try {
    // Step 1: Parse the first-level JSON string
    const initialParseResult = safeJsonParse(jsonString);
    if (!initialParseResult.success) return null;

    let parsedData = initialParseResult.data;

    // Step 2: Handle nested stringified JSON by repeatedly parsing
    // Sometimes JSON objects are stringified multiple times
    while (typeof parsedData === "string") {
      const parseResult = safeJsonParse(parsedData);
      if (!parseResult.success) break; // Stop if we can't parse further

      parsedData = parseResult.data;
    }

    // Step 3: Search for workflow_widget_json in the parsed data structure
    // This will handle both direct workflow_widget_json properties and nested/duplicate cases
    const result = findCardWidgetInObject(parsedData);

    // Step 4: Return the extracted workflow_widget_json or null if not found
    if (result.success) return result.data;
    else return null;
  } catch {
    // If anything goes wrong during the process, return null
    return null;
  }
};
