# COVID-19 tracking pipeline

A Python project that cleans a local COVID-19 CSV, uploads the processed file to AWS S3, and displays the local results in a Streamlit dashboard.

## How it works

1. `pipeline.py` reads `data/raw/covid_data.csv`.
2. It converts `Day` to dates, removes rows missing `Entity`, `Day`, or `Weekly cases`, removes exact duplicate rows, and sorts by entity and date.
3. It adds `Year` and `Month`, then writes `data/processed/covid_processed.csv`.
4. It uploads that file to `processed_data/covid_processed.csv` in your S3 bucket.
5. `dashboard.py` reads the processed **local file**, not S3, and shows a country selector, case metrics, trend and ranking charts, and a data preview.

## Requirements

- Python 3 with support for the installed package versions.
- A CSV dataset with the columns described below.
- An existing AWS S3 bucket and credentials with permission to upload to it.

The repository does not include a dataset. `requirements.txt` is currently empty, so install the imported packages directly for now. Package versions are not pinned.

## Setup

Run commands from the repository root.

```bash
git clone https://github.com/ChidanandB16/covid-tracking-pipeline.git
cd covid-tracking-pipeline
python -m venv venv
```

Activate the environment:

```bash
# macOS / Linux
source venv/bin/activate
```

```powershell
# Windows PowerShell
venv\Scripts\Activate.ps1
```

Then install the dependencies:

```bash
python -m pip install pandas boto3 python-dotenv streamlit plotly
```

Use `python3` instead of `python` if that is how Python is installed on your system.

### Prepare the input data

Create the directories before running the pipeline. The script does not create them itself.

```bash
python -c "from pathlib import Path; Path('data/raw').mkdir(parents=True, exist_ok=True); Path('data/processed').mkdir(parents=True, exist_ok=True)"
```

Place your dataset at `data/raw/covid_data.csv`. It must contain these exact column names:

| Column | Expected values |
| --- | --- |
| `Entity` | Country or region name, such as `India` |
| `Day` | A parseable date, preferably `YYYY-MM-DD` |
| `Weekly cases` | Numeric weekly case counts |

Extra columns are retained. Use a dataset with at least one valid row. Rows with missing required values are dropped, but invalid dates and nonnumeric case counts are not explicitly cleaned.

### Configure AWS

Create a `.env` file in the repository root:

```dotenv
AWS_REGION=your-bucket-region
S3_BUCKET_NAME=your-existing-bucket-name
```

Configure credentials through your usual AWS credential setup. With `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` unset, Boto3 can use its default credential providers, such as a local AWS profile or an IAM role. The scripts also accept those two variables from the environment or `.env` if needed.

Never commit credentials. `.env` and `data/` are already ignored by Git. `venv/` is also ignored by Git.

The pipeline needs `s3:PutObject` permission for the destination object. The optional connection check in `config.py` also needs `s3:ListBucket`. AWS charges may apply.

## Run the pipeline

```bash
python pipeline.py
```

A successful run prints the processed row count and confirms the S3 upload. Re-running uploads to the same S3 key; depending on bucket versioning, this may replace the current object or create a new version.

Optional connection check:

```bash
python config.py
```

This lists objects in the configured bucket. It is not required by the pipeline or dashboard.

## Open the dashboard

After the processed CSV exists, run:

```bash
python -m streamlit run dashboard.py
```

Open the local URL printed by Streamlit. The selector defaults to India when present, otherwise the first available entity.

The dashboard shows:

- Cases on the latest date in the selected entity's data.
- The sum and peak of its `Weekly cases` values.
- A weekly trend chart.
- The top 10 entities by summed weekly case counts.
- A preview of the selected entity's processed rows.

These metrics describe the supplied dataset, not a live feed. The card labelled "Total Reported Cases" is a sum of `Weekly cases`; its meaning depends on the source's reporting frequency. The ranking includes every `Entity` value, including aggregate regions if present in your input.

## Troubleshooting

| Problem | Check |
| --- | --- |
| `ModuleNotFoundError` | Activate the environment and install the packages above. |
| Missing raw CSV | Put the dataset at `data/raw/covid_data.csv` and run from the repository root. |
| Cannot save processed CSV | Create `data/processed/` before running the pipeline. |
| `KeyError` for a column | Match `Entity`, `Day`, and `Weekly cases` exactly. |
| Date conversion or numeric errors | Clean invalid dates and nonnumeric counts in the input CSV. |
| S3 credentials or access error | Check credentials, bucket name, region, and upload permissions. |
| Dashboard cannot find data | Run the pipeline first. The dashboard needs the local processed CSV. |

The local processed file is written before the S3 upload. If the upload fails, that file may still be available for the dashboard. There is no dedicated offline pipeline option, automatic data download, or scheduled refresh in the current code.

## Project files

```text
config.py          Optional S3 connection check
pipeline.py        CSV cleaning and S3 upload
dashboard.py       Streamlit dashboard
requirements.txt   Currently empty
README.md          Setup and usage guide
```
