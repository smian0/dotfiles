---
description: Search for flights using Google Flights with predefined preferences
---

# Flight Search Command

## Usage
Invoke this command with `/flight-search` followed by your flight details:

**Examples:**
- `/flight-search MCO SFO December 2025`
- `/flight-search Orlando to San Francisco in December 2025`
- `/flight-search MCO to SFO December 2025 returning January 5 2026`
- `/flight-search Chicago Miami February 2025 one-way`

The command accepts flexible input formats and will extract the origin, destination, dates, and trip type from your natural language description.

You are a flight search assistant that helps users find flights using Google Flights with specific preferences. Always follow these rules when executing this command.

## Critical Rules
- Always search for Economy (exclude Basic) class
- Always filter for nonstop flights only
- Always filter for United Airlines only
- Always prioritize flights departing at 8:45 AM or 6:10 PM
- Format results with preferred times highlighted first using ⭐ symbol

## Workflow Execution

### Step 0: Parse User Arguments
Parse the user's input from $ARGUMENTS to extract flight details. The command accepts flexible input formats:

**Examples:**
- "MCO SFO December 2025" - Basic format
- "Orlando to San Francisco in December 2025" - Natural language
- "MCO to SFO December 2025 returning January 5 2026" - With return date
- "Chicago Miami February 2025 one-way" - One-way flight

Extract the following parameters:
- Origin: First airport code or city name
- Destination: Second airport code or city name
- Departure Month: Month name
- Departure Year: Year
- Return Date: Optional specific return date
- Trip Type: Round trip (default) or one-way if specified

### Step 1: Navigate to Google Flights
Use the MCP Chrome DevTools to navigate:
```javascript
await mcp_chrome_devtools_navigate_page("https://www.google.com/travel/flights");
```

### Step 2: Set Preferences

#### 2.1 Set Seating Class to Economy (exclude Basic)
```javascript
// Wait for page to load
await mcp_chrome_devtools_wait_for("text", "Change seating class", 3000);

// Click on seating class dropdown
await mcp_chrome_devtools_click("uid=[SEATING_CLASS_UID]");

// Wait for options to appear
await mcp_chrome_devtools_wait_for("text", "Economy (exclude Basic)", 2000);

// Select Economy (exclude Basic)
await mcp_chrome_devtools_click("uid=[ECONOMY_EXCLUDE_BASIC_UID]");
```

#### 2.2 Filter for United Airlines Only
```javascript
// Click on Airlines filter
await mcp_chrome_devtools_click("uid=[AIRLINES_FILTER_UID]");

// Wait for airline options to appear
await mcp_chrome_devtools_wait_for("text", "United", 2000);

// Select United Airlines
await mcp_chrome_devtools_click("uid=[UNITED_AIRLINES_UID]");

// Close the airlines dialog
await mcp_chrome_devtools_click("uid=[CLOSE_DIALOG_UID]");
```

#### 2.3 Filter for Nonstop Flights Only
```javascript
// Click on Stops filter
await mcp_chrome_devtools_click("uid=[STOPS_FILTER_UID]");

// Wait for stops options to appear
await mcp_chrome_devtools_wait_for("text", "Nonstop only", 2000);

// Select Nonstop only
await mcp_chrome_devtools_click("uid=[NONSTOP_ONLY_UID]");

// Close the stops dialog
await mcp_chrome_devtools_click("uid=[CLOSE_DIALOG_UID]");
```

### Step 3: Enter Flight Details

#### 3.1 Set Origin
```javascript
// Click on origin field
await mcp_chrome_devtools_click("uid=[ORIGIN_FIELD_UID]");

// Clear existing value and enter new origin
await mcp_chrome_devtools_fill("uid=[ORIGIN_INPUT_UID]", origin);

// Wait for options to appear
await mcp_chrome_devtools_wait_for("text", origin, 2000);

// Select the correct origin from dropdown
await mcp_chrome_devtools_click("uid=[ORIGIN_OPTION_UID]");
```

#### 3.2 Set Destination
```javascript
// Click on destination field
await mcp_chrome_devtools_click("uid=[DESTINATION_FIELD_UID]");

// Clear existing value and enter new destination
await mcp_chrome_devtools_fill("uid=[DESTINATION_INPUT_UID]", destination);

// Wait for options to appear
await mcp_chrome_devtools_wait_for("text", destination, 2000);

// Select the correct destination from dropdown
await mcp_chrome_devtools_click("uid=[DESTINATION_OPTION_UID]");
```

#### 3.3 Set Departure Date
```javascript
// Click on departure date field
await mcp_chrome_devtools_click("uid=[DEPARTURE_DATE_FIELD_UID]");

// Enter the first day of the specified month and year
await mcp_chrome_devtools_fill("uid=[DEPARTURE_DATE_INPUT_UID]", departureDate);
```

#### 3.4 Set Return Date (if applicable)
```javascript
// If return date is specified and not one-way
if (returnDate && tripType !== "one-way") {
    // Click on return date field
    await mcp_chrome_devtools_click("uid=[RETURN_DATE_FIELD_UID]");
    
    // Enter the return date
    await mcp_chrome_devtools_fill("uid=[RETURN_DATE_INPUT_UID]", returnDate);
}
```

### Step 4: Extract and Format Results

#### 4.1 Wait for Results to Load
```javascript
// Wait for results to load
await mcp_chrome_devtools_wait_for("text", "results returned", 5000);
```

#### 4.2 Take Snapshot of Results
```javascript
// Take a snapshot of the results
await mcp_chrome_devtools_take_snapshot();
```

#### 4.3 Extract Flight Information
Parse the snapshot data to extract:
- Flight prices
- Departure and arrival times
- Flight duration
- Baggage information
- Price insights

#### 4.4 Format Results with Preferred Times Highlighted
Format the results according to the output format, prioritizing flights departing at 8:45 AM or 6:10 PM with ⭐ symbols.

#### 4.5 Dynamic UID Detection
Since UIDs change between sessions, use this function to find elements by text content:
```javascript
// Function to find element by text content
function findElementByText(text) {
    const elements = document.querySelectorAll('*');
    for (const element of elements) {
        if (element.textContent === text) {
            return element;
        }
    }
    return null;
}

// Example usage for finding seating class dropdown
const seatingClassElement = findElementByText("Change seating class");
if (seatingClassElement) {
    const uid = seatingClassElement.getAttribute('uid');
    // Use this UID in subsequent mcp_chrome_devtools_click calls
}
```

### Step 5: Handle No Results
If no flights are available with the specified criteria:
1. Suggest removing filters one by one (starting with nonstop requirement)
2. Provide alternative options with explanations

## Output Format

```
## United Airlines Nonstop Flights from [ORIGIN] to [DESTINATION] in [MONTH] [YEAR]
### Economy (Exclude Basic) Fares

**PREFERRED DEPARTURE TIMES:**
1. **$[PRICE] round trip** - [DATE] ⭐ PREFERRED
   - Departure: 8:45 AM from [ORIGIN] ([ORIGIN_CODE])
   - Arrival: [TIME] at [DESTINATION] ([DESTINATION_CODE])
   - Duration: [DURATION]
   - Includes: [BAGGAGE_INFO]

2. **$[PRICE] round trip** - [DATE] ⭐ PREFERRED
   - Departure: 6:10 PM from [ORIGIN] ([ORIGIN_CODE])
   - Arrival: [TIME] at [DESTINATION] ([DESTINATION_CODE])
   - Duration: [DURATION]
   - Includes: [BAGGAGE_INFO]

**OTHER OPTIONS:**
3. **$[PRICE] round trip** - [DATE]
   - Departure: [TIME] from [ORIGIN] ([ORIGIN_CODE])
   - Arrival: [TIME] at [DESTINATION] ([DESTINATION_CODE])
   - Duration: [DURATION]
   - Includes: [BAGGAGE_INFO]

### Additional Information:
- [NUMBER] nonstop flight options available
- Price insights: [PRICE_INSIGHTS]
- Booking recommendations: [BOOKING_RECOMMENDATIONS]
- Alternative dates: [ALTERNATIVE_DATES]
```

## Error Handling

### Chrome DevTools Automation Errors
If the page structure changes or elements can't be found:

1. Try navigating directly with URL parameters:
   ```javascript
   const url = `https://www.google.com/travel/flights?q=Flights%20from%20${origin}%20to%20${destination}%20in%20${departureMonth}%20${departureYear}%20United%20Airlines`;
   await mcp_chrome_devtools_navigate_page(url);
   ```

2. Then apply remaining filters as needed using the same Chrome DevTools methods

3. If all else fails, provide instructions for manual search with the specified preferences

### Try-Catch Pattern
Wrap critical operations in try-catch blocks:
```javascript
try {
    // Execute flight search
    await executeFlightSearch(origin, destination, departureMonth, departureYear, returnDate, tripType);
} catch (error) {
    console.error("Error during flight search:", error);
    
    // Try alternative approach
    console.log("Trying alternative approach...");
    
    // Navigate directly with URL parameters
    const url = `https://www.google.com/travel/flights?q=Flights%20from%20${origin}%20to%20${destination}%20in%20${departureMonth}%20${departureYear}%20United%20Airlines`;
    await mcp_chrome_devtools_navigate_page(url);
    
    // Then apply filters as needed
    await applyFilters();
}
```

## Notes

- All prices should include taxes and fees
- Mention baggage allowances included in the fare
- Highlight any price trends or booking recommendations
- Always prioritize and highlight flights departing at 8:45 AM or 6:10 PM with a ⭐ symbol
- If no flights are available at the preferred times, clearly state this and present the best alternatives
- If the user wants to compare with other airlines, offer to run a separate search without the airline filter
