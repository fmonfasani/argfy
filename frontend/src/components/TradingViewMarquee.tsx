export default function TradingViewMarquee() {
  return (
    <div className="bg-white border-b py-4">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-center items-center space-x-8 text-sm">
          <div className="flex items-center space-x-2">
            <span className="text-gray-500">S&P 500:</span>
            <span className="font-semibold text-green-600">4,697.8 ↑</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-500">EUR/USD:</span>
            <span className="font-semibold text-blue-600">1.0876</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-500">Bitcoin:</span>
            <span className="font-semibold text-orange-600">$42,350 ↑</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-500">GGAL:</span>
            <span className="font-semibold text-green-600">$2,847 ↑</span>
          </div>
        </div>
      </div>
    </div>
  )
}