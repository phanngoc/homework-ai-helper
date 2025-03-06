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
        const jobLinks = await page.$$eval('div.view_job_item a.img_job_card', elements => {
            return elements.map(el => {
            const url = 'https://www.vietnamworks.com' + el.getAttribute('href');
            const title = el.getAttribute('title');
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

        const titleDetail = await page.$eval('h1[name="title"]', el => el.innerText);
        const salary = await page.$eval('div.vnwLayout__container div div div div div div div div > div:nth-child(2) > div:first-child', el => el.innerText);
        const location = await page.$eval('div.vnwLayout__container div div div div div div div div > div:nth-child(3) > div > span', el => el.innerText);
        const descriptionJob = await page.$eval('div.vnwLayout__container div div div div div div div:nth-child(3) > div > div > div > div > div', el => el.innerText);
        // Check if salary or location exists; if not, skip processing
        if (!salary || !location) {
            log.info(`No salary or location found for ${request.loadedUrl}. Skipping...`);
            return;
        }

        // Save results as JSON to ./storage/datasets/default
        await pushData({ title: titleDetail, url: request.loadedUrl, salary: salary, location: location, description: descriptionJob });

        // Extract links from the current page
        // and add them to the crawling queue.
        // await enqueueLinks();
    },
    // Comment this option to scrape the full website.
    // maxRequestsPerCrawl: 20,
    // Uncomment this option to see the browser window.
    // headless: false,
});

// Add first URL to the queue and start the crawl.
for (let i = 1; i <= 500; i++) {
    await crawler.run([`https://www.vietnamworks.com/viec-lam?g=5&w=1&level=5&page=${i}`]);
}
