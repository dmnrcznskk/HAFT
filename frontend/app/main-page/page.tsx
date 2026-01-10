import Link from 'next/link'
import React from 'react'
import "./main-page.css"

const Page = () => {
  return (
    <div>
      <div className="baner">
        <div className="baner-content">
          <p>
            Chcesz stworzyć własny wzór? <br/>
            <span>Wygeneruj go <span className="highlight">teraz!</span></span>
          </p>
          <Link href="/generator-page" className="button-link">
            Generuj
          </Link>
        </div>
        {/* Tu możesz dodać tag img, jeśli ten kursor/siatka to osobny plik */}
        <div className="baner-image"></div>
      </div>

      <div className="filters-section">
        <div className="filter-label">Nowe</div>
      </div>
    </div>
  )
}

export default Page