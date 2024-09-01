from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters
import csv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define list to store job data
jobs = []

def on_data(data: EventData):
    jobs.append({
        'title': data.title,
        'company': data.company,
        'location': data.location,
        'date': data.date,
        'link': data.link,
        'description': data.description
    })
    logging.info(f"Scraped job: {data.title} at {data.company}")

def on_error(error):
    logging.error(f"Error occurred: {error}")

def on_end():
    logging.info(f"Scraping completed. Total jobs found: {len(jobs)}")
    save_to_csv(jobs, "linkedin_jobs.csv")

def save_to_csv(jobs, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["title", "company", "location", "date", "link", "description"])
        writer.writeheader()
        writer.writerows(jobs)
    logging.info(f"Saved {len(jobs)} jobs to {filename}")

# Instantiate the scraper
scraper = LinkedinScraper(
    chrome_executable_path=None,  # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver) 
    chrome_options=None,  # Custom Chrome options here
    headless=True,  # Overrides headless mode only if chrome_options is None
    max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
    slow_mo=1,  # Slow down the scraper to avoid 'Too many requests 429' errors (in seconds)
    page_load_timeout=20  # Page load timeout (in seconds)    
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

queries = [
    Query(
        query='AI ML GenAI',
        options=QueryOptions(
            locations=['Singapore'],
            apply_link=True,  # Try to extract apply link
            limit=500,  # Limit to 50 jobs
            filters=QueryFilters(
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.MONTH,
                type=[TypeFilters.FULL_TIME, TypeFilters.CONTRACT],
                experience=[ExperienceLevelFilters.ENTRY_LEVEL, ExperienceLevelFilters.MID_SENIOR]
            )
        )
    )
]

scraper.run(queries)