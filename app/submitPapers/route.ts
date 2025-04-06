import { submitPapers } from '@/services/api/api'
import { NextResponse } from 'next/server'

// If we need a route handler, we can create it here
export async function POST(req: Request) {
  const body = await req.json()
  const papers = body.papers

  console.log('Papers:', papers)

  // We're using required on inputs for now, but server side validation would happen here
  if (!Array.isArray(papers) || papers.length === 0) {
    return NextResponse.json(
      { error: 'Please provide at least one valid paper DOI' },
      { status: 400 }
    )
  }

  try {
    // Submit papers and get recommendations
    const response = await submitPapers(papers)

    return NextResponse.json(response)
  } catch (error) {
    console.error('Error in route handler:', error)

    return NextResponse.json(
      {
        error:
          error instanceof Error ? error.message : 'Failed to process request',
      },
      { status: 500 }
    )
  }
}
