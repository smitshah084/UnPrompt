import React, { useState } from "react";
import { postData } from "../../axios/fetchData";
import sendIcon from "../../assets/sendIcon.svg";
function Home() {
  const [response, setResponse] = useState();
  const [query, setQuery] = useState();

  const handleInputChange = (e) => {
    setQuery(e.target.value);
  };

  const handleSubmit = async () => {
    const result = await postData("/api/endpoint", { query });
    setResponse(result);
  };

  return (
    <section className="bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center p-4">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-4">
        Ask me anything?
      </h1>
      <div className="flex w-full max-w-md">
        <textarea
          value={query}
          onChange={handleInputChange}
          className="flex-grow p-2 border border-gray-300 dark:border-gray-700 rounded-l-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-300 resize-none overflow-y-auto h-10"
        />
        <button
          onClick={handleSubmit}
          className="p-2 bg-blue-500 text-white rounded-r-md hover:bg-blue-600 dark:bg-blue-700 dark:hover:bg-blue-800"
        >
          <img src={sendIcon} alt="Send Icon" />
        </button>
      </div>
      {response && (
        <div className="mt-4 p-4 w-full max-w-md bg-white dark:bg-gray-800 rounded-md shadow overflow-auto">
          <p className="text-gray-900 dark:text-gray-100 break-words">
            {response}
          </p>
        </div>
      )}
    </section>
  );
}

export default Home;
