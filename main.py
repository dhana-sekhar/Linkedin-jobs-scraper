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

def on_end(query_name, location):
    logging.info(f"Scraping completed for {query_name} in {location}. Total jobs found: {len(jobs)}")
    if jobs:  # Check if there are any jobs before saving
        filename = f"{location.replace(' ', '_')}_{query_name.replace(' ', '_')}_JD.csv"
        save_to_csv(jobs, filename)
    else:
        logging.warning(f"No jobs found for {query_name} in {location}. Skipping CSV creation.")
    jobs.clear()  # Clear the jobs list after saving to CSV

def save_to_csv(jobs, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["title", "company", "location", "date", "link", "description"])
        writer.writeheader()
        writer.writerows(jobs)
    logging.info(f"Saved {len(jobs)} jobs to {filename}")

# Instantiate the scraper
scraper = LinkedinScraper(
    chrome_executable_path=None,
    chrome_options=None,
    headless=True,
    max_workers=1,
    slow_mo=2,  # Increased the delay between actions
    page_load_timeout=40  # Increased the page load timeout
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)

# Define your queries and locations
queries_and_locations = [
    {'query': 'AI ML GenAI', 'locations': ['Singapore']},
    {'query': 'Data Science', 'locations': ['United States']},
    {'query': 'Software Engineer', 'locations': ['India', 'Germany']},
]

# Run the scraper for each query and location
for item in queries_and_locations:
    for location in item['locations']:
        query_name = item['query']
        query = Query(
            query=query_name,
            options=QueryOptions(
                locations=[location],
                apply_link=True,
                limit=500,
                filters=QueryFilters(
                    relevance=RelevanceFilters.RECENT,
                    time=TimeFilters.MONTH,
                    type=[TypeFilters.FULL_TIME, TypeFilters.CONTRACT],
                    experience=[ExperienceLevelFilters.ENTRY_LEVEL, ExperienceLevelFilters.MID_SENIOR]
                )
            )
        )
        
        def custom_on_end():
            on_end(query_name, location)
        
        scraper.on(Events.END, custom_on_end)
        scraper.run([query])
