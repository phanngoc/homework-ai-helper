// import rehypeKatex from 'rehype-katex'
// import rehypeStringify from 'rehype-stringify'
// import remarkMath from 'remark-math'
// import remarkParse from 'remark-parse'
// import remarkRehype from 'remark-rehype'
// import { unified } from 'unified'
// import vfile from 'to-vfile'

// const file = await unified()
//   .use(remarkParse)
//   .use(remarkMath)
//   .use(remarkRehype)
//   .use(rehypeKatex)
//   .use(rehypeStringify)
//   .process(await vfile.read('example.md'))

// console.log(file)
// console.log(String(file))


import rehypeDocument from 'rehype-document'
import rehypeKatex from 'rehype-katex'
import rehypeParse from 'rehype-parse'
import rehypeStringify from 'rehype-stringify'
import vfile from 'to-vfile'
import {unified} from 'unified'

const file = await unified()
  .use(rehypeParse, {fragment: true})
  .use(rehypeDocument, {
    // Get the latest one from: <https://katex.org/docs/browser>.
    css: 'https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css'
  })
  .use(rehypeKatex)
  .use(rehypeStringify)
  .process(await vfile.read('input.html'))

file.basename = 'output.html'
await vfile.write(file)