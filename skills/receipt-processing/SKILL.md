# Receipt Processing Skill

## Overview
Process expense receipts (images) from Google Drive or direct upload, extract financial data, add to Business Expenses sheet, and move to processed folder.

## Triggers

### 1. Direct Receipt Upload
User sends an image (JPG/PNG) of a receipt directly in chat.

### 2. Batch Processing Command
User says: "process receipts", "process all receipts", or similar.
→ Process all images in "2026 to be processed" folder.

## Workflow

### For Single Receipt (Direct Upload):
1. Save image locally
2. Extract data using image analysis:
   - Date (DD/MM/YYYY)
   - Vendor name
   - Total amount
   - Currency (CHF/EUR/USD)
   - VAT percentage and amount
   - Description (summarized, no commas - use spaces/dashes)
   - Category (Fuel, Production materials, Equipment, Shipping, etc.)
3. Determine year from date
4. Find next empty row in Expenses sheet
5. Add row with pipe-separated values:
   ```
   gog sheets update <sheet_id> "Expenses!A<row>" "<date>|<year>|<currency>|<amount>|<vat_pct>|<vat_amt>|<vendor>|<desc>|<cat>|||" --json
   ```
6. If uploaded to Drive: move to correct year folder
7. Confirm completion to user

### For Batch Processing:
1. List files in "2026 to be processed":
   ```
   gog drive ls --parent 16W9-NJQqvCy_WfJu9159Ab-G0UOrnskK --json --results-only
   ```
2. For each image file:
   - Download: `gog drive download <id> --out /tmp/<name>`
   - Extract data (as above)
   - Add to sheet
   - Move to correct year folder
3. Compile report
4. Send to Telegram group -1003829111345

## Resource IDs

### Folders
- **2026 to be processed**: `16W9-NJQqvCy_WfJu9159Ab-G0UOrnskK`
- **2026 processed**: `1__9dBNYyIvpTBwfnYJSqTSdG6PWJ5YsH`
- **2025 processed**: `1l6_SlAq5fl8avdEMhuzF6lL9_aExP9Ky`
- **2025 to be processed**: `1gcdmFxmTutQwRKJbt8876ESlvweVglpz`

### Sheets
- **Business Expenses**: `1xeudOXfiSeSe5JERVK15d_1VPCMPRZsw1Wj21-TcK5M`
- **Tab**: Expenses
- **Columns**: A=Date, B=Year, C=Currency, D=Amount, E=VAT%, F=VAT amt, G=Vendor, H=Description, I=Category, J=Full CHF, K=Full EUR, L=Exchange rate

### Telegram
- **Report group**: `-1003829111345`

## Rules

1. **Images only**: PDFs cannot be processed (no conversion tools available)
2. **No commas in descriptions**: Use dashes or spaces instead (pipe separator format)
3. **Year detection**: Parse date to determine folder (2025 → 2025 processed, 2026 → 2026 processed)
4. **VAT handling**: Extract VAT% and amount if visible on receipt
5. **Categories**: Fuel, Production materials, Equipment, Shipping, Office supplies, etc.

## Examples

### Good Description Format:
- "Bleifrei 95 petrol - 22.03L" ✓
- "Production supplies - acetone activated carbon battery" ✓

### Bad Description Format (commas cause issues):
- "Becher rPET, Polyston, Renovo Aceton, Aktivkohle" ✗ (splits across rows)

## Error Handling

- If image analysis fails: Ask user for manual entry
- If sheet update fails: Report error, keep file in to-be-processed
- If folder move fails: Report but confirm sheet was updated

## Related
- Daily news cron (uses same Telegram group)
- Business Analysis document (expense tracking for financial planning)
