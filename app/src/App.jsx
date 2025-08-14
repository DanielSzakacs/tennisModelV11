import { useState } from 'react'

export default function App() {
  const [a, setA] = useState('')
  const [b, setB] = useState('')
  const [prob, setProb] = useState(null)

  const predict = async () => {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player_a: a, player_b: b })
    })
    const data = await res.json()
    setProb(data.probability)
  }

  return (
    <div className="p-4">
      <input className="border" value={a} onChange={e=>setA(e.target.value)} placeholder="Player A" />
      <input className="border ml-2" value={b} onChange={e=>setB(e.target.value)} placeholder="Player B" />
      <button className="ml-2 bg-blue-500 text-white px-2" onClick={predict}>Predict</button>
      {prob !== null && <div className="mt-2">Win probability: {(prob*100).toFixed(1)}%</div>}
    </div>
  )
}
