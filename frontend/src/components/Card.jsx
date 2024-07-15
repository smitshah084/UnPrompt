import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const Card = ({ url, altText, title, content, color: hexColor = "" }) => {
  return (
    <div
      className={`card lg:card-side shadow-xl text-white`}
      style={{ backgroundColor: hexColor }}
    >
      <figure className="p-2">
        <img src={url} alt={altText} />
      </figure>
      <div className="card-body">
        <h2 className="card-title">{title}</h2>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
      </div>
    </div>
  );
};
export default Card;
