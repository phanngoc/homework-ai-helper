import { createPlaywrightRouter } from 'crawlee';
import fs from 'fs';
import https from 'https';

export const router = createPlaywrightRouter();

router.addDefaultHandler(async ({ enqueueLinks, log }) => {
    log.info(`enqueueing new URLs`);
    await enqueueLinks({
        selector: 'h3.entry-title > a',
        label: 'detail', // <= note the different label
    });
});

const downloadPdf = async (pdfLink: string|null, fileName: string) => {
    console.log(`Downloading PDF from ${pdfLink} to ${fileName}`);
    const file = fs.createWriteStream(fileName);
    if (pdfLink) {
        const request = https.get(pdfLink, function(response) {
            response.pipe(file);
         
            // after download completed close filestream
            file.on("finish", () => {
                file.close();
                console.log("Download Completed");
            });
         });
         
    }
};

const getNameFromUrl = (url: string) => {
    const urlParts = url.split('/');
    const fileName = urlParts[urlParts.length - 1];
    const name = fileName.split('.')[0];
    return name;
};

router.addHandler('detail', async ({ request, page, log, pushData }) => {
    const title = await page.title();
    log.info(`${title}`, { url: request.loadedUrl });
    const pdfLink = await page.$eval('.entry-content > center > a', (element) => element.getAttribute('href'));
    log.info(`PDF Link: ${pdfLink}`, { url: request.loadedUrl });

    if (!pdfLink || pdfLink.trim() === '') {
        log.info('No PDF link found', { url: request.loadedUrl });
        return;
    }

    const name = getNameFromUrl(pdfLink);
    log.info(`Name from URL: ${name}`, { url: request.loadedUrl });
    // Save PDF to storage
    await downloadPdf(pdfLink, `./storage/key_value_stores/default/${name}.pdf`);
    if (title && pdfLink) {
        await pushData({
            url: request.loadedUrl,
            title,
            pdfLink,
        });
    }
});
