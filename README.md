# SAM.gov NAICS Export Tool

Export contract opportunities from SAM.gov to CSV format, filtered by NAICS code.

## Features

- Filter opportunities by NAICS code prefix (default: 212 - Mining)
- Configurable date range (up to 365 days)
- Automatic pagination for large result sets
- Exports 35+ data fields including contacts, locations, and awards
- Rate limiting and retry logic built-in

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env and add your SAM_API_KEY
```

## Getting a SAM.gov API Key

1. Go to [SAM.gov](https://sam.gov) and create an account (or sign in)
2. Click on your name in the top right corner
3. Select **Account Details**
4. Scroll down to the **API Key** section
5. Enter your password when prompted
6. Click **Request Public API Key**
7. Copy the generated key to your `.env` file:
   ```
   SAM_API_KEY=your_key_here
   ```

Note: API keys may take a few minutes to activate after creation.

## Usage

```bash
# Default: last 30 days, NAICS 212 (Mining)
python -m sam_export.cli

# Custom date range
python -m sam_export.cli --days 90

# Custom output filename
python -m sam_export.cli --output mining_opportunities.csv

# Different NAICS code
python -m sam_export.cli --naics 236    # Construction
python -m sam_export.cli --naics 54     # Professional Services

# Limit number of records
python -m sam_export.cli --limit 100
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--days` | 30 | Number of days to look back (max: 365) |
| `--output`, `-o` | auto | Output CSV filename |
| `--naics` | 212 | NAICS code prefix to filter |
| `--limit` | all | Maximum records to fetch |

## Output Fields

The CSV export includes:

**Basic Info**: noticeId, title, solicitationNumber, type, postedDate, archiveDate, active

**Classification**: naicsCode, classificationCode, typeOfSetAside, typeOfSetAsideDescription

**Organization**: fullParentPathName, organizationType, officeAddress (city, state, zip)

**Contact**: name, email, phone, title

**Place of Performance**: street, city, state, zip, country

**Award**: number, amount, date, awardee name, awardee location

**Links**: uiLink, description URL, resourceLinks

## API Constraints

- Maximum 1-year date range per request
- Maximum 1000 records per API call (pagination handled automatically)
- Rate limiting: 0.5 second delay between requests

## License

MIT
