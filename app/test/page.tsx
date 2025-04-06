// Test page -> test the Fast API server with Get request
import { getHelloWorld } from '@/services/api/api'

export default async function TestPage() {
  try {
    // Test API call
    const response = await getHelloWorld()

    const data = response.data
    console.log('Test response: ', data)

    return (
      <div className='p-8 mt-20 max-w-md mx-auto bg-white rounded shadow-md'>
        <h1 className='text-2xl text-black font-bold mb-4'>API Test</h1>

        <div className='bg-gray-100 text-green-500 p-4 rounded'>
          <h2 className='text-lg text-green-600 font-extrabold mb-2'>
            Response from API:
          </h2>
          <p className='text-xl'>{data.Hello}</p>
        </div>
      </div>
    )
  } catch (error) {
    return (
      <div className='p-8 max-w-md mx-auto bg-white rounded shadow-md'>
        <h1 className='text-2xl font-bold mb-4'>API Test Failed</h1>
        <p className='text-red-600'>
          {error instanceof Error ? error.message : 'Failed to connect to API'}
        </p>
      </div>
    )
  }
}
