from pyzerox import zerox
import os
import json
import asyncio
from dotenv import load_dotenv
import csv

kwargs = {}

## system prompt to use for the vision model
custom_system_prompt = None

# to override
# custom_system_prompt = "For the below PDF page, do something..something..." ## example

###################### Example for OpenAI ######################
model = "gpt-4o-mini" ## openai model
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")  # Load from .env file


import PyPDF2
import os
import kagglehub

# Download latest version
path = kagglehub.dataset_download("lequidon/vi-math-10-grade")

print("Path to dataset files:", path)

# List all files in the dataset directory
files = os.listdir(path)
print("Files in dataset:")
for file in files:
    print(f"- {file}")


def save_to_csv(result, output_file='results.csv'):
    headers = ['filename', 'page_count', 'processed_pages', 'output_path']
    
    # Check if file exists to determine if we need to write headers
    file_exists = os.path.exists(output_file)
    
    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        
        # Concatenate all page contents into a single string
        content = '\n'.join([page.content for page in result.pages])
        row = {
            'file_name': os.path.basename(result['file_name']),
            'processed_pages': len(result['pages']),
            'content' : content,
        }
        writer.writerow(row)


# Define main async entrypoint
async def main():
    results = []
    output_dir = "./output_test"
    csv_path = os.path.join(output_dir, 'processing_results.csv')
    
    for file in files:
        sample_file = os.path.join(path, file)
        file_path = sample_file
        with open(sample_file, 'rb') as f:  # Open in binary mode for PDFs
            pdf_reader = PyPDF2.PdfReader(f)
            # Get text from first page
            if len(pdf_reader.pages) > 0:
                text = pdf_reader.pages[0].extract_text()
                print(f"\nSample content:")
                print(text[:500])  # Print first 500 characters
        select_pages = None ## None for all, but could be int or list(int) page numbers (1 indexed)

        result = await zerox(file_path=file_path, model=model, output_dir=output_dir,
                            custom_system_prompt=custom_system_prompt,select_pages=select_pages, **kwargs)
        print('result:', result)
        # Save each file's results immediately
        save_to_csv(result, csv_path)
        results.append(result)
    
    return results


# run the main function:
result = asyncio.run(main())

# print markdown result
print(result)