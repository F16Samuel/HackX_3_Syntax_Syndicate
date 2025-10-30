const WelcomeLeft = () => {
    return (
      <div className="w-2/5 flex flex-col justify-center items-center border-r border-gray-700 p-10 bg-black">
        <div className="text-4xl font-bold mb-4">Welcome to Sample Test</div>
        <div className="space-y-2 text-gray-400 text-sm">
          <p>
            <span className="font-semibold text-white">Test duration:</span> 30 mins
          </p>
          <p>
            <span className="font-semibold text-white">No. of questions:</span> 5 questions
          </p>
        </div>
      </div>
    )
};

export default WelcomeLeft;