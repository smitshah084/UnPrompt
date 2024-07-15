import React, { useEffect, useRef, useState } from "react";
import { fetchData, postData } from "../../axios/fetchData";
import Card from "../../components/Card";
import { toast } from "react-toastify";
import randomColor from "randomcolor";

function Home() {
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const observer = useRef();
  const lastCardRef = useRef();

  const loadCards = async () => {
    setLoading(true);
    try {
      // const result = await returnMock(get_cards);
      const result = await fetchData("/content/get_cards");
      if (result)
        setCards((prevCards) => [
          ...prevCards,
          ...result.cards.map((card) => ({
            ...card,
            color: randomColor({
              luminosity: "dark",
            }),
          })),
        ]);
    } catch (error) {
      toast("🦄 Error fetching data");
      setError("Error fetching data");
      console.error("Error fetching data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCards();
  }, []);

  useEffect(() => {
    if (loading) return;
    if (observer.current) observer.current.disconnect();
    observer.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        loadCards();
      }
    });
    if (lastCardRef.current) observer.current.observe(lastCardRef.current);
    return () => {
      if (observer.current) observer.current.disconnect();
    };
  }, [loading]);

  return (
    <section className="bg-gray-50 dark:bg-gray-900 flex flex-col items-center justify-center p-4">
      {cards && (
        <div className="flex flex-col gap-5">
          {cards.map((card, index) => (
            <div
              key={card.title}
              ref={index === cards.length - 1 ? lastCardRef : null}
            >
              <Card
                key={card.title}
                url={card.image_link}
                altText={card.image_caption}
                title={card.title}
                content={card.content}
                color={card.color}
              />
            </div>
          ))}
        </div>
      )}
      {error && (
        <div className="mt-4 p-4 w-full max-w-md bg-red-500 text-white rounded-md shadow overflow-auto">
          <p className="break-words">{error}</p>
        </div>
      )}
      {loading && (
        <div className="mt-4 p-4 w-full max-w-md bg-white dark:bg-gray-800 rounded-md shadow overflow-auto">
          <p className="text-gray-900 dark:text-gray-100 break-words">
            Loading...
          </p>
        </div>
      )}
    </section>
  );
}

export default Home;
