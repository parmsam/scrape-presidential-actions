# scrape-presidential-action

This project scrapes presidential actions from the WhiteHouse.gov website and saves them as JSON files.

## Features

- Scrapes all presidential actions from the White House website.
- Saves the collected actions with metadata to the `presidential_actions` directory.
- Ensures respectful request timing to avoid overloading the server.

## Usage

1. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

2. Run the scraper:
    ```sh
    python scrape.py
    ```

3. The collected actions will be saved in the `presidential_actions` directory.

## Files

- [scrape.py](scrape.py): Main script to scrape and save presidential actions.
- presidential_actions: Directory where the collected actions are saved.
- [run.sh](run.sh): Shell script to run the scraper.

## Functions

- [PresidentialActionsScraper](scrape.py): Class to handle the scraping process.
- [save_actions](scrape.py): Function to save the collected actions to files.

## License

This project is licensed under the MIT License.


