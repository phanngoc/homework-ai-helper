// For more information, see https://crawlee.dev/
import { PlaywrightCrawler } from 'crawlee';

// PlaywrightCrawler crawls the web using a headless
// browser controlled by the Playwright library.
const crawler = new PlaywrightCrawler({
    // Use the requestHandler to process each of the crawled pages.
    async requestHandler({ request, page, enqueueLinks, log, pushData }) {
        const title = await page.title();
        log.info(`Title of ${request.loadedUrl} is '${title}'`);

        // Find all job title elements and extract their URLs
        const jobLinks = await page.$$eval('h3.imt-3[data-controller="utm-tracking"]', elements => {
            return elements.map(el => {
                const url = el.getAttribute('data-url');
                const title = el.textContent.trim();
                return { url, title };
            });
        });
        log.info('jobLinks', jobLinks);
        // Enqueue job detail pages
        for (const job of jobLinks) {
            if (job.url) {
                await crawler.addRequests([job.url]);
                log.info(`Enqueued job: ${job.title} - ${job.url}`);
            }
        }

        // Return early if no job links are found
        if (jobLinks.length > 0) {
            log.info(`This is job listing page: ${request.loadedUrl}`);
            return;
        }

        const content = await page.$eval('.icontainer', el => el.innerText);
        // Check if content exists; if not, skip processing
        if (!content) {
            log.info(`No content found for ${request.loadedUrl}. Skipping...`);
            return;
        }

        // Save results as JSON to ./storage/datasets/default
        await pushData({ title, url: request.loadedUrl, content: content });

        // Extract links from the current page
        // and add them to the crawling queue.
        await enqueueLinks();
    },
    // Comment this option to scrape the full website.
    // maxRequestsPerCrawl: 20,
    // Uncomment this option to see the browser window.
    // headless: false,
});

// Add first URL to the queue and start the crawl.
await crawler.run(['https://itviec.com/it-jobs']);
