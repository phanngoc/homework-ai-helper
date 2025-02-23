from pyzerox import zerox
import os
import json
import asyncio
from dotenv import load_dotenv

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


if len(files) > 0:
    sample_file = os.path.join(path, files[0])
    file_path = sample_file
    with open(sample_file, 'rb') as f:  # Open in binary mode for PDFs
        pdf_reader = PyPDF2.PdfReader(f)
        # Get text from first page
        if len(pdf_reader.pages) > 0:
            text = pdf_reader.pages[0].extract_text()
            print(f"\nSample content from {files[0]}:")
            print(text[:500])  # Print first 500 characters



# Define main async entrypoint
async def main():
    ## process only some pages or all
    select_pages = None ## None for all, but could be int or list(int) page numbers (1 indexed)

    output_dir = "./output_test" ## directory to save the consolidated markdown file
    result = await zerox(file_path=file_path, model=model, output_dir=output_dir,
                        custom_system_prompt=custom_system_prompt,select_pages=select_pages, **kwargs)
    
    return result


# run the main function:
result = asyncio.run(main())

# print markdown result
print(result)