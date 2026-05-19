import { fetchLandingData } from '@/lib/landing-data'
import LandingClient from './LandingClient'

export const revalidate = 300

export default async function HomePage() {
  const data = await fetchLandingData()
  return <LandingClient data={data} />
}
