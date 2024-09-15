// For more information, see https://crawlee.dev/
import { PlaywrightCrawler, ProxyConfiguration, Dataset } from 'crawlee';

import { router } from './routes.js';

// create start URLs run from page 1 to 50
const startUrls = Array.from({ length: 50 }, (_, i) => `https://thcs.toanmath.com/de-thi-tuyen-sinh-lop-10-mon-toan/page/${i + 1}`);
console.log('sstartUrls', startUrls);
const crawler = new PlaywrightCrawler({
    // proxyConfiguration: new ProxyConfiguration({ proxyUrls: ['...'] }),
    requestHandler: router,
    // Comment this option to scrape the full website.
    // maxRequestsPerCrawl: 5,
});

await crawler.run(startUrls);

// Add this line to export to CSV.
// await Dataset.exportToCSV('results');