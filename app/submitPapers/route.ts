import { submitPapers } from '@/services/api/api'
import { NextResponse } from 'next/server'

// If we need a route handler, we can create it here
export async function POST(req: Request, res: Response) {
  const body = await req.json()
  const papers = body.papers
  console.log('Papers:', papers)

  if (!Array.isArray(papers) || papers.length === 0) {
    return NextResponse.json(
      { error: 'Please provide at least one valid paper DOI' },
      { status: 400 }
    )
  }

  // Format DOIs if needed
  const formattedPapers = papers.map((paper) => {
    if (
      /^10\.\d{4,9}\/[-._;()/:A-Z0-9]+$/i.test(paper) &&
      !paper.startsWith('doi:')
    ) {
      return `doi:${paper}`
    }
    return paper
  })

  // Send the papers to the FastAPI server
  const response = await submitPapers(formattedPapers)
  if (response.status !== 200) {
    return NextResponse.json(
      { error: 'Failed to submit papers' },
      { status: response.status }
    )
  }

  return NextResponse.json(papers)
}
