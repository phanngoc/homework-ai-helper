import fs from 'fs/promises';
import path from 'path';
import { createObjectCsvWriter } from 'csv-writer';

async function mergeJsonToCsv() {
    try {
        // Path to the datasets directory
        const datasetPath = path.join(process.cwd(), 'storage', 'datasets', 'default');
        
        // Get all JSON files
        const files = await fs.readdir(datasetPath);
        const jsonFiles = files.filter(file => file.endsWith('.json'));
        
        // Array to store all data
        const allData = [];
        
        // Read each JSON file
        for (const file of jsonFiles) {
            const filePath = path.join(datasetPath, file);
            const content = await fs.readFile(filePath, 'utf-8');
            const data = JSON.parse(content);
            allData.push(data);
        }
        
        // Setup CSV writer
        const csvWriter = createObjectCsvWriter({
            path: 'output.csv',
            header: [
                { id: 'title', title: 'TITLE' },
                { id: 'url', title: 'URL' },
                { id: 'content', title: 'CONTENT' }
            ]
        });
        
        // Write to CSV
        await csvWriter.writeRecords(allData);
        console.log(`Successfully merged ${jsonFiles.length} files into output.csv`);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

// Run the function
mergeJsonToCsv();