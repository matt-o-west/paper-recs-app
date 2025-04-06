import Link from 'next/link'
import { Paper } from './PapersForm'

interface ResultCardProps {
  paper: Paper
  index: number
}

export default function ResultCard({ paper, index }: ResultCardProps) {
  const { doi, name, abstract, references, cited_by } = paper

  const formatDoiLink = (doi: string) => {
    const cleanDoi = doi.startsWith('doi:') ? doi.substring(4) : doi
    return `https://doi.org/${cleanDoi}`
  }

  // Basic styling, update as needed
  return (
    <div className='p-6 bg-slate-100 rounded-lg shadow-md mb-4 border border-gray-100 hover:shadow-lg transition-shadow'>
      <div className='flex items-start gap-3'>
        <div className='bg-indigo-200 text-indigo-800 font-bold rounded-full w-8 h-8 flex items-center justify-center flex-shrink-0'>
          {index + 1}
        </div>

        <div className='flex-1'>
          <h2 className='text-xl font-bold text-gray-800 mb-2'>
            {name || doi}
          </h2>
          <a
            href={formatDoiLink(doi)}
            target='_blank'
            rel='noopener noreferrer'
            className='text-indigo-600 text-sm hover:underline mb-3 inline-block'
          >
            {doi}
          </a>
          {abstract && (
            <p className='text-gray-700 text-sm mb-4'>{paper.abstract}</p>
          )}
          <div className='flex flex-wrap gap-2 mb-4'>
            {cited_by && cited_by.length > 0 && (
              <span className='bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full'>
                Cited by: {paper.cited_by.length}
              </span>
            )}
            {references && references.length > 0 && (
              <span className='bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full'>
                References: {references.length}
              </span>
            )}
          </div>

          {/* References list (collapsible) */}
          {references && references.length > 0 && (
            <details className='mb-2'>
              <summary className='cursor-pointer text-sm font-medium text-indigo-600 hover:text-indigo-800'>
                View references
              </summary>
              <ul className='mt-2 pl-5 text-xs text-gray-600 list-disc'>
                {references.map((ref, i) => (
                  <li key={i}>
                    <a
                      href={formatDoiLink(ref)}
                      target='_blank'
                      rel='noopener noreferrer'
                      className='hover:underline'
                    >
                      {ref}
                    </a>
                  </li>
                ))}
              </ul>
            </details>
          )}
          {/* Citing papers list (collapsible) */}
          {cited_by && cited_by.length > 0 && (
            <details>
              <summary className='cursor-pointer text-sm font-medium text-indigo-600 hover:text-indigo-800'>
                View citing papers
              </summary>
              <ul className='mt-2 pl-5 text-xs text-gray-600 list-disc'>
                {cited_by.map((cite, i) => (
                  <li key={i}>
                    <a
                      href={formatDoiLink(cite)}
                      target='_blank'
                      rel='noopener noreferrer'
                      className='hover:underline'
                    >
                      {cite}
                    </a>
                  </li>
                ))}
              </ul>
            </details>
          )}

          <div className='mt-4'>
            <Link
              href={formatDoiLink(paper.doi)}
              target='_blank'
              rel='noopener noreferrer'
              className='inline-block bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded text-sm transition-colors'
            >
              View Paper
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
