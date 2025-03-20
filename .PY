import requests
import argparse
import csv
import json
import sys
from typing import List

# Define a function to fetch papers from PubMed API
def fetch_papers(query: str, debug: bool = False) -> List[dict]:
    url = f"https://api.ncbi.nlm.nih.gov/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=xml"
    
    if debug:
        print(f"Fetching papers from: {url}")
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        sys.exit(1)
    
    papers_data = response.text
    return parse_paper_ids(papers_data)


# Parse the paper ids from the API response
def parse_paper_ids(data: str) -> List[str]:
    # Logic to extract PubMed paper IDs from the API response XML
    paper_ids = []
    if "<IdList>" in data and "</IdList>" in data:
        start = data.index("<IdList>") + len("<IdList>")
        end = data.index("</IdList>")
        id_list = data[start:end]
        paper_ids = id_list.splitlines()
    return paper_ids


# Function to fetch detailed information about the paper using PubMed API
def fetch_paper_details(paper_id: str, debug: bool = False) -> dict:
    url = f"https://api.ncbi.nlm.nih.gov/eutils/esummary.fcgi?db=pubmed&id={paper_id}&retmode=xml"
    
    if debug:
        print(f"Fetching details for: {paper_id}")
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error fetching data for {paper_id}: {response.status_code}")
        return {}
    
    paper_details = response.text
    return parse_paper_details(paper_details)


# Parse detailed paper information
def parse_paper_details(data: str) -> dict:
    details = {}
    try:
        # Logic to parse paper title, authors, emails, and affiliations
        details = {
            "PubmedID": data.split("<Id>")[1].split("</Id>")[0],
            "Title": data.split("<Title>")[1].split("</Title>")[0],
            "PublicationDate": data.split("<PubDate>")[1].split("</PubDate>")[0]
        }
    except Exception as e:
        print(f"Error parsing paper details: {e}")
    return details


# Save data to CSV file
def save_to_csv(papers: List[dict], filename: str):
    with open(filename, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["PubmedID", "Title", "PublicationDate", "Non-academic Author(s)", "Company Affiliation(s)", "Corresponding Author Email"])
        writer.writeheader()
        for paper in papers:
            writer.writerow(paper)
    
    print(f"Results saved to {filename}")


# Main function to handle the command-line interface and process user query
def main():
    parser = argparse.ArgumentParser(description="Research Paper Fetcher")
    parser.add_argument("query", help="Query to search in PubMed", type=str)
    parser.add_argument("-d", "--debug", help="Enable debug mode", action="store_true")
    parser.add_argument("-f", "--file", help="Specify output filename", type=str, default="papers.csv")
    
    args = parser.parse_args()
    
    # Fetch paper IDs
    paper_ids = fetch_papers(args.query, args.debug)
    
    papers = []
    
    # Fetch and process each paper's details
    for paper_id in paper_ids:
        paper_details = fetch_paper_details(paper_id, args.debug)
        papers.append(paper_details)
    
    # Save results to CSV
    save_to_csv(papers, args.file)


if __name__ == "__main__":
    main()
